import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@123",   # use your MySQL root password
        database="smart_canteen"
    )
    return connection
