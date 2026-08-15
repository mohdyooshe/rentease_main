import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('DB_HOST', 'localhost')
user = os.environ.get('DB_USER', 'root')
password = os.environ.get('DB_PASSWORD', '')

print(f"Connecting to MySQL at {host} as {user}...")

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        with open('schema.sql', 'r') as f:
            sql_file = f.read()
            # Split commands by semicolon (this is a simple parser, schema.sql has simple commands)
            sql_commands = sql_file.split(';')
            for command in sql_commands:
                if command.strip():
                    print(f"Executing: {command.strip()[:50]}...")
                    cursor.execute(command)
    connection.commit()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Error initializing database: {e}")
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
