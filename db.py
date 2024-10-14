import mysql.connector
from mysql.connector import pooling

class DatabaseSingleton:
    _instance = None
    _connection_pool = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            if config:
                cls._connection_pool = pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=10,  # adjust pool size as needed
                    **config
                )
                
                print('number of pool')
        return cls._instance

    def get_connection(self):
        if self._connection_pool:
            print('pool is initiolazed')
            return self._connection_pool.get_connection()
            
        else:
            raise Exception("Connection pool is not initialized.")
