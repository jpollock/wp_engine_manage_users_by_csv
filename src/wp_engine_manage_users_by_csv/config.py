import os

def validate_api_credentials(api_username=None, api_password=None):
    """
    Validate API credentials from either CLI arguments or environment variables.
    Returns dict with username and password if valid, None otherwise.
    """
    username = api_username or os.getenv('WPENGINE_USERNAME')
    password = api_password or os.getenv('WPENGINE_PASSWORD')
    
    if not username or not password:
        return None
        
    return {
        'username': username,
        'password': password
    }
