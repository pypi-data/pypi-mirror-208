import os
import pymssql

API_IRRIS_URI = str(os.environ.get('API_IRRIS_URI'))
API_IRRIS_USER = str(os.environ.get('API_IRRIS_USER'))
API_IRRIS_PASSWORD = str(os.environ.get('API_IRRIS_PASSWORD'))
API_IRRIS_SOURCE = str(os.environ.get('API_IRRIS_SOURCE'))

API_IRRIS_ROUTE_AUTH = str(os.environ.get('API_IRRIS_ROUTE_AUTH'))
API_IRRIS_ROUTE_MALFACON = str(os.environ.get('API_IRRIS_ROUTE_MALFACON'))

RABBITMQ_USERNAME = str(os.environ.get('RABBITMQ_USERNAME'))
RABBITMQ_PASSWORD = str(os.environ.get('RABBITMQ_PASSWORD'))
RABBITMQ_DNS = str(os.environ.get('RABBITMQ_DNS'))

DB_HOST = str(os.environ.get('DB_HOST'))
DB_NAME = str(os.environ.get('DB_NAME'))
DB_USER = str(os.environ.get('DB_USER'))
DB_PASSWORD = str(os.environ.get('DB_PASSWORD'))

APP_IDENTITY_NAME  = str(os.environ.get('APP_IDENTITY_NAME'))

RESULT_FOLDER = "C:/Users/LucienM/source/InfradeepBackV2/csv"

def createConnection():
    """Create a connection to the database"""
    return pymssql.connect(
        server=DB_HOST, 
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
        )