import pymysql
from flask import current_app

class LoggingCursor(pymysql.cursors.DictCursor):
    """Custom cursor that logs queries to the console if configured."""
    def execute(self, query, args=None):
        if current_app.config.get('MYSQL_QUERY_LOG'):
            print(f"[SQL LOG] Query: {query}")
            if args:
                print(f"[SQL LOG] Args: {args}")
        return super().execute(query, args)

def get_db_connection():
    """
    Returns a PyMySQL database connection using credentials from the Flask app config.
    Uses the LoggingCursor to print queries.
    """
    ssl_args = {'ssl': {'ssl_mode': 'REQUIRED'}} if current_app.config['MYSQL_USE_SSL'] else {}

    connection = pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=LoggingCursor,
        **ssl_args
    )
    return connection
