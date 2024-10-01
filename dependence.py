import mysql.connector
import pandas as pd
import streamlit as st
import hashlib
import re
import json


# Function to establish MySQL connection (with error handling and resource cleanup)
def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            # host="63.34.199.220",
            # port="3306",
            # user="sane",
            # password="sanemysql!2244",
            # database="michu_dashBoard"
            host="localhost",
            port="3306",
            user="root",
            password="SH36essti",
            database="michuDashBoard" 
        )
        print("Connected to MySQL database successfully.")
        return mydb
    except mysql.connector.Error as err:
        print("Error connecting to database:", err)
        st.error("An error occurred while connecting to the database. Please check your connection details.")
        return None  # Indicate failure

def fetch_data(query, mydb):
    if mydb is not None:
        cursor = mydb.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()  # Close cursor after fetching data
        return data
    else:
        return []

def load_dataframes(mydb):
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"
    # Fetch data with JOIN to get branch name from branch_list table
    query = """
    SELECT ui.userId, ui.userName, ui.district, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """
    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'Branch'])

    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId','userName','District','Branch'])
    df_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), columns=['customerId', 'userId','full Name', 'Product Type','Phone Number','Saving Account', 'Region', 'Zone/sub city/ Woreda','Register Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='userId', how='inner')
    
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/sub city/ Woreda', 'Register Date']]
    
    return df_combine

def load_unquie(mydb):
    query = """
    SELECT d.district_name, bl.branch_code, bl.branch_name
    FROM branch_list bl
    JOIN district_list d ON bl.dis_Id = d.dis_Id
    """

    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['District', 'branch_code', 'Branch'])
    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine

def load_unquiecustomer(mydb):
    query = """
    SELECT ui.userId, ui.userName, ui.district, branch_code, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    branch_customer = pd.DataFrame(fetch_data(branch_customer_query, mydb), columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date'])

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_info, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_info, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    # Step 1: Identify rows in branch_customer that are not in df_customer
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]

    # Step 2: Merge the result with df_user_info to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_info, on='userId', how='inner')

    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

    # Now registed_by_branch will contain only the rows from branch_customer that were not found in df_customer

    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine



def load_convertion(mydb):
    query = """
    SELECT ui.userId, ui.userName, ui.district, branch_code, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """

    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM conversiondata WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['ConversionId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['ConversionId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine


def load_branchdata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]

    # Fetch data from user_info and duretCustomer tables based on userId
    # Fetch data from user_info and join with branch_list to get the branch name
    query = f"""
    SELECT ui.userId, ui.userName, ui.district, ui.branch, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.userId = '{user_id}'
    """
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])


    # df_user_info = pd.DataFrame(fetch_data(f"SELECT * FROM user_info WHERE userId = '{user_id}'", mydb), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role', 'password', 'ccreatedAt'])
    # Filtered queries for data starting from July 1
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `disbursed_date` >= '2024-07-01'"
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE `disbursed_date` >= '2024-07-01'"

    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), columns=['uniqId', 'userId', 'full Name', 'Product_Type', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date'])
    unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge df_user_info with dureti_customer on 'userId'
    merged_df_1 = pd.merge(df_user_info, dureti_customer, on='userId', how='inner')
    
    merged_df_2 = pd.merge(df_user_info, unique_customer, on='branch_code', how='inner')
    # merged_df_2

    merged_df_3 = pd.merge(df_user_info, conversion_customer, on='branch_code', how='inner')
    # merged_df_3

    branch_customer = pd.DataFrame(fetch_data(branch_customer_query, mydb), columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date'])

    unique_by_branch = pd.merge(branch_customer, unique_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_info, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(unique_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_info, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    # Step 1: Identify rows in branch_customer that are not in df_customer
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(unique_customer['Saving Account'])]

    # Step 2: Merge the result with df_user_info to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_info, on='userId', how='inner')

    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]


    return merged_df_1, merged_df_2, merged_df_3, unique_cust_by_branch, unique_cust_by_self, registed_by_branch

def load_districtduretidata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]
    # district ["Centeral Finfinne", "East Finfinne", "Western Finfinne"]

    # Fetch data from user_info and duretCustomer tables based on userId
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_name, ui.role
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = '{district}'
    """
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role'])

    # df_user_info = pd.DataFrame(fetch_data(f"SELECT * FROM user_info WHERE district = '{district}'", mydb), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role', 'password', 'ccreatedAt'])
    df_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), columns=['customerId', 'userId', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date'])

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='userId', how='inner')

    # Select specific columns for the combined DataFrame
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date']]

    return df_combine


def load_districtuniquedata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = f"SELECT  district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    # district = user_id_result[0][1]
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `disbursed_date` >= '2024-07-01'"
    query = f"""
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = '{district}'
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId', 'userName','District','Branch'])

    df_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    branch_customer = pd.DataFrame(fetch_data(branch_customer_query, mydb), columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date'])

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_info, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_info, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    # Step 1: Identify rows in branch_customer that are not in df_customer
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]

    # Step 2: Merge the result with df_user_info to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_info, on='userId', how='inner')

    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

    # Now registed_by_branch will contain only the rows from branch_customer that were not found in df_customer

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    df_combine = merged_df[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine


def load_districtconversiondata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = f"SELECT  district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    # district = user_id_result[0][1]
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE `disbursed_date` >= '2024-07-01'"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_code, bl.branch_name, ui.role
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = '{district}'
    """
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'full_Name', 'userName', 'District', 'branch_code', 'Branch', 'role'])
    
    # df_user_info = pd.DataFrame(fetch_data(f"SELECT * FROM user_info WHERE district = '{district}'", mydb), columns=['userId', 'full_Name','userName','District','Branch','role','password','ccreatedAt'])
    df_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), columns=['convId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['convId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    return df_combine


def aggregate_and_insert_actual_data(mydb):
    # Fetch the latest disbursed_date from unique_intersection and conversiondata tables
    latest_disbursed_query = """
        SELECT MAX(disbursed_date) 
        FROM (
            SELECT disbursed_date FROM unique_intersection
            UNION
            SELECT disbursed_date FROM conversiondata
        ) AS combined_dates
    """
    latest_disbursed_date = fetch_data(latest_disbursed_query, mydb)[0][0]
    
    # Check if this date already exists in the actual table
    check_date_query = f"""
        SELECT EXISTS (
            SELECT 1 FROM actual WHERE actual_date = '{latest_disbursed_date}'
        )
    """
    date_exists = fetch_data(check_date_query, mydb)[0][0]
    
    if date_exists:
        # st.warning("The latest disbursed date is already present in the actual table.")
        return
    # Fetch the disbursed_date from both tables to ensure they are equal
    date_check_query = f"""
        SELECT
            (SELECT disbursed_date FROM unique_intersection WHERE disbursed_date = '{latest_disbursed_date}' LIMIT 1) AS unique_date,
            (SELECT disbursed_date FROM conversiondata WHERE disbursed_date = '{latest_disbursed_date}' LIMIT 1) AS conversion_date
    """
    date_check = fetch_data(date_check_query, mydb)[0]
    
    unique_date = date_check[0]
    conversion_date = date_check[1]
    
    if unique_date != conversion_date:
        # st.warning("The disbursed_date in unique_intersection does not match the disbursed_date in conversiondata.")
        return
    
    # Fetch data from unique_intersection and conversiondata tables where disbursed_date is the latest
    unique_query = f"""
        SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, uni_id
        FROM unique_intersection
        WHERE disbursed_date = '{latest_disbursed_date}'
    """
    conversion_query = f"""
        SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, conv_id
        FROM conversiondata
        WHERE disbursed_date = '{latest_disbursed_date}'
    """
    
    unique_data = fetch_data(unique_query, mydb)
    conversion_data = fetch_data(conversion_query, mydb)
    
    # Convert fetched data to DataFrames
    unique_df = pd.DataFrame(unique_data, columns=['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date', 'uni_id'])
    conversion_df = pd.DataFrame(conversion_data, columns=['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date', 'conv_id'])
    
    # Concatenate both DataFrames
    combined_df = pd.concat([unique_df, conversion_df])
    
    if combined_df.empty:
        # st.warning("No data found in unique_intersection or conversiondata tables for the latest disbursed_date.")
        return

    # Group by branch_code and aggregate the required columns
    aggregated_df = combined_df.groupby('branch_code').agg(
        unique_actual=('uni_id', 'nunique'),
        account_actual=('saving_account', 'count'),
        disbursment_actual=('disbursed_amount', 'sum'),
        actual_date=('disbursed_date', 'first')
    ).reset_index()
    
    # Insert aggregated data into the actual table
    cursor = mydb.cursor()
    for index, row in aggregated_df.iterrows():
        # Check if this branch_code and actual_date already exist in the actual table
        check_record_query = """
            SELECT EXISTS (
                SELECT 1 FROM actual 
                WHERE branch_code = %s AND actual_date = %s
            )
        """
        cursor.execute(check_record_query, (row['branch_code'], row['actual_date']))
        record_exists = cursor.fetchone()[0]
        
        if not record_exists:
            # Insert the new record only if it doesn't already exist
            cursor.execute("""
                INSERT INTO actual (branch_code, unique_actual, account_actual, disbursment_actual, actual_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['branch_code'], row['unique_actual'], row['account_actual'], row['disbursment_actual'], row['actual_date']))
    
    mydb.commit()
    cursor.close()



def load_actual_vs_targetdata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        user_id_query = "SELECT district FROM user_info"
        district_result = fetch_data(user_id_query, mydb)
        # print(district_result)
        if not district_result:
            st.warning("No users found.")
            return pd.DataFrame()  # Return an empty DataFrame if no users are found

        # Handle the mix of lists and non-lists in the result
        districts = []
        for item in district_result:
            if isinstance(item, list):
                districts.extend(item)
            else:
                districts.append(item)
        # Flatten nested lists and tuples, ensuring all items are strings
        districts = [str(d[0]) if isinstance(d, (list, tuple)) else str(d) for d in districts]
        
        # Convert the list of districts to a string suitable for the SQL IN clause
        districts_str = ', '.join(f"'{d}'" for d in districts)
        # print(districts_str)

        district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name IN ({districts_str})"
        district_result = fetch_data(district_query, mydb)
        if not district_result:
            st.warning("No district found with the given district names.")
            return pd.DataFrame()  # Return an empty DataFrame if no districts are found

        dis_ids = [row[0] for row in district_result]

        # Convert the list of dis_Id to a string suitable for the SQL IN clause
        dis_ids_str = ', '.join(f"'{d}'" for d in dis_ids)



        # Fetch branch code and branch name
        branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id IN ({dis_ids_str})"
        branch_code_result = fetch_data(branch_code_query, mydb)
        if not branch_code_result:
            st.warning("No branches found for the given districts.")
            return pd.DataFrame()  # Return an empty DataFrame if no branches are found

        # Extract branch codes from the result
        branch_codes = [row[1] for row in branch_code_result]

        # Convert the list of branch codes to a string suitable for the SQL IN clause
        branch_codes_str = ', '.join(f"'{c}'" for c in branch_codes)

        # Create DataFrames from the fetched data
        actul_dis = pd.DataFrame(district_result, columns=['dis_Id', 'District'])
        actual_branch = pd.DataFrame(branch_code_result, columns=['dis_Id', 'Branch Code', 'Branch'])

        # Merge DataFrames based on 'dis_Id'
        act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')


        

        # Aggregate and insert actual data
        aggregate_and_insert_actual_data(mydb)


        # Fetch actual data
        df_actual = pd.DataFrame(
            fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code IN ({branch_codes_str})", mydb), 
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )      
        # Fetch target data
        df_target = pd.DataFrame(
            fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code IN ({branch_codes_str})", mydb),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        return act_dis_branch, df_actual, df_target


    elif role == "Sales Admin":
        district_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        district_result = fetch_data(district_query, mydb)

        if not district_result:
            st.warning("No users found.")
            return pd.DataFrame()  # Return an empty DataFrame if no users are found

        district = district_result[0][0]
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]

        # Convert the list of districts to a string suitable for the SQL IN clause
        districts_str = ', '.join(f"'{d}'" for d in districts)

        # Fetch dis_Id for the districts
        district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name IN ({districts_str})"
        district_result = fetch_data(district_query, mydb)
        if not district_result:
            st.warning("No district found with the given district names.")
            return pd.DataFrame()  # Return an empty DataFrame if no districts are found

        dis_ids = [row[0] for row in district_result]

        # Convert the list of dis_Id to a string suitable for the SQL IN clause
        dis_ids_str = ', '.join(f"'{d}'" for d in dis_ids)

        # Fetch branch code and branch name
        branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id IN ({dis_ids_str})"
        branch_code_result = fetch_data(branch_code_query, mydb)
        if not branch_code_result:
            st.warning("No branches found for the given districts.")
            return pd.DataFrame()  # Return an empty DataFrame if no branches are found

        # Extract branch codes from the result
        branch_codes = [row[1] for row in branch_code_result]

        # Convert the list of branch codes to a string suitable for the SQL IN clause
        branch_codes_str = ', '.join(f"'{c}'" for c in branch_codes)

        # Create DataFrames from the fetched data
        actul_dis = pd.DataFrame(district_result, columns=['dis_Id', 'District'])
        actual_branch = pd.DataFrame(branch_code_result, columns=['dis_Id', 'Branch Code', 'Branch'])

        # Merge DataFrames based on 'dis_Id'
        act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')

        # Fetch actual data
        df_actual = pd.DataFrame(
            fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code IN ({branch_codes_str})", mydb), 
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )

        # Fetch target data
        df_target = pd.DataFrame(
            fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code IN ({branch_codes_str})", mydb),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        return act_dis_branch, df_actual, df_target

    elif role == "Branch User":
        # Fetch branch and district for the given username
        
        user_id_query = f"SELECT branch, district FROM user_info WHERE userName = '{username}'"
        user_id_result = fetch_data(user_id_query, mydb)

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame()  # Return an empty DataFrame if no user is found

        branch = user_id_result[0][0]  # Assuming branch is the first element in the first row of the result
        district = user_id_result[0][1]

        # Fetch branch code and branch name
        branch_code_query = f"SELECT branch_code, branch_name FROM branch_list WHERE branch_code = '{branch}'"
        branch_code_result = fetch_data(branch_code_query, mydb)

        if not branch_code_result:
            st.warning("No branch found with the given branch name.")
            return pd.DataFrame()  # Return an empty DataFrame if no branch is found

        branch_code = branch_code_result[0][0]

        # Create DataFrames from the fetched data
        actul_dis = pd.DataFrame(user_id_result, columns=['Branch Code', 'District'])
        actual_branch = pd.DataFrame(branch_code_result, columns=['Branch Code', 'Branch'])

        # Merge DataFrames based on 'branch'
        act_dis_branch = pd.merge(actul_dis, actual_branch, on='Branch Code', how='inner')

        # Fetch actual data
        df_actual = pd.DataFrame(
            fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code = '{branch_code}'", mydb),
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )

        # Fetch target data
        df_target = pd.DataFrame(
            fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code = '{branch_code}'", mydb),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        
        return act_dis_branch, df_actual, df_target


    else:
        # Fetch branch and district for the given username
        user_id_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_id_result = fetch_data(user_id_query, mydb)

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame()  # Return an empty DataFrame if no user is found

        # district = user_id_result[0][0]  # Assuming district is the first element in the first row of the result
        district = user_id_result[0][0]

        # Fetch dis_Id for the district
        district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name = '{district}'"
        district_result = fetch_data(district_query, mydb)
        if not district_result:
            st.warning("No district found with the given district name.")
            return pd.DataFrame()  # Return an empty DataFrame if no district is found

        dis_id = district_result[0][0]

        # Fetch branch code and branch name
        branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id = '{dis_id}'"
        branch_code_result = fetch_data(branch_code_query, mydb)
        if not branch_code_result:
            st.warning("No branches found for the given district.")
            return pd.DataFrame()  # Return an empty DataFrame if no branches are found

        # Extract branch codes from the result
        branch_code = [f"'{row[1]}'" for row in branch_code_result]  # Get all branch codes from the query result and quote them

        # Create DataFrames from the fetched data
        actul_dis = pd.DataFrame(district_result, columns=['dis_Id', 'District'])
        actual_branch = pd.DataFrame(branch_code_result, columns=['dis_Id', 'Branch Code', 'Branch'])

        # Merge DataFrames based on 'dis_Id'
        act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')

        # Fetch actual data
        df_actual = pd.DataFrame(
            fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code IN ({','.join(branch_code)})", mydb), 
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )

        # Fetch target data
        df_target = pd.DataFrame(
            fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code IN ({','.join(branch_code)})", mydb),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        return act_dis_branch, df_actual, df_target





def load_salesduretidata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]
    # Parse the JSON format district
    districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{district}'" for district in districts)

    # SQL query using the IN clause
    # query = f"SELECT * FROM user_info WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_name, ui.role
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"

    # Fetch data from user_info and duretCustomer tables based on userId
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role'])
    df_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), columns=['customerId', 'userId', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date'])

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='userId', how='inner')

    # Select specific columns for the combined DataFrame
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date']]

    return df_combine

def load_salesuniquedata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = f"SELECT  district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    # Parse the JSON format district
    districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{district}'" for district in districts)


    # SQL query using the IN clause
    # query = f"SELECT * FROM user_info WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_info = pd.DataFrame(fetch_data("SELECT userId, userName, district, branch FROM user_info", mydb), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    branch_customer = pd.DataFrame(fetch_data(branch_customer_query, mydb), columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date'])

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_info, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_info, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]
    # Step 2: Merge the result with df_user_info to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_info, on='userId', how='inner')
    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

    # Merge the two DataFrames based on 'userId'
    merged_df_uni = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df_uni[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Product Type', 'Customer Name', 'Saving Account', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    

    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine

def load_salesconversiondata(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_info WHERE userName = '{username}'"
    user_id_result = fetch_data(user_id_query, mydb)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]
    # Parse the JSON format district
    districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{district}'" for district in districts)
    # query = f"SELECT * FROM user_info WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_code, bl.branch_name, ui.role
    FROM user_info ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE `Disbursed_Date` >= '2024-07-01'"

    df_user_info = pd.DataFrame(fetch_data(query, mydb), columns=['userId', 'full_Name','userName','District', 'branch_code', 'Branch','role'])
    df_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), columns=['ConversionId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_info, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['ConversionId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    return df_combine

def load_resetpassword(mydb):
    df_combine = pd.DataFrame(fetch_data("SELECT * FROM reset_user_password", mydb), columns=['ResetId', 'user_Id', 'user name','full Name','outlook email','District/Branch','Asked Date'])
    
    return df_combine


def insert_user(conn, cursor, fullName, username, district, branch, role, password):
    """
    Inserts a new user into the MySQL server database.

    Args:
        email: User's email address.
        username: User's chosen username.
        password: User's password (plain text).

    Returns:
        True if insertion is successful, False otherwise.
    """
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT branch_code FROM branch_list WHERE branch_name = %s", (branch,))
    resultt = cursor.fetchone()
    if resultt is None:
        # st.warning("Branch not found in the database. Setting branch to NULL.")
        branch_code = None
    else:
        branch_code = resultt[0]

    # Fetch role_id
    cursor.execute("SELECT role_Id FROM role_list WHERE role = %s", (role,))
    result = cursor.fetchone()
    if result is None:
        st.error("Role not found in the database.")
        return False
    role_id = result[0]

    try:
        cursor.execute("""
            INSERT INTO user_info (full_Name, userName, district, branch, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fullName, username, district, branch_code, role_id, hashed_password))
        conn.commit()
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False

def insert_customer(conn, cursor, username, fullName, Product_Type, phone_number, Saving_Account, Region, Woreda):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_info table using the provided username
        cursor.execute("SELECT userId FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()  # Fetch the first row
        if result:
            userId = result[0]  # Extract userId from the result
            # Insert customer information into the customer table
            cursor.execute("""
                INSERT INTO duretCustomer (userId, fullName, Product_Type, phoneNumber, Saving_Account, Region, Woreda)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (userId, fullName, Product_Type, processed_phone_number, Saving_Account, Region, Woreda))
            conn.commit()
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False
def insert_resetpuser(conn, cursor, username, name, outlook_email, branch_name):
    """
    Inserts a new user into the MySQL server database.

    Args:
        email: User's email address.
        username: User's chosen username.
        password: User's password (plain text).

    Returns:
        True if insertion is successful, False otherwise.
    """
    user_id = []
    if username in get_usernames(cursor):
        cursor.execute("SELECT userId FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()
        user_id = result[0]
    else:
        cursor.execute("SELECT crm_id FROM crm_user WHERE username = %s", (username,))
        result = cursor.fetchone()
        user_id = result[0]

    try:
        cursor.execute("""
            INSERT INTO reset_user_password (`user_Id`,`user name`, `full Name`, `outlook email`, `District/Branch`)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, username, name, outlook_email, branch_name))
        conn.commit()
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False
    

def conversion_customer(conn, cursor, username, fullName, Product_Type, phone_number, Saving_Account, collected_Amount, amount_borrowed_again,remark):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_info table using the provided username
        cursor.execute("SELECT userId FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()  # Fetch the first row
        if result:
            userId = result[0]  # Extract userId from the result
            # Insert customer information into the customer table
            cursor.execute("""
                INSERT INTO conversioncustomer (userId, fullName, Product_Type, phoneNumber, Saving_Account, collected_Amount, Amount_borrowed_Again, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (userId, fullName, Product_Type, processed_phone_number, Saving_Account, collected_Amount, amount_borrowed_again,remark))
            conn.commit()
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False

# come back
def unique_customer(conn, cursor, username, fullName, Product_Type, phone_number, tin_number, Saving_Account, disbursed_Amount,remark):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_info table using the provided username
        cursor.execute("SELECT userId FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()  # Fetch the first row
        if result:
            userId = result[0]  # Extract userId from the result
            # Insert customer information into the customer table
            cursor.execute("""
                INSERT INTO uniquecustomer (userId, fullName, Product_Type, phoneNumber, tin_number, Saving_Account, disbursed_Amount, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (userId, fullName, Product_Type, processed_phone_number, tin_number, Saving_Account, disbursed_Amount, remark))
            conn.commit()
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False

def validate_phone(phone):
    """
    Validates if the given phone number is in the correct format.

    Args:
    phone_number (str): The phone number to validate.

    Returns:
    bool: True if the phone number is valid, False otherwise.
    """
    pattern = r"^(09|07)\d{8}$"
    
    return re.match(pattern, phone)


def validate_full_name(full_name):
    """
    Validates if the given full name contains both a first name and a last name.

    Args:
    full_name (str): The full name to validate.

    Returns:
    bool: True if the full name is valid, False otherwise.
    """
    # Regular expression to match two to four words separated by a space
    pattern = r"^[A-Za-z0-9./']+ [A-Za-z0-9./']+(?: [A-Za-z0-9./']+){0,2}$"
    return re.match(pattern, full_name.strip())

def validate_tin_number(tin_number):
    """
    Validates if the given TIN number is exactly 10 digits long.

    Args:
    tin_number (str): The TIN number to validate.

    Returns:
    bool: True if the TIN number is valid, False otherwise.
    """
    pattern = r"^\d{10}$"
    return(pattern, tin_number)

def validate_username(username):
    """
    Checks username validity using a regular expression.

    Args:
        username: The username to validate.

    Returns:
        True if the username is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9_-]{2,}$"
    return re.match(pattern, username)

def get_user_emails(cursor):
    """
    Fetches a list of user emails from the MySQL server database.

    Returns:
        A list of user email addresses.
    """
    cursor.execute("SELECT email FROM dashUsers")
    emails = [user[0] for user in cursor.fetchall()]
    return emails

def get_usernames(cursor):
    """
    Fetches a list of usernames from the MySQL server database.

    Returns:
        A list of user usernames.
    """
    cursor.execute("SELECT username FROM user_info")
    usernames = [user[0] for user in cursor.fetchall()]
    return usernames

def get_crmusernames(cursor):
    """
    Fetches a list of usernames from the MySQL server database.

    Returns:
        A list of user usernames.
    """
    cursor.execute("SELECT username FROM crm_user")
    usernames = [user[0] for user in cursor.fetchall()]
    return usernames

def get_password_by_username(cursor, username):
    """
    Fetches the hashed password associated with a given username.

    Args:
        username: The username to fetch the password for.

    Returns:
        The hashed password if the username exists, None otherwise.
    """
    cursor.execute("SELECT password FROM user_info WHERE username = %s", (username,))
    result = cursor.fetchone()
    # cursor.execute("SELECT crm_password FROM crm_user WHERE username = %s", (username,))
    # resultt = cursor.fetchone()
    if result:
        return result[0]
    
    return None


def get_crmpassword_by_username(cursor, username):
    """
    Fetches the hashed password associated with a given username.

    Args:
        username: The username to fetch the password for.

    Returns:
        The hashed password if the username exists, None otherwise.
    """
    cursor.execute("SELECT crm_password FROM crm_user WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None


def verify_password(password, hashed_password):
    """
    Verifies a plain text password against a hashed password.

    Args:
        password: The plain text password.
        hashed_password: The hashed password to compare against.

    Returns:
        True if the passwords match, False otherwise.
    """
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def update_password(conn, cursor, username, new_password):
    """
    Updates the password for a given username in the MySQL server database.

    Args:
        username: The username for which to update the password.
        new_password: The new password (plain text).

    Returns:
        True if the password update is successful, False otherwise.
    """
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

    try:
        if username in get_usernames(cursor):
            cursor.execute("""
                UPDATE user_info
                SET password = %s
                WHERE username = %s
            """, (hashed_password, username))
            conn.commit()
            return True
        else:
            cursor.execute("""
                UPDATE crm_user
                SET crm_password = %s
                WHERE username = %s
            """, (hashed_password, username))
            conn.commit()
            return True
    except Exception as e:
        st.error("Failed to update password")
        st.exception(e)
        return False
def get_role_by_username(cursor, username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    # cursor.execute("SELECT role FROM user_info WHERE username = %s", (username,))
    cursor.execute("""
        SELECT rl.role 
        FROM user_info ui
        JOIN role_list rl ON ui.role = rl.role_Id
        WHERE ui.username = %s
    """, (username,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Returning the role
    else:
        return None
    

def get_role_by_crmusername(cursor, username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    # cursor.execute("SELECT role FROM user_info WHERE username = %s", (username,))
    cursor.execute("""
        SELECT ui.role 
        FROM crm_list ui
        JOIN crm_user rl ON ui.employe_id = rl.employe_id
        WHERE rl.username = %s
    """, (username,))
    resultt = cursor.fetchone()
    if resultt:
        return resultt[0]
    else:
        return None



def is_branch_registered(cursor, branch):
    """
    Checks if the given branch is registered in the `user_info` table.
    
    Args:
        cursor: MySQL cursor object.
        branch: The branch name to check.
        
    Returns:
        A list of branch names if the branch code is found in the `user_info` table, otherwise an empty list.
    """
    
    # Fetch branch_code from branch_list
    cursor.execute("SELECT branch_code FROM branch_list WHERE branch_name = %s", (branch,))
    result = cursor.fetchone()
    if result is None:
        # Branch not found in branch_list
        return []

    branch_code = result[0]

    # Check if branch_code is present in user_info
    cursor.execute("SELECT DISTINCT branch FROM user_info WHERE branch = %s", (branch_code,))
    result2 = cursor.fetchall()
    if not result2:
        # No records found for the branch_code in user_info
        return []

    # Fetch branch names corresponding to branch_code
    cursor.execute("SELECT branch_name FROM branch_list WHERE branch_code = %s", (branch_code,))
    branches = [row[0] for row in cursor.fetchall() if row[0] is not None]

    return branches


def get_duretiphone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber.
    """
    cursor.execute("SELECT phoneNumber FROM duretCustomer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    return modified_phone

def get_duretiacount(cursor):
    """
    Fetches a list of account from the MySQL server database.

    Returns:
        A list of user account.
    """
    cursor.execute("SELECT Saving_Account FROM duretCustomer")
    account = [user[0] for user in cursor.fetchall()]
    return account

def get_unquiephone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber.
    """
    cursor.execute("SELECT phoneNumber FROM uniquecustomer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone

def get_unquieaccount(cursor):
    """
    Fetches a list of account from the MySQL server database.

    Returns:
        A list of user account.
    """
    cursor.execute("SELECT Saving_Account FROM uniquecustomer")
    account = [user[0] for user in cursor.fetchall()]
    return account

def validate_saving_account(saving_account):
    """
    Validates if the saving account length is either 12 or 13 characters.

    Args:
    saving_account (str): The saving account to validate.

    Returns:
    bool: True if the saving account length is valid, False otherwise.
    """
    
    return saving_account.isdigit() and len(saving_account) in [12, 13]

def get_conversionphone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber.
    """
    cursor.execute("SELECT phoneNumber FROM conversioncustomer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    return modified_phone

def get_conversionaccount(cursor):
    """
    Fetches a list of account from the MySQL server database.

    Returns:
        A list of user account.
    """
    cursor.execute("SELECT Saving_Account FROM conversioncustomer")
    account = [user[0] for user in cursor.fetchall()]
    return account

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@coopbankoromiasc\.com$"
    return re.match(pattern, email)

def has_user_sent_request_today(cursor, username):
    """
    Checks if the user has already sent a reset request today.

    Args:
    cursor (MySQLCursor): The cursor object to execute the query.
    username (str): The username to check.

    Returns:
    bool: True if the user has already sent a request today, False otherwise.
    """
    query = """
    SELECT COUNT(*) FROM reset_user_password
    WHERE `user name` = %s AND `Asked Date` >= CURDATE() - INTERVAL 3 DAY
    """
    cursor.execute(query, (username,))
    request_count = cursor.fetchone()[0]
    return request_count > 0

def get_fullname_by_username(cursor, username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    cursor.execute("SELECT full_Name FROM user_info WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Returning the role

    else:
        return None
    

def get_fullname_by_crmusername(cursor, username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """

    cursor.execute("""SELECT ui.full_name FROM crm_list ui
                   JOIN crm_user rl ON ui.employe_id = rl.employe_id 
                   WHERE rl.username = %s""", (username,))
    resultt = cursor.fetchone()
    if resultt:
        return resultt[0]
    else:
        return None
    

def get_roles_from_db(cursor):
    # cursor = mydb.cursor()
    cursor.execute("SELECT role FROM role_list")
    roles = cursor.fetchall()
    cursor.close()
    return [role[0] for role in roles]

def get_district_from_db(cursor):
    # cursor = mydb.cursor()
    cursor.execute("SELECT district_name FROM district_list")
    district = cursor.fetchall()
    cursor.close()
    return [dis[0] for dis in district]

def get_branch_from_db(cursor, district):
    """
    Fetches branch names from the database for a given district.

    Args:
        cursor: Database cursor.
        district (str): The name of the district.

    Returns:
        list: List of branch names associated with the given district.
    """
    try:
        # Fetch the district ID
        cursor.execute("SELECT dis_Id FROM district_list WHERE district_name = %s", (district,))
        dis_id = cursor.fetchone()
        
        # Check if the district ID is found
        if dis_id:
            dis_id = dis_id[0]
            # Fetch branch names for the district ID
            cursor.execute("SELECT branch_name FROM branch_list WHERE dis_Id = %s", (dis_id,))
            branches = cursor.fetchall()
            return [branch[0] for branch in branches]
        else:
            # Return an empty list if no district ID is found
            return []
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error fetching branches: {e}")
        return []
    
def load_targetdata(mydb):
    df_branch = pd.DataFrame(fetch_data("SELECT branch_code, branch_name FROM branch_list", mydb), columns=['Branch Code', 'Branch'])

    query = """
    SELECT t.branch_code, t.unique_target, t.account_target, t.disbursment_target, t.target_date, t.created_date
    FROM target t
    JOIN (
        SELECT branch_code, MAX(created_date) AS max_date
        FROM target
        GROUP BY branch_code
    ) latest ON t.branch_code = latest.branch_code AND t.created_date = latest.max_date
    """
    
    df_target = pd.DataFrame(fetch_data(query, mydb), columns=['Branch Code', 'Unique Target', 'Account Target', 'Disbursment Target', 'Target Date', 'Uploaded Date'])

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_target, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Unique Target', 'Account Target', 'Disbursment Target', 'Target Date', 'Uploaded Date']]
    
    return df_combine

def load_actualdata(mydb):
    df_branch = pd.DataFrame(fetch_data("SELECT branch_code, branch_name FROM branch_list", mydb), columns=['Branch Code', 'Branch'])

    query = """
    SELECT t.branch_code, t.unique_actual, t.account_actual, t.disbursment_actual, t.actual_date, t.created_date
    FROM actual t
    JOIN (
        SELECT branch_code, MAX(created_date) AS max_date
        FROM actual
        GROUP BY branch_code
    ) latest ON t.branch_code = latest.branch_code AND t.created_date = latest.max_date
    """
    
    df_actual = pd.DataFrame(fetch_data(query, mydb), columns=['Branch Code', 'Unique Actual', 'Account Actual', 'Disbursment Actual', 'Actual Date', 'Uploaded Date'])

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Unique Actual', 'Account Actual', 'Disbursment Actual', 'Actual Date', 'Uploaded Date']]
    
    return df_combine



def branchCustomer(conn, cursor, username, fullName, product_type, phone_number, tin_number, Saving_Account, disbursed_Amount, region, zone, woreda, specific_area, line_of_business, purpose_of_loan, staff_name,  remark):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_info table using the provided username
        cursor.execute("SELECT userId FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()  # Fetch the first row
        if result:
            userId = result[0]  # Extract userId from the result
            # Insert customer information into the customer table
            cursor.execute("""
                INSERT INTO branchcustomer(userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Region, zone, Woreda, Specific_Area, Line_of_Business, Purpose_of_Loan, Staff_Name, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (userId, fullName, product_type, processed_phone_number, tin_number, Saving_Account, disbursed_Amount, region, zone, woreda, specific_area, line_of_business, purpose_of_loan, staff_name, remark))
            conn.commit()
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False



def check_unique_phone(cursor, phone_number):
    """
    Fetches phone number from the MySQL server database to check if it exists.

    Args:
        cursor: MySQL cursor object
        phone_number: Phone number to check

    Returns:
        bool: True if the phone number exists, False otherwise
    """
    processed_phone_number = "+251" + phone_number[1:]

    # Retrieve phone number from customer_list table
    cursor.execute("SELECT phone_number FROM customer_list WHERE phone_number = %s", (processed_phone_number,))
    result1 = cursor.fetchone()
    
    # Retrieve phone number from customer_list_nonecode table
    cursor.execute("SELECT phone_number FROM customer_list_nonecode WHERE phone_number = %s", (processed_phone_number,))
    result2 = cursor.fetchone()
    # Retrieve phone number from branchcustomer table
    cursor.execute("SELECT phoneNumber FROM branchcustomer WHERE phoneNumber = %s", (processed_phone_number,))
    result3 = cursor.fetchone()

     # Retrieve phone number from kiyya_customer table
    cursor.execute("SELECT phone_number FROM kiyya_customer WHERE phone_number = %s", (processed_phone_number,))
    result4 = cursor.fetchone()

     # Retrieve phone number from women_product table
    cursor.execute("SELECT phone_number FROM women_product_customer WHERE phone_number = %s", (processed_phone_number,))
    result5 = cursor.fetchone()
    
    # Check if phone number exists in any of the tables
    return result1 is not None or result2 is not None or result3 is not None or result4 is not None or result5 is not None

def check_unique_account(cursor, account):
    """
    Fetches phone number from the MySQL server database to check if it exists.

    Args:
        cursor: MySQL cursor object
        phone_number: Phone number to check

    Returns:
        bool: True if the phone number exists, False otherwise
    """
    # processed_phone_number = "+251" + phone_number[1:]

    # Retrieve phone number from customer_list table
    cursor.execute("SELECT saving_account FROM customer_list WHERE saving_account = %s", (account,))
    result1 = cursor.fetchone()
    
    # Retrieve phone number from customer_list_nonecode table
    cursor.execute("SELECT saving_account FROM customer_list_nonecode WHERE saving_account = %s", (account,))
    result2 = cursor.fetchone()

    # Retrieve phone number from branchcustomer table
    cursor.execute("SELECT Saving_Account FROM branchcustomer WHERE Saving_Account = %s", (account,))
    result3 = cursor.fetchone()

    # Retrieve phone number from actualdata table
    cursor.execute("SELECT saving_account FROM actualdata WHERE saving_account = %s", (account,))
    result4 = cursor.fetchone()

    # Retrieve phone number from unique_intersection table
    cursor.execute("SELECT saving_account FROM unique_intersection WHERE saving_account = %s", (account,))
    result5 = cursor.fetchone()

    # Retrieve phone number from conversiondata table
    cursor.execute("SELECT saving_account FROM conversiondata WHERE saving_account = %s", (account,))
    result6 = cursor.fetchone()

    # Retrieve phone number from kiyya_customer table
    cursor.execute("SELECT account_number FROM kiyya_customer WHERE account_number = %s", (account,))
    result7 = cursor.fetchone()
   

    # Retrieve phone number from women_product table
    cursor.execute("SELECT account_no FROM women_product_customer WHERE account_no = %s", (account,))
    result8 = cursor.fetchone()

    
    # Check if phone number exists in any of the tables
    return result1 is not None or result2 is not None or result3 is not None or result4 is not None or result5 is not None or result6 is not None or result7 is not None or result8 is not None



def load_uniqactualdata(mydb):
    df_branch = pd.DataFrame(fetch_data("SELECT branch_code, branch_name FROM branch_list", mydb), columns=['Branch Code', 'Branch'])

    query = """
    SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date
    FROM unique_intersection
    WHERE DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i') = (
    SELECT MAX(DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i')) FROM unique_intersection
    )
    """
    
    df_actual = pd.DataFrame(fetch_data(query, mydb), columns=['Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine

def load_convactualdata(mydb):
    df_branch = pd.DataFrame(fetch_data("SELECT branch_code, branch_name FROM branch_list", mydb), columns=['Branch Code', 'Branch'])

    query = """
    SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date
    FROM conversiondata
    WHERE DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i') = (
    SELECT MAX(DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i')) FROM conversiondata)
    """
    
    df_actual = pd.DataFrame(fetch_data(query, mydb), columns=['Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine

def load_customer_detail(mydb):
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    
    if role == 'Admin' or role == 'under_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        closed_query = """
        SELECT * FROM customer_list WHERE loan_status = 'Closed'
        """
        active_query = """
        SELECT * FROM customer_list WHERE loan_status = 'Active'
        """
        arrears_query = """
        SELECT * FROM customer_list WHERE loan_status = 'In Arrears'
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_district = fetch_data(user_query, mydb)
        district = user_district[0][0]
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        districts_str = ', '.join(f"'{d}'" for d in districts)
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        closed_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Closed'
        AND branch_code IN ({branch_codes_str})
        """
        active_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Active'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'District User': 
        user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_district = fetch_data(user_query, mydb)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name = '{user_district[0][0]}'
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        closed_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Closed'
        AND branch_code IN ({branch_codes_str})
        """
        active_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Active'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    elif role == 'Branch User':
        user_query = f"SELECT branch FROM user_info WHERE userName = '{username}'"
        user_branch_code = fetch_data(user_query, mydb)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE br.branch_code = '{user_branch_code[0][0]}'
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        closed_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Closed'
        AND branch_code IN ({branch_codes_str})
        """
        active_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Active'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'collection_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        closed_query = """
        SELECT * FROM customer_list WHERE loan_status = 'Closed'
        """
        active_query = """
        SELECT * FROM customer_list WHERE loan_status = 'Active'
        """
        arrears_query = """
        SELECT * FROM customer_list WHERE loan_status = 'In Arrears'
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'collection_user':
        user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_district = fetch_data(user_query, mydb)
        district = user_district[0][0]
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        districts_str = ', '.join(f"'{d}'" for d in districts)
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        closed_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Closed'
        AND branch_code IN ({branch_codes_str})
        """
        active_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'Active'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT * FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_closed = pd.DataFrame(fetch_data(closed_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(fetch_data(active_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(fetch_data(arrears_query, mydb), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    else:
        st.warning("No data for this user")
        quit()
        return None



def get_branch_code(mydb):
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # Queries with placeholders to prevent SQL injection
    branch_query = f"""
        SELECT ui.branch
        FROM user_info ui
        WHERE ui.username = '{username}'
    """
    
    col_admin_query = """
        SELECT branch_code
        FROM branch_list
    """

    user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
    
    user_district = fetch_data(user_query, mydb)
    if not user_district:
        return None

    district = user_district[0][0]
    
    # Handle the possibility of the district being a JSON-encoded string
    if isinstance(district, str):
        try:
            districts = json.loads(district)
        except json.JSONDecodeError:
            districts = [district]
    else:
        districts = [district]

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{d}'" for d in districts)

    col_user_query = f"""
    SELECT br.branch_code FROM branch_list br
    JOIN district_list dr ON br.dis_Id = dr.dis_Id
    WHERE dr.district_name IN ({districts_str})
    """
    branch_codes = None
    if role == 'Branch User':
        branch_code = fetch_data(branch_query, mydb)
        if branch_code:
            branchs_code = branch_code[0][0]
            if isinstance(branchs_code, str):
                try:
                    branch_codes = json.loads(branchs_code)
                except json.JSONDecodeError:
                    branch_codes = [branchs_code]
            else:
                branch_codes = [branchs_code]
        

    elif role == 'collection_admin':
        branch_code = fetch_data(col_admin_query, mydb)
        if branch_code:
            branchs_code = [row[0] for row in branch_code]
            branch_codes = branchs_code
        
    elif role == 'collection_user':
        branch_code = fetch_data(col_user_query, mydb)
        if branch_code:
            branchs_code = [row[0] for row in branch_code]
            branch_codes = branchs_code

    if branch_codes:
        return branch_codes, role  # Return a list of branch codes
    else:
        return None



def get_dis_and_branch(mydb):
    code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
    df_branch = pd.DataFrame(fetch_data(code_query, mydb), columns=['District', 'branch_code', 'Branch'])
    return df_branch





# Function to fetch employee ID from the crm_list table
def get_employe_id(mydb, employe_id):
    """
    Fetches an employee ID from the crm_list table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = f"SELECT employe_id FROM crm_list WHERE employe_id = '{employe_id}'"
    empid = fetch_data(query, mydb)
    
    if empid:
        return empid[0][0]
    return None

# Function to fetch employee ID from the crm_list table
def get_employe_usename(mydb, username):
    """
    Fetches an employee ID from the crm_list table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = f"SELECT username FROM crm_user WHERE username = '{username}'"
    username = fetch_data(query, mydb)
    
    if username:
        return username[0][0]
    return None

# Function to fetch employee ID from the crm_user table
def get_employe_user(mydb, employe_id):
    """
    Fetches an employee ID from the crm_user table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = f"SELECT employe_id FROM crm_user WHERE employe_id = '{employe_id}'"
    empid = fetch_data(query, mydb)
    
    if empid:
        return empid[0][0]
    return None

# Function to insert a new user into the crm_user table
def insert_crmuser(conn, cursor, employe_id, username, password):
    """
    Inserts a new user into the crm_user table in the MySQL server database.

    Args:
        conn: MySQL database connection object.
        cursor: MySQL database cursor object.
        employe_id: The employee ID of the new user.
        username: The username of the new user.
        password: The plain text password of the new user.

    Returns:
        True if the insertion is successful, False otherwise.
    """
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute("""
            INSERT INTO crm_user (employe_id, username, crm_password)
            VALUES (%s, %s, %s)
        """, (employe_id, username, hashed_password))
        conn.commit()
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False


def womenCustomer(conn, cursor, name, phone_number, Saving_Account, disbursed_Amount, remark):
    username = st.session_state.get("username", "")
    crm_id = get_id(conn, cursor, username)

    # # Debugging: Print types of variables
    # st.write(f"crm_id: {crm_id}, Type: {type(crm_id)}")
    # st.write(f"name: {name}, Type: {type(name)}")
    # st.write(f"phone_number: {phone_number}, Type: {type(phone_number)}")
    # st.write(f"Saving_Account: {Saving_Account}, Type: {type(Saving_Account)}")
    # st.write(f"disbursed_Amount: {disbursed_Amount}, Type: {type(disbursed_Amount)}")
    # st.write(f"remark: {remark}, Type: {type(remark)}")
    try:
        processed_phone_number = "+251" + phone_number[1:]
        
        cursor.execute("""
            INSERT INTO women_product_customer(crm_id, full_name, phone_number, account_no, disbursed_amount, remark)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (crm_id, name, processed_phone_number, Saving_Account, disbursed_Amount, remark))
        conn.commit()
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False


# Function to fetch employee ID from the crm_user table
def get_id(mydb, cursor, username):
    """
    Fetches an employee ID from the crm_user table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    if username in get_usernames(cursor):
        cursor.execute("SELECT userId FROM user_info WHERE userName = %s", (username,))
        result = cursor.fetchone()
    else:
        cursor.execute("SELECT crm_id FROM crm_user WHERE username = %s", (username,))
        result = cursor.fetchone()
    return result[0] if result else None


def get_unquiedureatphone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber. kiyya_customer
    """
    cursor.execute("SELECT phone_number FROM women_product_customer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone

def get_unquiedkiyyaphone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber. kiyya_customer
    """
    cursor.execute("SELECT phone_number FROM kiyya_customer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone

def get_unquiedkiyyaphone(cursor):
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber. kiyya_customer
    """
    cursor.execute("SELECT phone_number FROM kiyya_customer")
    phone = [user[0] for user in cursor.fetchall()]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone


def check_durationunique_account(cursor, account):
    """
    Checks if an account number exists in any of the specified tables with specific conditions.

    Args:
        cursor: MySQL database cursor.
        account: Account number to check.

    Returns:
        True if the account number exists in any of the tables, False otherwise.
    """
    # Retrieve account number from women_product_customer table
    cursor.execute("SELECT account_no FROM women_product_customer WHERE account_no = %s", (account,))
    result4 = cursor.fetchone()  # Only fetch one result, no need to fetch all

    # Retrieve saving account from unique_intersection table with specific product types
    cursor.execute("""
        SELECT saving_account FROM unique_intersection 
        WHERE saving_account = %s AND (product_type = 'Women Formal' OR product_type = 'Women Informal')
    """, (account,))
    result5 = cursor.fetchone()  # Fetch only one result

    # Retrieve saving account from conversiondata table with specific product types
    cursor.execute("""
        SELECT saving_account FROM conversiondata 
        WHERE saving_account = %s AND (product_type = 'Women Formal' OR product_type = 'Women Informal')
    """, (account,))
    result6 = cursor.fetchone()  # Fetch only one result

    # Retrieve account number from kiyya_customer table
    cursor.execute("SELECT account_number FROM kiyya_customer WHERE account_number = %s", (account,))
    result7 = cursor.fetchone()  # Fetch only one result

    # # Retrieve account number from branch_customer table  
    # cursor.execute("SELECT Saving_Account FROM branchcustomer WHERE Saving_Account = %s", (account,))
    # result8 = cursor.fetchone()  # Fetch only one result

    # Check if account number exists in any of the tables
    return result4 is not None or result5 is not None or result6 is not None or result7 is not None





def load_women_data(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # Fetch userId based on username
    if role == "CRM":
        crm_id_query = f"SELECT crm_id FROM crm_user WHERE username = '{username}'"
        crm_id_result = fetch_data(crm_id_query, mydb)
    else:
        crm_id_query = f"SELECT userId FROM user_info WHERE username = '{username}'"
        crm_id_result = fetch_data(crm_id_query, mydb)

    # Check if crm_id_result is empty
    if not crm_id_result:
        st.warning("No CRM ID found for the current user.")
        return pd.DataFrame(), pd.DataFrame()

    dureti_customer_query = f"SELECT * FROM women_product_customer WHERE crm_id = '{crm_id_result[0][0]}'and `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"


    dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), 
                                   columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date'])

    unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                   columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                       columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge DataFrames on 'Saving Account'
    unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
    conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

    # Select and concatenate the required columns
    unique_cust_by_crm = unique_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]
    conv_cust_by_crm = conv_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]

    combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
    # st.write(combined_cust_by_crm)

    # Perform a left join to identify customers only in dureti_customer
    merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['wpc_id', 'crm_id','Phone Number', 'Saving Account', 'remark'], how='left', indicator=True)
    # st.write(merged_df)

    # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
    crm_only = merged_df[merged_df['_merge'] == 'left_only']
    crm_cust_only = crm_only[['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']]

    return combined_cust_by_crm, crm_cust_only


def load_all_women_data(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # CRM user query
    crm_user_query = """
        SELECT dr.crm_id, br.full_name, br.sub_process 
        FROM crm_list br
        JOIN crm_user dr ON br.employe_id = dr.employe_id
        """
    crm_user_list = pd.DataFrame(fetch_data(crm_user_query, mydb), columns=['crm_id', 'Recruited by', 'Sub Process'])

    # Women product customer query
    women_customer_query = """
        SELECT dr.crm_id, br.full_Name, br.district 
        FROM user_info br
        JOIN women_product_customer dr ON br.userId = dr.crm_id
        """
    women_customer_list = pd.DataFrame(fetch_data(women_customer_query, mydb), columns=['crm_id', 'Recruited by', 'Sub Process'])

    # Combine user data
    combined_user = pd.concat([crm_user_list, women_customer_list], axis=0).drop_duplicates(subset=['crm_id'])

    # Queries for customer data
    dureti_customer_query = "SELECT * FROM women_product_customer WHERE `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal')"
    conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal')"

    # Fetching customer data
    dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), 
                                   columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date'])

    unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                   columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                       columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merging on 'Saving Account'
    unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
    conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

    # Select relevant columns
    unique_cust_by_crm = unique_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]
    conv_cust_by_crm = conv_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]

    # Combine unique and conversion customers
    combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()

    # Merge with user data
    combined_cust_by_crm_all = pd.merge(combined_cust_by_crm, combined_user, on='crm_id', how='inner')

    # Left join to identify customers only in dureti_customer
    merged_df = pd.merge(dureti_customer, combined_cust_by_crm, 
                         on=['wpc_id', 'crm_id', 'Phone Number', 'Saving Account', 'remark'], 
                         how='left', indicator=True)

    # Filter to keep rows only in dureti_customer
    crm_only = merged_df[merged_df['_merge'] == 'left_only']
    crm_cust_only = crm_only[['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']]
    
    # Merge CRM-only customers with user data
    crm_cust_only_all = pd.merge(crm_cust_only, combined_user, on='crm_id', how='inner')

    return combined_cust_by_crm_all, crm_cust_only_all




def kiyya_customer(conn, cursor, username, fullName, phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        userId  = get_id(conn, cursor, username)
        if userId:
            # Insert customer information into the customer table
            cursor.execute("""
                INSERT INTO kiyya_customer(userId, fullName, phone_number, account_number, customer_ident_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, daily_sales, purpose_of_loan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (userId, fullName, processed_phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan))
            conn.commit()
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False

def load_all_kiyya_data(mydb):
    # Access the username and role from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # CRM user query
    crm_user_query = """
        SELECT DISTINCT k.userId, br.full_name, br.sub_process 
        FROM crm_list br
        JOIN crm_user dr ON br.employe_id = dr.employe_id
        JOIN kiyya_customer k ON k.userId = dr.crm_id
        """
    crm_user_list = pd.DataFrame(fetch_data(crm_user_query, mydb), columns=['userId', 'Recruited by', 'Sub Process'])

    # Women product customer query
    women_customer_query = """
    SELECT DISTINCT dr.userId, br.full_Name, br.district 
    FROM user_info br
    JOIN kiyya_customer dr ON br.userId = dr.userId
    """
    women_customer_list = pd.DataFrame(fetch_data(women_customer_query, mydb), columns=['userId', 'Recruited by', 'Sub Process'])

    # Combine user data
    combined_user = pd.concat([crm_user_list, women_customer_list], axis=0).drop_duplicates(subset=['userId']).reset_index(drop=True).rename(lambda x: x + 1)
  

    # Queries for customer data
    keyya_customer_query = "SELECT * FROM kiyya_customer where userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' and `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal')"
    conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal')"

    # Fetching customer data
    dureti_customer = pd.DataFrame(fetch_data(keyya_customer_query, mydb), 
                                   columns=['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])
    unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                   columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                       columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge DataFrames on 'Saving Account'
    unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
    conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

    # Select and concatenate the required columns
    unique_cust_by_crm = unique_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    conv_cust_by_crm = conv_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    # Combine unique and conversion customers
    combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1)
    
    
    

    # Merge with user data
    combined_cust_by_crm_all = pd.merge(combined_cust_by_crm, combined_user, on='userId', how='inner')
  

    # Left join to identify customers only in dureti_customer
    merged_df = pd.merge(dureti_customer, combined_cust_by_crm, 
                         on=['kiyya_id', 'userId','Phone Number', 'Saving Account'], 
                         how='left', indicator=True)

    # Filter to keep rows only in dureti_customer
    crm_only = merged_df[merged_df['_merge'] == 'left_only']
    crm_cust_only = crm_only[['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']]

    # Merge CRM-only customers with user data
    crm_cust_only_all = pd.merge(crm_cust_only, combined_user, on='userId', how='inner')

    return combined_cust_by_crm_all, crm_cust_only_all


def load_kiyya_data(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # Fetch userId based on username
    if role == "CRM":
        crm_id_query = f"SELECT crm_id FROM crm_user WHERE username = '{username}'"
        crm_id_result = fetch_data(crm_id_query, mydb)
    else:
        crm_id_query = f"SELECT userId FROM user_info WHERE username = '{username}'"
        crm_id_result = fetch_data(crm_id_query, mydb)

    # Check if crm_id_result is empty
    if not crm_id_result:
        st.warning("No CRM ID found for the current user.")
        return pd.DataFrame(), pd.DataFrame()

    dureti_customer_query = f"SELECT * FROM kiyya_customer WHERE userId = '{crm_id_result[0][0]}' and `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"


    dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), 
                                   columns = ['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])

    unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                   columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                       columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    # Merge DataFrames on 'Saving Account'
    unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
    conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

    # Select and concatenate the required columns
    unique_cust_by_crm = unique_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount',  'Disbursed Date']]
    conv_cust_by_crm = conv_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]

    combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
    # st.write(combined_cust_by_crm)

    # Perform a left join to identify customers only in dureti_customer
    merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['kiyya_id', 'userId','Phone Number', 'Saving Account'], how='left', indicator=True)
    # st.write(merged_df)

    # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
    crm_only = merged_df[merged_df['_merge'] == 'left_only']
    crm_cust_only = crm_only[['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity', 'Woreda', 'Register Date']]

    return combined_cust_by_crm, crm_cust_only


def load_kiyya_branch_data(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    if role == 'District User':
        # Fetch the user's district
        user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_district = fetch_data(user_query, mydb)

        # Check if a district was found for the user
        if not user_district or len(user_district) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district value from the query result
        district_value = user_district[0][0]

        # Fetch userIds for the corresponding district
        crm_id_query = f"SELECT userId FROM user_info WHERE district = '{district_value}'"
        crm_id_result = fetch_data(crm_id_query, mydb)

        # Check if any userIds were found
        if not crm_id_result or len(crm_id_result) == 0:
            st.warning("No user IDs found for the district.")
            return pd.DataFrame(), pd.DataFrame()

        # Extract the userIds from the result
        crm_ids = [str(row[0]) for row in crm_id_result]

        # Construct the query for the kiyya_customer table using the userIds
        crm_id_list = "', '".join(crm_ids)
        dureti_customer_query = f"SELECT * FROM kiyya_customer WHERE userId IN ('{crm_id_list}') and `registered_date` >= '2024-10-01'"

        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"


        dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), 
                                    columns = ['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])

        unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount',  'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        # st.write(combined_cust_by_crm)

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['kiyya_id', 'userId','Phone Number', 'Saving Account'], how='left', indicator=True)
        # st.write(merged_df)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity', 'Woreda', 'Register Date']]

        return combined_cust_by_crm, crm_cust_only
    else:
        st.warning("User is not a District User.")
        return pd.DataFrame(), pd.DataFrame()

def load_formal_branch_data(mydb):
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    if role == 'District User':
        # Fetch the user's district
        user_query = f"SELECT district FROM user_info WHERE userName = '{username}'"
        user_district = fetch_data(user_query, mydb)

        # Check if a district was found for the user
        if not user_district or len(user_district) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district value from the query result
        district_value = user_district[0][0]

        # Fetch userIds for the corresponding district
        crm_id_query = f"SELECT userId FROM user_info WHERE district = '{district_value}'"
        crm_id_result = fetch_data(crm_id_query, mydb)

        # Check if any userIds were found
        if not crm_id_result or len(crm_id_result) == 0:
            st.warning("No user IDs found for the district.")
            return pd.DataFrame(), pd.DataFrame()

        # Extract the userIds from the result
        crm_ids = [str(row[0]) for row in crm_id_result]

        # Construct the query for the kiyya_customer table using the userIds
        crm_id_list = "', '".join(crm_ids)
        dureti_customer_query = f"SELECT * FROM women_product_customer WHERE crm_id IN ('{crm_id_list}') and `registered_date` >= '2024-10-01'"
        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"


        dureti_customer = pd.DataFrame(fetch_data(dureti_customer_query, mydb), 
                                    columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date'])

        unique_customer = pd.DataFrame(fetch_data(unique_customer_query, mydb), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(fetch_data(conversion_customer_query, mydb), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        # st.write(combined_cust_by_crm)

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['wpc_id', 'crm_id','Phone Number', 'Saving Account', 'remark'], how='left', indicator=True)
        # st.write(merged_df)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']]

        return combined_cust_by_crm, crm_cust_only
    else:
        st.warning("User is not a District User.")
        return pd.DataFrame(), pd.DataFrame()


def load_kiyya_report_data(mydb):
    

    # df_user_info = pd.DataFrame(fetch_data(f"SELECT * FROM user_info WHERE userId = '{user_id}'", mydb), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role', 'password', 'ccreatedAt'])
    # Filtered queries for data starting from July 1
    keyya_customer_query = f"SELECT * FROM kiyya_customer"
    
    kiyya_customer = pd.DataFrame(fetch_data(keyya_customer_query, mydb), columns=['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])
    

    return kiyya_customer








def create_record(mydb, name, email):
    cursor = mydb.cursor()
    sql = "INSERT INTO users(name, email) VALUES (%s, %s)"
    val = (name, email)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()

def read_records(mydb):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    return result

def update_record(mydb, id, name, email):
    cursor = mydb.cursor()
    sql = "UPDATE users SET name=%s, email=%s WHERE id=%s"
    val = (name, email, id)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()

def delete_record(mydb, id):
    cursor = mydb.cursor()
    sql = "DELETE FROM users WHERE id=%s"
    val = (id,)
    cursor.execute(sql, val)
    mydb.commit()
    cursor.close()
