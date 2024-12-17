from typing import Dict, List, Optional, Tuple
from wp_engine_api import WPEngineAPI
from wp_engine_api.models import Account, Installation, AccountUser
from .logger import log_error, log_action

def verify_api_access(client: WPEngineAPI) -> bool:
    """
    Verify API access by attempting to get current user.
    """
    try:
        client.users.get_current()
        return True
    except Exception as e:
        log_error(f"API authentication failed: {str(e)}")
        return False

def resolve_accounts_and_installs(client: WPEngineAPI, users_data: List[Dict]) -> Dict:
    """
    Resolve account names and install names to their respective IDs.
    Returns dict with resolved data and any errors.
    """
    result = {
        'users': [],
        'errors': []
    }
    
    # Get all accounts
    try:
        accounts = {account.name: account.id for account in client.accounts.list()}
    except Exception as e:
        log_error(f"Failed to fetch accounts: {str(e)}")
        result['errors'].append("Failed to fetch accounts")
        return result
        
    # Get all installs
    try:
        installs = {install.name: install.id for install in client.installs.list()}
    except Exception as e:
        log_error(f"Failed to fetch installs: {str(e)}")
        result['errors'].append("Failed to fetch installs")
        return result
        
    # Track unresolved names
    unresolved_accounts = set()
    unresolved_installs = set()
    
    # Process each user
    for user in users_data:
        account_id = accounts.get(user['account_name'])
        if not account_id:
            unresolved_accounts.add(user['account_name'])
            continue
            
        # For remove action, we don't need to validate install IDs
        if user['action'] == 'remove':
            result['users'].append({
                **user,
                'account_id': account_id,
                'install_ids': []
            })
            continue
            
        # Resolve install IDs for add action
        install_ids = []
        for install_name in user['install_names']:
            if install_name:  # Skip empty names
                install_id = installs.get(install_name)
                if install_id:
                    install_ids.append(install_id)
                else:
                    unresolved_installs.add(install_name)
        
        if not unresolved_installs:
            result['users'].append({
                **user,
                'account_id': account_id,
                'install_ids': install_ids
            })
            
    # Add any resolution errors
    if unresolved_accounts:
        result['errors'].append(
            f"Cannot find account names: {', '.join(unresolved_accounts)}"
        )
    if unresolved_installs:
        result['errors'].append(
            f"Cannot find install names: {', '.join(unresolved_installs)}"
        )
        
    return result

def get_existing_users(client: WPEngineAPI, account_id: str) -> Dict[str, AccountUser]:
    """
    Get existing users for an account.
    Returns dict mapping email to AccountUser.
    """
    try:
        users = client.accounts.list_users(account_id)
        return {user.email: user for user in users}
    except Exception as e:
        log_error(f"Failed to fetch users for account {account_id}: {str(e)}")
        return {}

def process_users(client: WPEngineAPI, users: List[Dict], dryrun: bool) -> bool:
    """
    Process user changes. Returns True if successful, False if errors occurred.
    """
    success = True
    
    for user in users:
        try:
            existing_users = get_existing_users(client, user['account_id'])
            
            if user['action'] == 'remove':
                # Handle user removal
                if user['email'] in existing_users:
                    existing_user = existing_users[user['email']]
                    if not dryrun:
                        client.account_user_api.delete_account_user(
                            user['account_id'],
                            existing_user.id
                        )
                    log_action(
                        user['email'],
                        user['account_name'],
                        'removed'
                    )
                else:
                    log_error(f"User {user['email']} not found in account {user['account_name']}")
                    
            else:  # action == 'add'
                if user['email'] in existing_users:
                    # Update existing user
                    existing_user = existing_users[user['email']]
                    if not dryrun:
                        # Update user details
                        client.account_user_api.update_account_user(
                            user['account_id'],
                            existing_user.id,
                            {
                                'first_name': user['first_name'],
                                'last_name': user['last_name'],
                                'roles': user['roles'],
                                'installs': user['install_ids']
                            }
                        )
                    log_action(
                        user['email'],
                        user['account_name'],
                        'updated'
                    )
                else:
                    # Create new user
                    if not dryrun:
                        client.account_user_api.create_account_user(
                            user['account_id'],
                            {
                                'user': {
                                    'first_name': user['first_name'],
                                    'last_name': user['last_name'],
                                    'email': user['email']
                                },
                                'roles': user['roles'],
                                'installs': user['install_ids']
                            }
                        )
                    log_action(
                        user['email'],
                        user['account_name'],
                        'added'
                    )
                
        except Exception as e:
            log_error(f"Error processing user {user['email']}: {str(e)}")
            success = False
            
    return success
