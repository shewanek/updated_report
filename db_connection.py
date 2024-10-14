from db import DatabaseSingleton

class DatabaseOperations:
    def __init__(self):
        config = {
            # "host":"localhost",
            # "port":"3306",
            # "user":"root",
            # "password":"SH36essti",
            # "database":"michudashboard" 
            "host":"10.101.200.141",
            "port":"3306",
            "user":"sane",
            "password":"Sanemichu!4422",
            "database":"michu_dashBoard"
        }
        self.db = DatabaseSingleton(config)
        print("connected successfully")

    def fetch_data(self, query, params=None):
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
    def fetch_one(self, query, params=None):
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()  # Fetch one result
            return result
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def insert_data(self, query, params=None):
        connection = None
        cursor = None
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
