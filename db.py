import mysql.connector
from mysql.connector import Error

class DatabaseSingleton:
    _instance = None
    _connection = None

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls.config = config
            try:
                cls._connection = mysql.connector.connect(**config)
                if cls._connection.is_connected():
                    print("Successfully connected to the database")
                else:
                    cls._connection = None  # Set to None if the connection fails
            except Error as e:
                print(f"Error while connecting to MySQL: {e}")
                cls._connection = None
        return cls._instance

    def get_connection(self):
        # Check if the connection is still alive
        if self._connection is not None:
            try:
                self._connection.ping(reconnect=True, attempts=3, delay=2)
                return self._connection
            except Error as e:
                print(f"Connection error: {e}")
                self._connection = None
        # Attempt to reconnect if connection is None
        return self._reconnect()

    def _reconnect(self):
        try:
            self._connection = mysql.connector.connect(**self.config)
            if self._connection.is_connected():
                print("Reconnected to the database")
                return self._connection
            else:
                print("Failed to reconnect to the database")
                return None
        except Error as e:
            print(f"Reconnection attempt failed: {e}")
            return None
