import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

dbname = os.getenv("dbname")
user = os.getenv("user")
password = os.getenv("pass")
host = os.getenv("host")
port = os.getenv("port")


def get_connection():
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
