import os
import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

host = os.environ.get('DB_HOST', 'localhost')
user = os.environ.get('DB_USER', 'root')
password = os.environ.get('DB_PASSWORD', '')

connection = pymysql.connect(
    host=host, user=user, password=password, database='rentease', charset='utf8mb4'
)

with connection.cursor() as cursor:
    try:
        cursor.execute("""
        ALTER TABLE items 
        ADD COLUMN product_price DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER price_per_day;
        """)
        print("Added product_price to items.")
    except Exception as e:
        print("items error:", e)

    try:
        cursor.execute("""
        ALTER TABLE rental_requests
        ADD COLUMN security_deposit DECIMAL(10,2) DEFAULT 0 AFTER total_amount,
        ADD COLUMN rent_amount DECIMAL(10,2) DEFAULT 0 AFTER security_deposit,
        ADD COLUMN grand_total DECIMAL(10,2) DEFAULT 0 AFTER rent_amount,
        ADD COLUMN deposit_status ENUM('held','refunded','partially_deducted','fully_deducted') DEFAULT 'held' AFTER grand_total,
        ADD COLUMN deposit_deduction DECIMAL(10,2) DEFAULT 0 AFTER deposit_status,
        ADD COLUMN deposit_refund DECIMAL(10,2) DEFAULT 0 AFTER deposit_deduction,
        ADD COLUMN deduction_reason TEXT AFTER deposit_refund;
        """)
        print("Added deposit columns to rental_requests.")
    except Exception as e:
        print("rental_requests error:", e)

    try:
        cursor.execute("ALTER TABLE users MODIFY COLUMN user_type ENUM('owner', 'renter', 'admin');")
        print("Re-added admin to user_type enum.")
    except Exception as e:
        print("user_type error:", e)

    try:
        # Create default admin
        email = 'admin@rentease.com'
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            hashed_pw = generate_password_hash('Admin@123')
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)",
                ('System Admin', email, hashed_pw, 'admin')
            )
            print("Created default admin user.")
    except Exception as e:
        print("admin creation error:", e)

connection.commit()
connection.close()
print("Migration complete.")
