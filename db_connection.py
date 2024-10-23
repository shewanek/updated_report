import streamlit as st
from db import DatabaseSingleton

class DatabaseOperations:
    def __init__(self):
        config = {
            "host": "10.101.200.141",        
            "port": "3306",
            "user": "sane",     
            "password": "Sanemichu!4422",  
            "database": "michu_dashBoard" 
            # "host": "localhost",        
            # "port": "3306",
            # "user": "root",     
            # "password": "SH36essti",  
            # "database": "michudashboard" 
        }
        self.db = DatabaseSingleton(config)
        print("Database connection established successfully.")

    def fetch_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()

            return result
        except Exception as e:
            st.error("connection error")
            # st.exception(e)
        finally:
            if cursor:
                cursor.close()
            connection.close()  # Return the connection to the pool

    def fetch_one(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            return cursor.fetchone()
        except Exception as e:
            st.error(f"connection error {e}")
            # st.exception(e)
        finally:
            if cursor:
                cursor.close()
            connection.close()

    def insert_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        finally:
            if cursor:
                cursor.close()
            connection.close()

    # Add the insert_many function here
    def insert_many(self, query, params_list):
        connection = self.db.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.executemany(query, params_list)  # Use executemany for batch inserts
            connection.commit()
            return cursor.rowcount  # Return the number of rows inserted
        finally:
            if cursor:
                cursor.close()
            connection.close()
    # Add the update function here
    def update_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount  # Return the number of rows updated
        finally:
            if cursor:
                cursor.close()
            connection.close()


