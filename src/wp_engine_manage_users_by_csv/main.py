#!/usr/bin/env python3

import os
import sys
import click
from datetime import datetime
from dotenv import load_dotenv
from wp_engine_api import WPEngineAPI
from .config import validate_api_credentials
from .csv_processor import process_csv_file
from .logger import setup_logging, log_action
from .api_client import verify_api_access, resolve_accounts_and_installs, process_users

@click.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--api-username', help='WP Engine API username')
@click.option('--api-password', help='WP Engine API password')
@click.option('--ask-for-confirmation', type=bool, default=True, help='Ask for confirmation before making changes')
@click.option('--dryrun', type=bool, default=True, help='Perform a dry run without making actual changes')
def main(csv_file, api_username, api_password, ask_for_confirmation, dryrun):
    """Manage WP Engine users using a CSV file."""
    try:
        # Setup logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = setup_logging(timestamp, dryrun)
        
        # Load environment variables
        load_dotenv()
        
        # Validate API credentials
        credentials = validate_api_credentials(api_username, api_password)
        if not credentials:
            sys.exit("Error: Missing API credentials")
            
        # Initialize API client
        client = WPEngineAPI(credentials['username'], credentials['password'])
        
        # Verify API access
        if not verify_api_access(client):
            sys.exit("Error: User can't be authenticated")
            
        # Process CSV file and resolve accounts/installs
        users_data = process_csv_file(csv_file)
        if not users_data:
            sys.exit("Error: Invalid or empty CSV file")
            
        # Resolve account names and install names
        resolved_data = resolve_accounts_and_installs(client, users_data)
        if resolved_data.get('errors'):
            for error in resolved_data['errors']:
                click.echo(f"Error: {error}")
            sys.exit(1)
            
        # Show summary if confirmation is required
        if ask_for_confirmation:
            click.echo(f"\nWill process {len(users_data)} users")
            click.echo(f"Dry run: {dryrun}")
            if not click.confirm("Do you want to proceed?"):
                sys.exit("Operation cancelled by user")
        
        # Process users
        success = process_users(client, resolved_data['users'], dryrun)
        
        if success:
            click.echo("Operation completed successfully")
        else:
            click.echo("Operation completed with errors. Please check the error log file")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
