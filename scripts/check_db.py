import sqlite3
from datetime import datetime
import os

def check_users():
    """Check users table in API Gateway database"""
    api_gateway_db = os.path.join(os.path.dirname(__file__), '..', 'api_gateway.db')
    print("\n=== Checking API Gateway Database ===")
    
    if not os.path.exists(api_gateway_db):
        print(f"API Gateway database not found at {api_gateway_db}")
        return
        
    print(f"Found API Gateway database at: {os.path.abspath(api_gateway_db)}")
    conn = sqlite3.connect(api_gateway_db)
    cursor = conn.cursor()
    
    try:
        print("\n=== Users ===")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        print(f"\nFound {len(users)} users:")
        for user in users:
            print("\nUser:")
            for col, val in zip(columns, user):
                print(f"{col}: {val}")
    except sqlite3.OperationalError as e:
        print(f"Error accessing users table: {e}")
    finally:
        conn.close()

def check_tasks():
    """Check tasks table in Task Service database"""
    task_service_db = os.path.join(os.path.dirname(__file__), '..', 'task_service.db')
    print("\n=== Checking Task Service Database ===")
    
    if not os.path.exists(task_service_db):
        print(f"Task Service database not found at {task_service_db}")
        return
        
    print(f"Found Task Service database at: {os.path.abspath(task_service_db)}")
    conn = sqlite3.connect(task_service_db)
    cursor = conn.cursor()

    # List all tables first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\nAvailable tables:", [table[0] for table in tables])
    
    try:
        print("\n=== Tasks ===")
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        print(f"\nFound {len(tasks)} tasks:")
        for task in tasks:
            print("\nTask:")
            for col, val in zip(columns, task):
                print(f"{col}: {val}")
    except sqlite3.OperationalError as e:
        print(f"Error accessing tasks table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()  # Check users table
    check_tasks()  # Check tasks table
