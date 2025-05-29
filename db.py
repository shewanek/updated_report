import mysql.connector
from mysql.connector import Error, pooling
import threading

class DatabaseSingleton:
    _instance = None
    _lock = threading.Lock()
    _pool = None

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls.config = config
            cls._initialize_pool(config)
        return cls._instance

    @classmethod
    def _initialize_pool(cls, config):
        """Create a connection pool with session reset on each checkout."""
        try:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=10,  # Adjust pool size as needed
                pool_reset_session=True,
                **config
            )
            print("Connection pool created successfully")
        except Error as e:
            print(f"Error creating connection pool: {e}")
            cls._pool = None

    def get_connection(self):
        """Fetch a connection from the pool, with reconnection if necessary."""
        try:
            if self._pool:
                connection = self._pool.get_connection()
                if connection.is_connected():
                    return connection
                else:
                    print("Failed to connect, attempting to reconnect.")
                    return self._reconnect()
            else:
                print("Connection pool not available, attempting to recreate.")
                return self._reconnect()
        except Error as e:
            print(f"Error fetching connection from pool: {e}")
            return self._reconnect()

    def _reconnect(self):
        """Attempts to re-establish the connection pool if connections fail."""
        try:
            print("Reinitializing connection pool...")
            self._initialize_pool(self.config)  # Reinitialize the pool
            # Try getting a new connection after pool reinitialization
            connection = self._pool.get_connection()
            if connection.is_connected():
                print("Reconnected successfully.")
                return connection
            else:
                print("Reconnection failed.")
                return None
        except Error as e:
            print(f"Reconnection attempt failed: {e}")
            return None
