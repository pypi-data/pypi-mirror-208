import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
class database():
    
    def connect_to_database(self):
        mydb = mysql.connector.connect(
        host=os.getenv("RDS_HOSTNAME"),
        user=os.getenv("RDS_USERNAME"),
        password=os.getenv("RDS_PASSWORD")
        )
        return mydb
