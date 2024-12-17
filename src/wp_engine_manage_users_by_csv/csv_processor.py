import pandas as pd
from typing import List, Dict, Optional
from .logger import log_error

REQUIRED_COLUMNS = [
    'action',
    'account_name',
    'first_name',
    'last_name',
    'email',
    'roles',
    'install_names'
]

VALID_ACTIONS = ['add', 'remove']

def validate_csv_structure(df: pd.DataFrame) -> bool:
    """
    Validate that the CSV has the required columns.
    If headers are missing, check if the first row contains the required data.
    """
    # Check if headers match required columns
    if all(col in df.columns for col in REQUIRED_COLUMNS):
        return True
        
    # If headers don't match, check if first row might be headers
    if len(df.columns) >= len(REQUIRED_COLUMNS):
        # Rename columns to generic names
        df.columns = [f'col_{i}' for i in range(len(df.columns))]
        
        # Check if first row contains valid data
        first_row = df.iloc[0]
        has_email = any('@' in str(val) for val in first_row)
        if has_email:
            # First row is data, use default column names
            df.columns = REQUIRED_COLUMNS[:len(df.columns)]
            return True
            
    return False

def process_csv_file(file_path: str) -> Optional[List[Dict]]:
    """
    Process the CSV file and return a list of user data dictionaries.
    Returns None if the file is invalid.
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Validate structure
        if not validate_csv_structure(df):
            log_error(f"Invalid CSV structure. Required columns: {', '.join(REQUIRED_COLUMNS)}")
            return None
            
        # Process each row
        users_data = []
        for _, row in df.iterrows():
            # Validate action
            action = str(row['action']).strip().lower()
            if action not in VALID_ACTIONS:
                log_error(f"Invalid action '{action}' for user {row['email']}. Must be 'add' or 'remove'")
                continue
                
            user_data = {
                'action': action,
                'account_name': str(row['account_name']).strip(),
                'first_name': str(row['first_name']).strip(),
                'last_name': str(row['last_name']).strip(),
                'email': str(row['email']).strip(),
                'roles': [role.strip() for role in str(row['roles']).split(',')],
                'install_names': [name.strip() for name in str(row['install_names']).split(',')]
            }
            
            # Validate email format
            if '@' not in user_data['email']:
                log_error(f"Invalid email format for user: {user_data['email']}")
                continue
                
            users_data.append(user_data)
            
        return users_data if users_data else None
        
    except Exception as e:
        log_error(f"Error processing CSV file: {str(e)}")
        return None
