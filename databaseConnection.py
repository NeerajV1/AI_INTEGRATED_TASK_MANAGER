import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
def connect():
    return psycopg2.connect(
        host="localhost",
        database="mydb",
        user="postgres",
        password=os.getenv("password")
    )