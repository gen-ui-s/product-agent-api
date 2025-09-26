import os
from pymongo import MongoClient
from dotenv import load_dotenv

from exceptions import DatabaseConnectionError
from logs import logger

load_dotenv()

DATABASE_URI = os.environ.get("DATABASE_URI")
DB_NAME = os.environ.get("DB_NAME", "genuis-db")
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
CERTIFICATE_PATH = "/var/task/global-bundle.pem"

client = None

def attempt_connection():
    try:
        connection_uri = DATABASE_URI.format(username=DB_USERNAME,password=DB_PASSWORD)
        logger.info(f"Attempting to connect to {DB_NAME}")

        new_client = MongoClient(
            connection_uri,
            # tls=True,
            # tlsCAFile=CERTIFICATE_PATH,
            serverSelectionTimeoutMS=5000 
        )
        new_client.admin.command('ping')
        logger.info("Connection Succesful")
        return new_client
    except Exception as e:
        logger.info(f"Database Connection failed: {e}")
        return None

client = attempt_connection()

def get_db():

    global client

    if client is None:
        logger.info("Initial connection failed, retrying...")
        client = attempt_connection()

    if client:
        return client[DB_NAME]
    else:
        raise DatabaseConnectionError("Unable to connect to the database.")