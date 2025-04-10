# DB GPS/Polygon Restoration Tool

This tool is designed to restore GPS points and polygon data in SQLCipher-protected SQLite databases, specifically for fixing data in DHIS2-related mobile databases where geographical coordinates were lost.

## Overview

The script connects to an encrypted SQLite database, identifies events where GPS coordinates or polygons were changed to an incomplete status, and restores the original coordinate data.

## Features

- Connect to password-protected SQLite databases
- Identify events with missing/corrupted GPS or polygon data
- Restore original geographical coordinates 
- Create detailed reports of all changes made
- Export changes to CSV for documentation

## Requirements

- Python 3.x
- SQLite3 module with SQLCipher support
- A valid database password (stored in a separate keys.py file)

## How to Use

1. Ensure your database path and password are properly configured
2. Run the script and select from the available options:
    - Option 1: Query a table
    - Option 2: Execute data restoration
    - Option 3: Export changes as CSV report
    - Option 4: Exit

## Functions

- `connect_to_db()`: Establishes a secure connection to the database
- `update_event()`: Updates the GPS/polygon value for a specific event
- `get_report()`: Generates a report of all changes
- `main()`: Controls the program flow and user interaction

## Example

```python
# Update your database path in the main() function
db_path = "/path/to/your/dhis.db"
```

## Security Notes

- Database passwords are stored in a separate keys.py file (not included in this repository)
- The script validates the database connection before any operations

## Generated Reports

The tool will create a CSV file named with the pattern `{username}_restore_missing_gps_polygon.csv` that contains all the changes made to the database.