import pymysql
from werkzeug.security import generate_password_hash

def init_db():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Connecting to MySQL to create database if it doesn't exist...")
    # Connect without specifying a DB to create the DB first
    connection = pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS rentease")
            print("Database 'rentease' created or already exists.")
    finally:
        connection.close()

if __name__ == '__main__':
    init_db()
    
    from app import app
    from models.db import db, User, Item, Request
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
        
        # Optionally add a mock user if none exists
        if not User.query.first():
            mock_user = User(
                username='demo_user', 
                email='demo@rentease.com', 
                password_hash=generate_password_hash('password123')
            )
            db.session.add(mock_user)
            db.session.commit()
            print("Added mock user: demo_user / password123")
            
            mock_item = Item(
                owner_id=mock_user.id,
                title='Sony A7III Camera',
                description='Great condition mirrorless camera. Comes with a 50mm lens.',
                daily_rate=45.00,
                is_available=True
            )
            db.session.add(mock_item)
            db.session.commit()
            print("Added mock item.")
