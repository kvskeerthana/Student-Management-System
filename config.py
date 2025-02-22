import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Keerthana_@1",  # Replace with your MySQL password
        database="StudentDB"
    )
