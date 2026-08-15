import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Add it to your .env file (local) or your hosting provider's environment variables (production)."
    )


class Config:
    SECRET_KEY = SECRET_KEY
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60) # 1 hour session timeout for security
    
    # Database Credentials
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DB = os.environ.get('DB_NAME', 'rentease')
    MYSQL_USE_SSL = os.environ.get('DB_USE_SSL', 'False') == 'True'
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max upload size
    
    # Debugging features
    MYSQL_QUERY_LOG = os.environ.get('MYSQL_QUERY_LOG', 'False') == 'True'
