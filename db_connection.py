import streamlit as st
import traceback
from db import DatabaseSingleton
from mysql.connector import Error

import tornado.websocket
from tornado.iostream import StreamClosedError


import os
from dotenv import load_dotenv

import sys
sys.tracebacklimit = 0  # Cleaner error output in Streamlit

class DatabaseOperations:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        config = {
            "host": "10.101.200.141",        
            "port": "3306",
            "user": "sane",     
            "password": "Sanemichu!4422",  
            "database": "michu_dashBoard",
            "connect_timeout": 5  # Add connection timeout

            # "host": os.getenv("DB_HOST"),
            # "port": os.getenv("DB_PORT"),
            # "user": os.getenv("DB_USER"),
            # "password": os.getenv("DB_PASSWORD"),
            # "database": os.getenv("DB_NAME"),
            # "host":"localhost",
            # "port":"3306",
            # "user":"root",
            # "password":"SH36essti",
            # "database":"michu_dashboard",
            # "connect_timeout": 5  # Add connection timeout
        }
        self.db = DatabaseSingleton(config)
        print("Database connection pool established successfully.")

    def _handle_websocket_error(self, e):
        """Special handling for WebSocket errors during database operations"""
        if isinstance(e, (tornado.websocket.WebSocketClosedError, StreamClosedError)):
            # logger.warning("WebSocket connection closed during database operation")
            return True
        return False

    def fetch_data(self, query, params=None):
        connection = self.db.get_connection()
        if connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(query, params)   
                    result = cursor.fetchall()
                    return result
                except Error as e:
                    if self._handle_websocket_error(e):
                        return None  # Gracefully handle WebSocket closure
                    # Print a full stack trace for debugging
                    print("Database fetch error:", e)
                    traceback.print_exc()  # This prints the full error trace to the terminal
                    st.error("Database fetch error. Please check the logs for details.")
                finally:
                    connection.close()
        return None

    def fetch_one(self, query, params=None):
        connection = self.db.get_connection()
        if connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(query, params)
                    return cursor.fetchone()
                    
                except Error as e:
                    if self._handle_websocket_error(e):
                        return None  # Gracefully handle WebSocket closure
                    # Print a full stack trace for debugging
                    print("Database fetch error:", e)
                    traceback.print_exc()  # This prints the full error trace to the terminal
                    st.error("Database fetch error. Please check the logs for details.")
                finally:
                    connection.close()
        return None
    def insert_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            if connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
            else:
                st.error("Failed to insert data: Connection is None")
        except Error as e:
            if self._handle_websocket_error(e):
                return None  # Gracefully handle WebSocket closure
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
            st.error(f"Database insert error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def insert_many(self, query, params_list):
        connection = self.db.get_connection()
        cursor = None
        try:
            if connection:
                cursor = connection.cursor()
                cursor.executemany(query, params_list)
                connection.commit()
                return cursor.rowcount
            else:
                st.error("Failed to insert data: Connection is None")
        except Error as e:
            if self._handle_websocket_error(e):
                return None  # Gracefully handle WebSocket closure
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
            st.error(f"Database batch insert error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            if connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount
            else:
                st.error("Failed to update data: Connection is None")
        except Error as e:
            if self._handle_websocket_error(e):
                return None
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
            st.error(f"Database update error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    def delete_data(self, query, params=None):
        connection = self.db.get_connection()
        cursor = None
        try:
            if connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount  # Return number of rows deleted
            else:
                st.error("Failed to delete data: Connection is None")
        except Error as e:
            if self._handle_websocket_error(e):
                return None  # Gracefully handle WebSocket closure
            # Print a full stack trace for debugging
            print("Database delete error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
            st.error("Database delete error. Please check the logs for details.")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
