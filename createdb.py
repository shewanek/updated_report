import mysql.connector
from dependence import connect_to_database

# Function to create the table
def create_crm_list_table():
    mydb = connect_to_database()
    cursor = mydb.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS crm_list (
        employe_id CHAR(36) PRIMARY KEY,
        dis_Id CHAR(36),
        full_name VARCHAR(255),
        crm_password VARCHAR(255),
        registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT crm_district
          FOREIGN KEY (dis_Id)
          REFERENCES district_list(dis_Id)
          ON DELETE CASCADE
          ON UPDATE CASCADE
    );
    """

    try:
        cursor.execute(create_table_query)
        mydb.commit()
        print("Table `crm_list` created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        mydb.close()

if __name__ == "__main__":
    create_crm_list_table()
