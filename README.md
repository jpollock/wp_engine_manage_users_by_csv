# WP Engine User Management by CSV

A command-line tool for managing WP Engine users using CSV files. This tool allows you to add, update, and remove users across multiple WP Engine accounts and installations.

## Installation

```bash
pip install wp-engine-manage-users-by-csv
```

## Requirements

- Python 3.7 or higher
- WP Engine API credentials

## Configuration

The tool requires WP Engine API credentials which can be provided in two ways:

1. Command line arguments:
   ```bash
   wp-engine-manage-users-by-csv users.csv --api-username=YOUR_USERNAME --api-password=YOUR_PASSWORD
   ```

2. Environment variables:
   Create a `.env` file with:
   ```
   WPENGINE_USERNAME=YOUR_USERNAME
   WPENGINE_PASSWORD=YOUR_PASSWORD
   ```

## CSV Format

The CSV file should contain the following columns:
- action: The action to perform ('add' or 'remove')
- account_name: WP Engine account name
- first_name: User's first name
- last_name: User's last name
- email: User's email address
- roles: Comma-separated list of roles
- install_names: Comma-separated list of installation names

Example CSV:
```csv
action,account_name,first_name,last_name,email,roles,install_names
add,myaccount,John,Doe,john@example.com,admin,"install1,install2"
add,myaccount,Jane,Smith,jane@example.com,"admin,collaborator","install1,install3"
remove,myaccount,Bob,Johnson,bob@example.com,collaborator,install4
```

Notes:
- The header row is optional. If not present, the columns must be in the order shown above.
- For 'remove' actions, the roles and install_names are not required but must be present in the CSV.
- When adding a user that already exists, their details will be updated.

## Usage

Basic usage:
```bash
# Dry run with example.csv (default)
wp-engine-manage-users-by-csv example.csv

# Execute changes with credentials
wp-engine-manage-users-by-csv example.csv --api-username=user --api-password=pass --dryrun=false

# Skip confirmation
wp-engine-manage-users-by-csv example.csv --ask-for-confirmation=false
```

Options:
- `--api-username`: WP Engine API username (optional if using .env)
- `--api-password`: WP Engine API password (optional if using .env)
- `--ask-for-confirmation`: Ask for confirmation before making changes (default: true)
- `--dryrun`: Perform a dry run without making actual changes (default: true)

## Logging

The tool creates two types of log files in the 'logs' directory:

1. Action logs: Record all user changes
   - Format: `actions_[timestamp].log` or `actions_[timestamp]_dryrun.log`
   - Contains: user, account, action (added/updated/removed), datetime

2. Error logs: Record any errors that occur
   - Format: `errors_[timestamp].log`
   - Contains: Detailed error messages with timestamps

## Error Handling

The tool will exit with an error message in the following cases:
- Missing API credentials
- Authentication failure
- Invalid CSV format
- Invalid action values (must be 'add' or 'remove')
- Unresolved account names or installation names
- User not found when attempting removal

## Development

To set up the development environment:

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```

## License

MIT License
