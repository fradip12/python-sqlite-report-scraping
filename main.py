import sqlite3
import os
import keys

def connect_to_db(db_path, password):
    """
    Connect to an SQLite database with password
    
    Args:
        db_path (str): Path to the SQLite database file
        password (str): Password for the database
        
    Returns:
        sqlite3.Connection: Database connection object or None if failed
    """
    try:
        # Check if database file exists
        if not os.path.exists(db_path):
            print(f"Database file not found at: {db_path}")
            return None
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        
        # Set the password using PRAGMA key
        conn.execute(f"PRAGMA key = '{password}'")
        
        # Test the connection by trying a simple query
        try:
            conn.execute("SELECT 1 FROM sqlite_master LIMIT 1")
            print(f"Successfully connected to database at {db_path}")
            return conn
        except sqlite3.DatabaseError as e:
            print(f"Authentication failed: {e}")
            conn.close()
            return None
            
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def update_event(conn, event_uid, value_to_update, data_element):
    try:
        cursor = conn.cursor()
        # Execute the update query
        update_query = f"""
            UPDATE "TrackedEntityDataValueFlow" 
            SET "value" = '{value_to_update}'
            WHERE "event" = '{event_uid}' 
            AND "dataElement" = '{data_element}'
        """
        cursor.execute(update_query)
        conn.commit()
        
        # Check if any row was affected
        if cursor.rowcount > 0:
            print(f"Successfully updated event {event_uid} with de : {data_element} with value {value_to_update}")
            return True
        else:
            print(f"No event found with uid {event_uid}")
            return False
            
    except sqlite3.Error as e:
        print(f"Error updating event {event_uid}: {e}")
        conn.rollback()
        return False
            
def get_report(conn, event_uids, data_elements):
    try:
        cursor = conn.cursor()
        
        # Convert lists to comma-separated strings for SQL IN clause
        events_str = "', '".join(event_uids)
        data_elements_str = "', '".join(data_elements)
        
        # Execute the query to get the report
        report_query = f"""
            SELECT * FROM "TrackedEntityDataValueFlow"
            WHERE "event" IN ('{events_str}')
            AND "dataElement" IN ('{data_elements_str}')
        """
        cursor.execute(report_query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error executing report query: {e}")
        conn.rollback()
        return None


def main():
    # Define your database path and password
    db_path = "/Users/fradiptaalqaiyum/Documents/restore-db-gps-polygon/martin.joseph-20250409130119/dhis.db"
    password = keys.get_db_password()
    # Store list of changed event
    list_of_changed_event = []
    # Store list of changed data element target
    list_of_changed_de_target = []
    # Store filename
    filename = db_path.split('/')[5]
    
    

    # Find Events to restore
    eventsToRestore = """
                            SELECT 
                                MAX(id) AS id, 
                                eventUid, 
                                description, 
                                CASE
                                    WHEN description LIKE '%DE target:%' THEN
                                        TRIM(SUBSTR(
                                            SUBSTR(description, INSTR(description, 'DE target:') + 10),
                                            1,
                                            CASE 
                                                WHEN INSTR(SUBSTR(description, INSTR(description, 'DE target:') + 10), ',') > 0 
                                                THEN INSTR(SUBSTR(description, INSTR(description, 'DE target:') + 10), ',') - 1
                                                ELSE LENGTH(SUBSTR(description, INSTR(description, 'DE target:') + 10))
                                            END
                                        ))
                                    ELSE ''
                                END AS dataElement,
                                CASE 
                                    WHEN description LIKE '%POINT%' THEN 'POINT'
                                    WHEN description LIKE '%POLYGON%' THEN 'POLYGON'
                                    ELSE 'UNKNOWN'
                                END AS type,
                                CASE 
                                            WHEN description LIKE '%POINT%' THEN (
                                                SELECT 
                                                    substr(description,  
                                                        instr(description, 'POINT('), 
                                                        instr(substr(description, instr(description, 'POINT('), length(description)), ')') 
                                                    )
                                            )
                                            WHEN description LIKE '%POLYGON%' THEN (
                                                SELECT 
                                                    substr(description, 
                                                        instr(description, 'POLYGON('), 
                                                        instr(substr(description, instr(description, 'POLYGON('), length(description)), ')') 
                                                    )
                                            )
                                            ELSE 'UNKNOWN'
                                        END as valueToUpdate
                                FROM "StateDetailFlow" 
                                WHERE description LIKE '%Status updated to INCOMPLETE by indicator%' 
                                AND (description LIKE '%POINT%' OR description LIKE '%POLYGON%')
                                GROUP BY eventUid, type
                            """
    
    # Connect to the database
    conn = connect_to_db(db_path, password)
    
    if conn:
        try:
            # Example: Execute a query to show tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Database tables:")
            for table in tables:
                print(f"- {table[0]}")
            
            # Keep connection open and wait for user actions
            while True:
                print("\nOptions:")
                print("1: Query a table")
                print("2: Execute Restore Data")
                print("3: Export Changes as CSV")
                print("4: Exit")
                
                choice = input("Enter your choice: ")
                
                if choice == "1":
                    table_name = input("Enter table name: ")
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
                        rows = cursor.fetchall()
                        if rows:
                            for row in rows:
                                print(row)
                        else:
                            print("No data found")
                    except sqlite3.Error as e:
                        print(f"Error querying table: {e}")
                
                elif choice == "2":
                    try:
                        cursor.execute(eventsToRestore)
                        rows = cursor.fetchall()
                        eventUid = ''
                        valueToUpdate = ''
                        valueType = ''
                        dataElement = ''
                        if rows:
                            # Get column names from cursor description
                            column_names = [description[0] for description in cursor.description]
                            print("\nColumns:", column_names)
                            
                            # Display results
                            print("\nResults:")
                            for row in rows:
                                # Print each value with its column name
                                for i, value in enumerate(row):
                                    if(column_names[i] == "eventUid"):
                                        eventUid = value
                                        list_of_changed_event.append(eventUid)
                                    elif (column_names[i] == "valueToUpdate"):
                                        valueToUpdate = value
                                    elif (column_names[i] == "type"):
                                        valueType = value
                                    elif (column_names[i] == "dataElement"):
                                        dataElement = value
                                        list_of_changed_de_target.append(dataElement)
                                print('-' * 50)
                                # Execute the update query for every event
                                try:
                                    if valueType != 'UNKNOWN':
                                        update_event(conn, eventUid, valueToUpdate, dataElement)
                                        conn.commit()
                                    else:
                                        print(f"Skipping update for {eventUid} - invalid geometry value")
                                except sqlite3.Error as e:
                                    print(f"Error updating event {eventUid}: {e}")
                                    conn.rollback()
                            print(f"\nTotal rows returned: {len(rows)}")
                        else:
                            print("Query executed successfully, but no data returned")
                    except sqlite3.Error as e:
                        print(f"Error executing query: {e}")
                elif choice == "3":
                    #Get Username for filename from query
                    cursor.execute("SELECT username FROM ktv_user_profile")
                    rows = cursor.fetchall()
                    # Export changes to CSV
                    report = get_report(conn, list_of_changed_event, list_of_changed_de_target)
                    if report:
                        # Write the report to CSV with headers
                        with open(f"{filename}_restore_missing_gps_polygon.csv", "w") as f:
                            # Write CSV header
                            f.write("id,event,dataElement,storedBy,value\n")
                            
                            # Write data rows
                            for row in report:
                                # For the value column (row[4]), make it a single string
                                # and handle any commas within the values
                                values = []
                                for i, item in enumerate(row):
                                    if i == 4:  # The value column
                                        values.append(f'"{str(item)}"')
                                    else:
                                        values.append(str(item))
                                
                                f.write(",".join(values) + "\n")
                                
                        print("Report exported to report.csv")
                    else:
                        print("No data to export")
                    break
                elif choice == "4":
                    print("Exiting...")
                    break
                
                else:
                    print("Invalid choice")
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the connection when done
            conn.close()
            print("Database connection closed")
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()