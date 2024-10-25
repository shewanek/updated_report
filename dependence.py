import pandas as pd
import streamlit as st
import hashlib
import re
import json
import numpy as np
from decimal import Decimal
from datetime import date, datetime
from db_connection import DatabaseOperations


        
# Initialize DatabaseOperations once
db_ops = DatabaseOperations()
def load_dataframes():
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"
    # Fetch data with JOIN to get branch name from branch_list table
    query = """
    SELECT ui.userId, ui.userName, ui.district, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """
    # Fetch data and create DataFrame
    df_user_infoss = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'userName', 'District', 'Branch'])

    # df_user_infoss = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infoss"), columns=['userId','userName','District','Branch'])
    df_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), columns=['customerId', 'userId','full Name', 'Product Type','Phone Number','Saving Account', 'Region', 'Zone/sub city/ Woreda','Register Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infoss, df_customer, on='userId', how='inner')
    
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/sub city/ Woreda', 'Register Date']]
    
    return df_combine

@st.cache_data
def load_unquie(role, usrname):
    query = """
    SELECT d.district_name, bl.branch_code, bl.branch_name
    FROM branch_list bl
    JOIN district_list d ON bl.dis_Id = d.dis_Id
    """

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine
@st.cache_data
def load_unquiecustomer(role, username):
    query = """
    SELECT ui.userId, ui.userName, ui.district, branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    branch_customer = pd.DataFrame(db_ops.fetch_data(branch_customer_query))
    branch_customer.columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    # Step 1: Identify rows in branch_customer that are not in df_customer
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]

    # Step 2: Merge the result with df_user_infos to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_infos, on='userId', how='inner')

    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

    # Now registed_by_branch will contain only the rows from branch_customer that were not found in df_customer

    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine



def load_convertion():
    query = """
    SELECT ui.userId, ui.userName, ui.district, branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM conversiondata WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), columns=['ConversionId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['ConversionId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine


def load_branchdata(username, page=1, page_size=1000):
    try:
        # Calculate the offset based on the current page and page size
        offset = (page - 1) * page_size

        # Fetch userId based on username
        user_id_query = "SELECT userId, district FROM user_infos WHERE userName = %s"
        user_id_result = db_ops.fetch_data(user_id_query, (username,))

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame(), 0  # Return an empty DataFrame if no user is found

        user_id = user_id_result[0]['userId']
        district = user_id_result[0]['district']

        # Fetch user_infos with selected columns
        query = """
        SELECT ui.userId, ui.userName, ui.district, ui.branch, bl.branch_name
        FROM user_infos ui
        JOIN branch_list bl ON ui.branch = bl.branch_code
        WHERE ui.userId = %s
        """
        df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (user_id,)), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])

        # Ensure 'branch_code' is a string
        df_user_infos['branch_code'] = df_user_infos['branch_code'].astype(str)

        # Fetch paginated data from different tables
        dureti_customer_query = f"""
        SELECT uniqId, userId, full Name, Product_Type, Phone Number, Saving Account, Region, Zone/Subcity/Woreda, Register Date 
        FROM duretCustomer 
        WHERE `Register_Date` >= '2024-07-01' 
        LIMIT {page_size} OFFSET {offset}
        """
        unique_customer_query = f"""
        SELECT uniqId, branch_code, Customer Number, Customer Name, Saving Account, Product Type, Disbursed Amount, Disbursed Date 
        FROM unique_intersection 
        WHERE `disbursed_date` >= '2024-07-01' 
        LIMIT {page_size} OFFSET {offset}
        """
        conversion_customer_query = f"""
        SELECT conId, branch_code, Customer Number, Customer Name, Saving Account, Product Type, Disbursed Amount, Disbursed Date 
        FROM conversiondata 
        WHERE `disbursed_date` >= '2024-07-01' 
        LIMIT {page_size} OFFSET {offset}
        """
        branch_customer_query = f"""
        SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name, Disbursed_date 
        FROM branchcustomer 
        LIMIT {page_size} OFFSET {offset}
        """

        # Fetch paginated data
        dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query))
        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
        branch_customer = pd.DataFrame(db_ops.fetch_data(branch_customer_query))

        # Ensure branch_code is string in relevant DataFrames
        unique_customer['branch_code'] = unique_customer['branch_code'].astype(str)
        conversion_customer['branch_code'] = conversion_customer['branch_code'].astype(str)

        # Perform the merge operation on paginated data
        merged_df_1 = pd.merge(df_user_infos, dureti_customer, on='userId', how='inner')
        merged_df_2 = pd.merge(df_user_infos, unique_customer, on='branch_code', how='inner')
        merged_df_3 = pd.merge(df_user_infos, conversion_customer, on='branch_code', how='inner')

        # Merge branch_customer with other data
        branch_customer['branch_code'] = branch_customer['userId'].astype(str)
        unique_by_branch = pd.merge(branch_customer, unique_customer, on='Saving Account', how='inner')
        unique_cust_by_branch = unique_by_branch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

        # Perform a right join
        merged_df = pd.merge(unique_customer, branch_customer, on='Saving Account', how='left', indicator=True)
        unique_by_self = merged_df[merged_df['_merge'] == 'left_only']
        unique_cust_by_self = pd.merge(unique_by_self, df_user_infos, on='branch_code', how='inner')
        unique_cust_by_self = unique_cust_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]

        # Return paginated data
        return merged_df_1, merged_df_2, merged_df_3, unique_cust_by_branch, unique_cust_by_self, len(branch_customer)
    
    except Exception as e:
        st.error("Failed to load your branch data.")
        st.exception(e)
        return None, None, None, None, None, 0



def load_districtduretidata():
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_infos WHERE userName = '{username}'"
    user_id_result = db_ops.fetch_data(user_id_query)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]
    # district ["Centeral Finfinne", "East Finfinne", "Western Finfinne"]

    # Fetch data from user_infos and duretCustomer tables based on userId
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_name, ui.role
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = '{district}'
    """
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role'])

    # df_user_infos = pd.DataFrame(db_ops.fetch_data(f"SELECT * FROM user_infos WHERE district = '{district}'"), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role', 'password', 'ccreatedAt'])
    df_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), columns=['customerId', 'userId', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date'])

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='userId', how='inner')

    # Select specific columns for the combined DataFrame
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date']]

    return df_combine

@st.cache_data
def load_districtuniquedata(username):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = "SELECT district FROM user_infos WHERE userName = %s"
    user_id_result = db_ops.fetch_data(user_id_query,(username,))

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0]['district']  # Assuming userId is the first element in the first row of the result
    # district = user_id_result[0][1]
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `disbursed_date` >= '2024-07-01'"
    query = """
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = %s
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (district,)))
    df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])

    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    branch_customer = pd.DataFrame(db_ops.fetch_data(branch_customer_query))
    branch_customer.columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    # Step 1: Identify rows in branch_customer that are not in df_customer
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]

    # Step 2: Merge the result with df_user_infos to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_infos, on='userId', how='inner')

    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]
    # st.write(registed_by_branch)
    # Now registed_by_branch will contain only the rows from branch_customer that were not found in df_customer

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    df_combine = merged_df[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    # st.write(unique_cust_by_branch)
    # st.write(unique_cust_by_self) 
    # st.write(registed_by_branch)
    # st.write(df_combine)
    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine


def load_districtconversiondata():
    # Access the username from session state
    username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = f"SELECT  district FROM user_infos WHERE userName = '{username}'"
    user_id_result = db_ops.fetch_data(user_id_query)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    # district = user_id_result[0][1]
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE `disbursed_date` >= '2024-07-01'"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_code, bl.branch_name, ui.role
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = '{district}'
    """
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'full_Name', 'userName', 'District', 'branch_code', 'Branch', 'role'])
    
    # df_user_infos = pd.DataFrame(db_ops.fetch_data(f"SELECT * FROM user_infos WHERE district = '{district}'"), columns=['userId', 'full_Name','userName','District','Branch','role','password','ccreatedAt'])
    df_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), columns=['convId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['convId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    return df_combine


def aggregate_and_insert_actual_data():
    # Fetch the latest disbursed_date from unique_intersection and conversiondata tables
    latest_disbursed_query = """
        SELECT MAX(disbursed_date) as disbursed_date
        FROM (
            SELECT disbursed_date FROM unique_intersection
            UNION
            SELECT disbursed_date FROM conversiondata
        ) AS combined_dates
    """
    latest_disbursed_dates = db_ops.fetch_one(latest_disbursed_query)
    latest_disbursed_date = latest_disbursed_dates['disbursed_date']
    # st.write(latest_disbursed_date)
    
    # Check if this date already exists in the actual table
    check_date_query = """
        SELECT MAX(actual_date) as actual_date FROM actual WHERE actual_date = %s
    """
    # Fetch the result, assuming db_ops.fetch_one returns a tuple like (1,) or (0,)
    # Fetch the result and access the first element to get 1 if exists, 0 if not
    date_exists = db_ops.fetch_one(check_date_query, (latest_disbursed_date,))
    # st.write(date_exists)

    # Now date_exists will be 1 if the date exists or 0 if it does not exist
    if date_exists['actual_date']:
        # st.warning("The latest disbursed date is already present in the actual table.")
        return
    # Fetch the disbursed_date from both tables to ensure they are equal
    date_check_query = """
        SELECT
            (SELECT disbursed_date FROM unique_intersection WHERE disbursed_date = %s LIMIT 1) AS unique_date,
            (SELECT disbursed_date FROM conversiondata WHERE disbursed_date = %s LIMIT 1) AS conversion_date
    """
    date_check = db_ops.fetch_data(date_check_query, (latest_disbursed_date, latest_disbursed_date))
    
    unique_date = date_check[0]['unique_date']
    conversion_date = date_check[0]['conversion_date']
    # st.write(unique_date)
    # st.write(conversion_date)
    
    if unique_date != conversion_date:
        # st.warning("The disbursed_date in unique_intersection does not match the disbursed_date in conversiondata.")
        return
    
    # Fetch data from unique_intersection and conversiondata tables where disbursed_date is the latest
    unique_query = """
        SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, uni_id
        FROM unique_intersection
        WHERE disbursed_date = %s
    """
    conversion_query = """
        SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, conv_id
        FROM conversiondata
        WHERE disbursed_date = %s
    """
    
    unique_data = db_ops.fetch_data(unique_query, (latest_disbursed_date,))
    conversion_data = db_ops.fetch_data(conversion_query, (latest_disbursed_date,))
    
    # Convert fetched data to DataFrames
    unique_df = pd.DataFrame(unique_data)
    unique_df.columns=['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date', 'uni_id']
    conversion_df = pd.DataFrame(conversion_data)
    conversion_df.columns=['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date', 'conv_id']
    
    # Concatenate both DataFrames
    combined_df = pd.concat([unique_df, conversion_df])
    
    if combined_df.empty:
        st.warning("No data found in unique_intersection or conversiondata tables for the latest disbursed_date.")
        return

    # Group by branch_code and aggregate the required columns
    aggregated_df = combined_df.groupby('branch_code').agg(
        unique_actual=('uni_id', 'nunique'),
        account_actual=('saving_account', 'count'),
        disbursment_actual=('disbursed_amount', 'sum'),
        actual_date=('disbursed_date', 'first')
    ).reset_index()
    # st.write(aggregated_df)
    # Insert aggregated data into the actual table
    for index, row in aggregated_df.iterrows():
        # Check if this branch_code and actual_date already exist in the actual table
        check_record_query = """
            SELECT MAX(actual_date) as actual_date FROM actual 
                WHERE branch_code = %s AND actual_date = %s
        """
        # db_ops.fetch_one(check_record_query, (row['branch_code'], row['actual_date']))
        record_exists = db_ops.fetch_one(check_record_query, (row['branch_code'], row['actual_date']))
        
        if not record_exists['actual_date']:
            # Insert the new record only if it doesn't already exist
            querry = """
                INSERT INTO actual (branch_code, unique_actual, account_actual, disbursment_actual, actual_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            db_ops.insert_data(querry, (row['branch_code'], row['unique_actual'], row['account_actual'], row['disbursment_actual'], row['actual_date']))
    
    


# @st.cache_data
def load_actual_vs_targetdata(role, username):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        try:
            # Fetch districts from user_infos
            aggregate_and_insert_actual_data()
            user_id_query = "SELECT district FROM user_infos"
            district_result = db_ops.fetch_data(user_id_query)

            if not district_result:
                st.warning("No users found.")
                return pd.DataFrame()  # Return an empty DataFrame if no users are found

            # Extract only the district names from the result
            districts = [item['district'] for item in district_result if item.get('district')]

            if not districts:
                st.warning("No valid district names found.")
                return pd.DataFrame()

            # Convert the list of districts to a tuple for parameterized query
            districts_tuple = tuple(districts) if len(districts) > 1 else (districts[0],)

            # Create the SQL query with placeholders for each district
            district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name IN ({', '.join(['%s'] * len(districts_tuple))})"

            # Fetch data with parameterized query
            district_result = db_ops.fetch_data(district_query, districts_tuple)
            # st.write(district_result)
            # Check if any districts were found
            if not district_result:
                st.warning("No district found with the given district names.")
                return pd.DataFrame()  # Return an empty DataFrame if no districts are found

            # Extract dis_Id values from the district query result
            dis_ids = [row['dis_Id'] for row in district_result]  # Assuming result is a dictionary with 'dis_Id' as a key

            # If no valid dis_ids, warn and return
            if not dis_ids:
                st.warning("No valid district IDs found.")
                return pd.DataFrame()

            # Convert the list of dis_ids to a tuple for parameterized SQL query
            dis_ids_tuple = tuple(dis_ids) if len(dis_ids) > 1 else (dis_ids[0],)

            # Fetch branch code and branch name using a parameterized query
            branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id IN ({', '.join(['%s'] * len(dis_ids_tuple))})"
            branch_code_result = db_ops.fetch_data(branch_code_query, dis_ids_tuple)
            # st.write(branch_code_result)

            # Check if branch information was found
            if not branch_code_result:
                st.warning("No branches found for the given districts.")
                return pd.DataFrame()  # Return an empty DataFrame if no branches are found
            # Assuming district_result and branch_code_result return dictionaries with relevant keys
            actul_dis = pd.DataFrame(district_result)  # Use 'district_name' from the result
            actul_dis.columns = ['dis_Id', 'District']
            actual_branch = pd.DataFrame(branch_code_result)
            actual_branch.columns = ['dis_Id', 'Branch Code', 'Branch']
            # st.write(actual_branch)
            # Merge DataFrames based on 'dis_Id'
            act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')

            # Display the merged DataFrame
            # Helper function to convert Decimal to float
            def convert_decimal(value):
                if isinstance(value, Decimal):
                    return float(value)
                return value

            # Helper function to convert date types to string
            def convert_date(value):
                if isinstance(value, (date, datetime)):
                    return value.strftime('%Y-%m-%d')
                return value

            # Extract branch codes from the result
            branch_codes = [row['branch_code'] for row in branch_code_result if 'branch_code' in row]  # Ensure the key exists

            # If no valid branch codes, warn and return
            if not branch_codes:
                st.warning("No valid branch codes found.")
                return pd.DataFrame()  # or return None if you prefer

            # Create the SQL query with the correct number of placeholders
            placeholders = ', '.join(['%s'] * len(branch_codes))  # Create placeholders for the number of branch codes
            actual_query = f"""
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date 
                FROM actual 
                WHERE branch_code IN ({placeholders})
            """

            # Fetch actual data using a parameterized query
            fetch_actual = db_ops.fetch_data(actual_query, tuple(branch_codes))  # Ensure the tuple is passed correctly
            # Debugging: Print the raw data fetched
            # st.write("Actual Data Fetched:", fetch_actual)

            # Check if fetch_actual has data
            if not fetch_actual:
                st.warning("No actual data found for the selected branch codes.")
                return pd.DataFrame()

            # Convert the data to a DataFrame and handle data type conversions
            df_actual = pd.DataFrame(fetch_actual)
            # Rename columns for 'actual' data
            df_actual.columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
            # Apply data type conversions
            df_actual['Actual Unique Customer'] = df_actual['Actual Unique Customer'].apply(convert_decimal)
            df_actual['Actual Number Of Account'] = df_actual['Actual Number Of Account'].apply(convert_decimal)
            df_actual['Actual Disbursed Amount'] = df_actual['Actual Disbursed Amount'].apply(convert_decimal)
            df_actual['Actual Date'] = df_actual['Actual Date'].apply(convert_date)
            df_actual['created_date'] = df_actual['created_date'].apply(convert_date)
            # st.write(df_actual)
            
            # Fetch target data
            target_query = """
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date 
                FROM target
            """
            fetch_target = db_ops.fetch_data(target_query)
            # st.write(fetch_target)
            df_target = pd.DataFrame(fetch_target)
            # Rename columns for 'target' data
            df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
            # Apply data type conversions
            df_target['Target Unique Customer'] = df_target['Target Unique Customer'].apply(convert_decimal)
            df_target['Target Number Of Account'] = df_target['Target Number Of Account'].apply(convert_decimal)
            df_target['Target Disbursed Amount'] = df_target['Target Disbursed Amount'].apply(convert_decimal)
            df_target['Target Date'] = df_target['Target Date'].apply(convert_date)
            df_target['created_date'] = df_target['created_date'].apply(convert_date)

            # st.write(df_target)
           

            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


    elif role == "Sales Admin":
        try:
            # Fetch district for the Sales Admin based on their username
            district_query = "SELECT district FROM user_infos WHERE userName = %s"
            district_result = db_ops.fetch_data(district_query, (username,))
            
            if not district_result:
                st.warning("No users found.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames if no users found

            district = district_result[0]['district']
            
            # Handle JSON-encoded district data
            if isinstance(district, str):
                try:
                    districts = json.loads(district)
                except json.JSONDecodeError:
                    districts = [district]  # If not JSON-encoded, treat it as a single district
            else:
                districts = [district]

            # Use placeholders for parameterized queries
            placeholders = ', '.join(['%s'] * len(districts))

            # Fetch dis_Id for the districts
            district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name IN ({placeholders})"
            district_result = db_ops.fetch_data(district_query, tuple(districts))
            
            if not district_result:
                st.warning("No districts found with the given district names.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames if no districts found

            dis_ids = [row['dis_Id'] for row in district_result]

            # Fetch branch code and branch name for the dis_ids
            branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id IN ({placeholders})"
            branch_code_result = db_ops.fetch_data(branch_code_query, tuple(dis_ids))
            
            if not branch_code_result:
                st.warning("No branches found for the given districts.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames if no branches found

            # Extract branch codes from the result
            branch_codes = [row['branch_code'] for row in branch_code_result]
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))

            # Create DataFrames for district and branch information
            actul_dis = pd.DataFrame(district_result)
            actul_dis.columns=['dis_Id', 'District']
            actual_branch = pd.DataFrame(branch_code_result)
            actual_branch.columns=['dis_Id', 'Branch Code', 'Branch']

            # Merge district and branch DataFrames based on 'dis_Id'
            act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')
            # st.write(act_dis_branch)

            # Fetch actual data
            actual_query = f"""
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date 
                FROM actual WHERE branch_code IN ({branch_codes_str})
            """
            df_actual = pd.DataFrame(db_ops.fetch_data(actual_query, tuple(branch_codes)))
            df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
            # st.write(df_actual)

            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date 
                FROM target WHERE branch_code IN ({branch_codes_str})
            """
            df_target = pd.DataFrame(db_ops.fetch_data(target_query, tuple(branch_codes)))
            df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
            # st.write(df_target)

            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    elif role == "Branch User":
        try:
            # Fetch branch and district for the given username
            user_id_query = "SELECT branch, district FROM user_infos WHERE userName = %s"
            user_id_result = db_ops.fetch_data(user_id_query, (username,))

            if not user_id_result:
                st.warning("No user found with the given username.")
                return pd.DataFrame()  # Return an empty DataFrame if no user is found

            branch = user_id_result[0]['branch']  # Assuming branch is the first element in the first row of the result
            district = user_id_result[0]['district']

            # Fetch branch code and branch name
            branch_code_query = "SELECT branch_code, branch_name FROM branch_list WHERE branch_code = %s"
            branch_code_result = db_ops.fetch_data(branch_code_query, (branch,))

            if not branch_code_result:
                st.warning("No branch found with the given branch name.")
                return pd.DataFrame()  # Return an empty DataFrame if no branch is found

            branch_code = branch_code_result[0]['branch_code']

            # Create DataFrames from the fetched data
            actul_dis = pd.DataFrame(user_id_result)
            actul_dis.columns=['Branch Code', 'District']
            actual_branch = pd.DataFrame(branch_code_result)
            actual_branch.columns=['Branch Code', 'Branch']

            # Merge DataFrames based on 'branch'
            act_dis_branch = pd.merge(actul_dis, actual_branch, on='Branch Code', how='inner')
            # st.write(act_dis_branch)

            # Fetch actual data
            actual_query = """
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date 
                FROM actual 
                WHERE branch_code = %s
            """
            df_actual = pd.DataFrame(db_ops.fetch_data(actual_query, (branch_code,)))
            df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']

            # Fetch target data
            target_query = """
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date 
                FROM target 
                WHERE branch_code = %s
            """
            df_target = pd.DataFrame(db_ops.fetch_data(target_query, (branch_code,)))
            df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']

            
            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    else:
        try:
            # Fetch district for the given username
            user_id_query = "SELECT district FROM user_infos WHERE userName = %s"
            user_id_result = db_ops.fetch_data(user_id_query, (username,))

            if not user_id_result:
                st.warning("No user found with the given username.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            # district = user_id_result[0][0]  # Assuming district is the first element in the first row of the result
            district = user_id_result[0]['district']

            # Fetch dis_Id for the district
            district_query = "SELECT dis_Id, district_name FROM district_list WHERE district_name = %s"
            district_result = db_ops.fetch_data(district_query, (district,))
            if not district_result:
                st.warning("No district found with the given district name.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()   # Return an empty DataFrame if no district is found

            dis_id = district_result[0]['dis_Id']

            # Fetch branch code and branch name
            branch_code_query = "SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id = %s"
            branch_code_result = db_ops.fetch_data(branch_code_query, (dis_id,))
            if not branch_code_result:
                st.warning("No branches found for the given district.")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()  # Return an empty DataFrame if no branches are found

            # Extract branch codes from the result
            branch_codes = [row['branch_code'] for row in branch_code_result]
            # branch_code = [f"'{row['branch_code']}'" for row in branch_code_result]  # Get all branch codes from the query result and quote them
            # branch_codes_str = ','.join(f"'{code}'" for code in branch_code)  # Prepare for SQL IN clause
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))


            # Create DataFrames from the fetched data
            actul_dis = pd.DataFrame(district_result)
            actul_dis.columns=['dis_Id', 'District']
            actual_branch = pd.DataFrame(branch_code_result)
            actual_branch.columns=['dis_Id', 'Branch Code', 'Branch']

            # Merge DataFrames based on 'dis_Id'
            act_dis_branch = pd.merge(actul_dis, actual_branch, on='dis_Id', how='inner')
            # st.write(act_dis_branch)

            # Fetch actual data using parameterized query
            actual_query = f"""
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date 
                FROM actual 
                WHERE branch_code IN ({branch_codes_str})
            """
            df_actual = pd.DataFrame(db_ops.fetch_data(actual_query, tuple(branch_codes)))
            # st.write(df_actual)
            df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']

            # Fetch target data using parameterized query
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date 
                FROM target 
                WHERE branch_code IN ({branch_codes_str})
            """
            df_target = pd.DataFrame(db_ops.fetch_data(target_query, tuple(branch_codes)))
            df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']

            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()





def load_salesduretidata():
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_infos WHERE userName = '{username}'"
    user_id_result = db_ops.fetch_data(user_id_query)

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
    # query = f"SELECT * FROM user_infos WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_name, ui.role
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    dureti_customer_query = f"SELECT * FROM duretCustomer WHERE `Register_Date` >= '2024-07-01'"

    # Fetch data from user_infos and duretCustomer tables based on userId
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role'])
    df_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), columns=['customerId', 'userId', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date'])

    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='userId', how='inner')

    # Select specific columns for the combined DataFrame
    df_combine = merged_df[['customerId', 'userName', 'District', 'Branch', 'Product Type', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity/Woreda', 'Register Date']]

    return df_combine

def load_salesuniquedata():
    # Access the username from session state
    username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = f"SELECT  district FROM user_infos WHERE userName = '{username}'"
    user_id_result = db_ops.fetch_data(user_id_query)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    # Parse the JSON format district
    districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{district}'" for district in districts)


    # SQL query using the IN clause
    # query = f"SELECT * FROM user_infos WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'userName', 'District', 'branch_code', 'Branch'])
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

    branch_customer = pd.DataFrame(db_ops.fetch_data(branch_customer_query), columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date'])

    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']]

    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    # Filter to keep only rows that are only in df_customer
    unique_byself = merged_df[merged_df['_merge'] == 'left_only']
    unique_by_self = pd.merge(unique_byself, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_self = unique_by_self[['District', 'Branch', 'Customer Number', 'Customer Name', 'Product Type', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
    
    # Using a left join and filtering for rows without a match in df_customer
    missing_in_df_customer = branch_customer[~branch_customer['Saving Account'].isin(df_customer['Saving Account'])]
    # Step 2: Merge the result with df_user_infos to get additional details
    result_with_details = pd.merge(missing_in_df_customer, df_user_infos, on='userId', how='inner')
    # Step 3: Select the desired columns for display
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)', 'Disbursed_Date']]

    # Merge the two DataFrames based on 'userId'
    merged_df_uni = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df_uni[['uniqueId', 'userName', 'District', 'Branch', 'Customer Number', 'Product Type', 'Customer Name', 'Saving Account', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    

    return unique_cust_by_branch, unique_cust_by_self, registed_by_branch, df_combine

def load_salesconversiondata():
    # Access the username from session state
    username = st.session_state.get("username", "")

    # Fetch userId based on username
    user_id_query = f"SELECT userId, district FROM user_infos WHERE userName = '{username}'"
    user_id_result = db_ops.fetch_data(user_id_query)

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    user_id = user_id_result[0][0]  # Assuming userId is the first element in the first row of the result
    district = user_id_result[0][1]
    # Parse the JSON format district
    districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    districts_str = ', '.join(f"'{district}'" for district in districts)
    # query = f"SELECT * FROM user_infos WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.full_Name, ui.userName, ui.district, bl.branch_code, bl.branch_name, ui.role
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({districts_str})
    """
    conversion_customer_query = f"SELECT * FROM conversiondata WHERE `Disbursed_Date` >= '2024-07-01'"

    df_user_infos = pd.DataFrame(db_ops.fetch_data(query), columns=['userId', 'full_Name','userName','District', 'branch_code', 'Branch','role'])
    df_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), columns=['ConversionId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['ConversionId', 'userName', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    
    return df_combine

def load_resetpassword():
    df_combine = pd.DataFrame(db_ops.fetch_data("SELECT * FROM reset_user_password"))
    df_combine.columns=['ResetId', 'user_Id', 'user name','full Name','outlook email','District/Branch','Asked Date']
    
    return df_combine


def insert_user(fullName, username, district, branch, role, password):
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
    query1 = "SELECT branch_code FROM branch_list WHERE branch_name = %s"
    resultt = db_ops.fetch_one(query1, (branch,))
    if resultt is None:
        # st.warning("Branch not found in the database. Setting branch to NULL.")
        branch_code = None
    else:
        branch_code = resultt['branch_code']

    # Fetch role_id
    query2 = "SELECT role_Id FROM role_list WHERE role = %s"
    result = db_ops.fetch_one(query2, (role,))
    if result is None:
        st.error("Role not found in the database.")
        return False
    role_id = result['role_Id']

    try:
        query3 = """
            INSERT INTO user_infos (full_Name, userName, district, branch, role, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db_ops.insert_data(query3, (fullName, username, district, branch_code, role_id, hashed_password))
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False

def insert_customer(conn, cursor, username, fullName, Product_Type, phone_number, Saving_Account, Region, Woreda):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_infos table using the provided username
        cursor.execute("SELECT userId FROM user_infos WHERE username = %s", (username,))
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
def insert_resetpuser(username, name, outlook_email, branch_name):
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
    if username in get_usernames():
        query1 = "SELECT userId FROM user_infos WHERE username = %s"
        result = db_ops.fetch_one(query1, (username,))
        user_id = result['userId']
    else:
        query2 = "SELECT crm_id FROM crm_user WHERE username = %s"
        result = db_ops.fetch_one(query2, (username,))
        user_id = result['crm_id']

    try:
        query3 = """
            INSERT INTO reset_user_password (`user_Id`,`user name`, `full Name`, `outlook email`, `District/Branch`)
            VALUES (%s, %s, %s, %s, %s)
        """
        db_ops.insert_data(query3, (user_id, username, name, outlook_email, branch_name))
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False
    

def conversion_customer(conn, cursor, username, fullName, Product_Type, phone_number, Saving_Account, collected_Amount, amount_borrowed_again,remark):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        # Retrieve userId from user_infos table using the provided username
        cursor.execute("SELECT userId FROM user_infos WHERE username = %s", (username,))
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
        # Retrieve userId from user_infos table using the provided username
        cursor.execute("SELECT userId FROM user_infos WHERE username = %s", (username,))
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

def get_usernames():
    """
    Fetches a list of usernames from the MySQL server database.

    Returns:
        A list of user usernames.
    """
    try:
        query = "SELECT username FROM user_infos"
        usernames = [user['username'] for user in db_ops.fetch_data(query)]  # Fetch data and extract usernames
        return usernames
    except Exception as e:
        st.error("Failed to get username")
        st.exception(e)

def get_crmusernames():
    """
    Fetches a list of usernames from the MySQL server database.

    Returns:
        A list of user usernames.
    """
    try:
        query = "SELECT username FROM crm_user"
        usernames = [user['username'] for user in db_ops.fetch_data(query)]  # Fetch data and extract usernames
        return usernames
    except Exception as e:
        st.error("Failed to get username")
        st.exception(e)

def get_password_by_username(username):
    """
    Fetches the hashed password associated with a given username.

    Args:
        username: The username to fetch the password for.

    Returns:
        The hashed password if the username exists, None otherwise.
    """
    try:
        # Use parameterized query to prevent SQL injection
        query = "SELECT password FROM user_infos WHERE username = %s"
        result = db_ops.fetch_one(query, (username,))  # Fetch the result using the username as a parameter
        
        if result:
            return result['password']  # Return the hashed password from the dictionary
        
        return None  # Return None if no result is found
    except Exception as e:
        st.error("Failed to get password")
        st.exception(e)

def get_crmpassword_by_username(username):
    """
    Fetches the hashed password associated with a given username.

    Args:
        username: The username to fetch the password for.

    Returns:
        The hashed password if the username exists, None otherwise.
    """
    try:
        query = "SELECT crm_password FROM crm_user WHERE username = %s"
        result = db_ops.fetch_one(query,  (username,))
        if result:
            return result['crm_password']
        return None
    except Exception as e:
        st.error("Failed to get the crm password")
        st.exception(e)
        return False


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

def update_password(username, new_password):
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
        if username in get_usernames():
            query1 = """
                UPDATE user_infos
                SET password = %s
                WHERE username = %s
            """
            params = (hashed_password, username)
            db_ops.update_data(query1, params)
            return True
        else:
            query2 = """
                UPDATE crm_user
                SET crm_password = %s
                WHERE username = %s
            """
            params = (hashed_password, username)
            db_ops.update_data(query2, params)
            return True
    except Exception as e:
        st.error("Failed to update password")
        st.exception(e)
        return False
def get_role_by_username(username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    # cursor.execute("SELECT role FROM user_infos WHERE username = %s", (username,))
    try:
        query = """
            SELECT rl.role 
            FROM user_infos ui
            JOIN role_list rl ON ui.role = rl.role_Id
            WHERE ui.username = %s
        """
        result = db_ops.fetch_one(query, (username,))
        
        if result:
            return result['role']  # Return the role from the dictionary
        
        return None  # Return None if no result is found

    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the role. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False

def get_role_by_crmusername(username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    # cursor.execute("SELECT role FROM user_infos WHERE username = %s", (username,))
    try:
        query = """
            SELECT ui.role 
            FROM crm_list ui
            JOIN crm_user rl ON ui.employe_id = rl.employe_id
            WHERE rl.username = %s
        """
        resultt = db_ops.fetch_one(query, (username,))
        if resultt:
            return resultt['role']
        else:
            return None
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the role. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False



def is_branch_registered(branch):
    """
    Checks if the given branch is registered in the `user_infos` table.
    
    Args:
        cursor: MySQL cursor object.
        branch: The branch name to check.
        
    Returns:
        A list of branch names if the branch code is found in the `user_infos` table, otherwise an empty list.
    """
    
    # Fetch branch_code from branch_list
    query1 = "SELECT branch_code FROM branch_list WHERE branch_name = %s"
    result = db_ops.fetch_one(query1, (branch,))
    if result is None:
        # Branch not found in branch_list
        return []

    branch_code = result['branch_code']

    # Check if branch_code is present in user_infos
    query2 = "SELECT DISTINCT branch FROM user_infos WHERE branch = %s"
    result2 = db_ops.fetch_data(query2, (branch_code,))
    if not result2:
        # No records found for the branch_code in user_infos
        return []

    # Fetch branch names corresponding to branch_code
    query3 = "SELECT branch_name FROM branch_list WHERE branch_code = %s"
    branches = [row['branch_name'] for row in db_ops.fetch_data(query3, (branch_code,)) if row['branch_name'] is not None]

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

def get_unquiephone():
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber.
    """
    try:
        query = "SELECT phoneNumber FROM uniquecustomer"
        phone = [user['phoneNumber'] for user in db_ops.fetch_data(query)]
        modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
        # st.write(modified_phone)
        return modified_phone
    
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the phone number. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False

def get_unquieaccount():
    """
    Fetches a list of account from the MySQL server database.

    Returns:
        A list of user account.
    """
    try:
        query = "SELECT Saving_Account FROM uniquecustomer"
        account = [user['Saving_Account'] for user in db_ops.fetch_data(query)]
        return account
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the saving account. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False

def validate_saving_account(saving_account):
    """
    Validates if the saving account length is either 12 or 13 characters.

    Args:
    saving_account (str): The saving account to validate.

    Returns:
    bool: True if the saving account length is valid, False otherwise.
    """
    
    return saving_account.isdigit() and len(saving_account) in [12, 13]

def get_conversionphone():
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber.
    """
    try:
        query = "SELECT phoneNumber FROM conversioncustomer"
        phone = [user['phoneNumber'] for user in db_ops.fetch_data(query)]
        modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
        return modified_phone
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the phone number. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False

def get_conversionaccount():
    """
    Fetches a list of account from the MySQL server database.

    Returns:
        A list of user account.
    """
    try:
        query = "SELECT Saving_Account FROM conversioncustomer"
        account = [user['Saving_Account'] for user in db_ops.fetch_data(query)]
        return account
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the account number. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False

def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@coopbankoromiasc\.com$"
    return re.match(pattern, email)

def has_user_sent_request_today(username):
    """
    Checks if the user has already sent a reset request today.

    Args:
    cursor (MySQLCursor): The cursor object to execute the query.
    username (str): The username to check.

    Returns:
    bool: True if the user has already sent a request today, False otherwise.
    """
    query = """
    SELECT COUNT(*) as request_count 
    FROM reset_user_password
    WHERE `user name` = %s AND `Asked Date` >= CURDATE() - INTERVAL 3 DAY
    """
    
    # Fetch the result from the database
    result = db_ops.fetch_one(query, (username,))
    
    # Ensure the result is not None and fetch the count
    if result:
        request_count = result['request_count']  # Assuming fetch_one returns a dictionary
        return request_count > 0
    else:
        return False

def get_fullname_by_username(username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    try:
        query = "SELECT full_Name FROM user_infos WHERE username = %s"
        result = db_ops.fetch_one(query, (username,))

        if result:
            return result['full_Name']  # Returning the role

        else:
            return None
    
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the full name. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False
    

def get_fullname_by_crmusername(username):
    """
    Retrieves the role associated with the given username from the database.

    Parameters:
        cursor (mysql.connector.cursor): Cursor object to execute MySQL queries.
        username (str): Username of the user.

    Returns:
        str: Role associated with the username.
    """
    try:
        query = """SELECT ui.full_name FROM crm_list ui
                    JOIN crm_user rl ON ui.employe_id = rl.employe_id 
                    WHERE rl.username = %s"""
        resultt = db_ops.fetch_one(query, (username,))
        if resultt:
            return resultt['full_name']
        else:
            return None
    except Exception as e:
        # Log the error for developers and show a user-friendly message
        st.error("An error occurred while retrieving the full name. Please try again later.")
        st.exception(f"Error: {str(e)}")  # Log the actual error for debugging
        return False
    

def get_roles_from_db():
    # cursor = .cursor()
    query = "SELECT role FROM role_list"
    roles = db_ops.fetch_data(query)
    return [role['role'] for role in roles]

def get_district_from_db():
    # cursor = .cursor()
    query = "SELECT district_name FROM district_list"
    district = db_ops.fetch_data(query)
    return [dis['district_name'] for dis in district]

def get_branch_from_db(district):
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
        query1 = "SELECT dis_Id FROM district_list WHERE district_name = %s"
        dis_id = db_ops.fetch_one(query1, (district,))
        
        # Check if the district ID is found
        if dis_id:
            dis_id = dis_id['dis_Id']
            # Fetch branch names for the district ID
            query2 = "SELECT branch_name FROM branch_list WHERE dis_Id = %s"
            branches = db_ops.fetch_data(query2, (dis_id,))
            return [branch['branch_name'] for branch in branches]
        else:
            # Return an empty list if no district ID is found
            return []
    except Exception as e:
        # Log the error or handle it as needed
        print(f"Error fetching branches: {e}")
        return []
    
def load_targetdata():
    query1 = "SELECT branch_code, branch_name FROM branch_list"
    df_branch = pd.DataFrame(db_ops.fetch_data(query1))
    df_branch.columns=['Branch Code', 'Branch']

    query = """
    SELECT t.branch_code, t.unique_target, t.account_target, t.disbursment_target, t.target_date, t.created_date
    FROM target t
    JOIN (
        SELECT branch_code, MAX(created_date) AS max_date
        FROM target
        GROUP BY branch_code
    ) latest ON t.branch_code = latest.branch_code AND t.created_date = latest.max_date
    """
    
    df_target = pd.DataFrame(db_ops.fetch_data(query))
    df_target.columns=['Branch Code', 'Unique Target', 'Account Target', 'Disbursment Target', 'Target Date', 'Uploaded Date']

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_target, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Unique Target', 'Account Target', 'Disbursment Target', 'Target Date', 'Uploaded Date']]
    
    return df_combine

def load_actualdata():
    df_branch = pd.DataFrame(db_ops.fetch_data("SELECT branch_code, branch_name FROM branch_list"), columns=['Branch Code', 'Branch'])

    query = """
    SELECT t.branch_code, t.unique_actual, t.account_actual, t.disbursment_actual, t.actual_date, t.created_date
    FROM actual t
    JOIN (
        SELECT branch_code, MAX(created_date) AS max_date
        FROM actual
        GROUP BY branch_code
    ) latest ON t.branch_code = latest.branch_code AND t.created_date = latest.max_date
    """
    
    df_actual = pd.DataFrame(db_ops.fetch_data(query), columns=['Branch Code', 'Unique Actual', 'Account Actual', 'Disbursment Actual', 'Actual Date', 'Uploaded Date'])

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Unique Actual', 'Account Actual', 'Disbursment Actual', 'Actual Date', 'Uploaded Date']]
    
    return df_combine



def branchCustomer(username, fullName, product_type, phone_number, tin_number, Saving_Account, disbursed_Amount, region, zone, woreda, specific_area, line_of_business, purpose_of_loan, staff_name, remark):
    try:
        # Validate the phone number format before processing
        if phone_number.startswith('0') and len(phone_number) == 10:
            processed_phone_number = "+251" + phone_number[1:]  # Properly format phone number
            
        else:
            st.error("Invalid phone number format. Please enter a valid Ethiopian number starting with '0'.")
            return False

        # Retrieve userId from user_infos table using the provided username
        query1 = "SELECT userId FROM user_infos WHERE username = %s"
        result = db_ops.fetch_one(query1, (username,))  # Fetch the first row
        
        if result:
            userId = result['userId']  # Extract userId from the result

            # Insert customer information into the branchcustomer table
            query2 = """
                INSERT INTO branchcustomer(userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Region, Zone, Woreda, Specific_Area, Line_of_Business, Purpose_of_Loan, Staff_Name, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(query2, (userId, fullName, product_type, processed_phone_number, tin_number, Saving_Account, disbursed_Amount, region, zone, woreda, specific_area, line_of_business, purpose_of_loan, staff_name, remark))
            return True
        else:
            st.error("User not found with the provided username.")
            return False

    except Exception as e:
        st.error("Failed to insert customer information. Please check your input and try again.")
        st.exception(e)  # Log the actual error for debugging
        return False



def check_unique_phone(phone_number):
    """
    Fetches phone number from the MySQL server database to check if it exists.

    Args:
        cursor: MySQL cursor object
        phone_number: Phone number to check

    Returns:
        bool: True if the phone number exists, False otherwise
    """
    processed_phone_number = "+251" + phone_number[1:]
    try:
        # Retrieve phone number from customer_list table
        query1 = "SELECT phone_number FROM customer_list WHERE phone_number = %s"
        result1 = db_ops.fetch_one(query1, (processed_phone_number,))
        
        # Retrieve phone number from customer_list_nonecode table
        query2 = "SELECT phone_number FROM customer_list_nonecode WHERE phone_number = %s"
        result2 = db_ops.fetch_one(query2, (processed_phone_number,))
        # Retrieve phone number from branchcustomer table
        query3 = "SELECT phoneNumber FROM branchcustomer WHERE phoneNumber = %s"
        result3 = db_ops.fetch_one(query3, (processed_phone_number,))

        # Retrieve phone number from kiyya_customer table
        query4 = "SELECT phone_number FROM kiyya_customer WHERE phone_number = %s"
        result4 = db_ops.fetch_one(query4, (processed_phone_number,))

        # Retrieve phone number from women_product table
        query5 = "SELECT phone_number FROM women_product_customer WHERE phone_number = %s"
        result5 = db_ops.fetch_one(query5, (processed_phone_number,))
        
        # Check if phone number exists in any of the tables
        return result1 is not None or result2 is not None or result3 is not None or result4 is not None or result5 is not None
    except Exception as e:
        st.error("Failed to search phone number")
        st.exception(e)
        return False
def check_unique_account(account):
    """
    Fetches phone number from the MySQL server database to check if it exists.

    Args:
        cursor: MySQL cursor object
        phone_number: Phone number to check

    Returns:
        bool: True if the phone number exists, False otherwise
    """
    # processed_phone_number = "+251" + phone_number[1:]
    try:
        # Retrieve phone number from customer_list table
        query1 = "SELECT saving_account FROM customer_list WHERE saving_account = %s"
        result1 = db_ops.fetch_one(query1, (account,))
        
        # Retrieve phone number from customer_list_nonecode table
        query2 = "SELECT saving_account FROM customer_list_nonecode WHERE saving_account = %s"
        result2 = db_ops.fetch_one(query2, (account,))

        # Retrieve phone number from branchcustomer table
        query3 = "SELECT Saving_Account FROM branchcustomer WHERE Saving_Account = %s"
        result3 = db_ops.fetch_one(query3, (account,))

        # Retrieve phone number from actualdata table
        query4 = "SELECT saving_account FROM actualdata WHERE saving_account = %s"
        result4 = db_ops.fetch_one(query4, (account,))

        # Retrieve phone number from unique_intersection table
        query5 = "SELECT saving_account FROM unique_intersection WHERE saving_account = %s"
        result5 = db_ops.fetch_one(query5, (account,))

        # Retrieve phone number from conversiondata table
        query6 = "SELECT saving_account FROM conversiondata WHERE saving_account = %s"
        result6 = db_ops.fetch_one(query6, (account,))

        # Retrieve phone number from kiyya_customer table
        query7 = "SELECT account_number FROM kiyya_customer WHERE account_number = %s"
        result7 = db_ops.fetch_one(query7, (account,))
    

        # Retrieve phone number from women_product table
        query8 = "SELECT account_no FROM women_product_customer WHERE account_no = %s"
        result8 = db_ops.fetch_one(query8, (account,))

        
        # Check if phone number exists in any of the tables
        return result1 is not None or result2 is not None or result3 is not None or result4 is not None or result5 is not None or result6 is not None or result7 is not None or result8 is not None
    except Exception as e:
        st.error("Failed to search account number")
        st.exception(e)
        return False


def load_uniqactualdata():
    query1 = "SELECT branch_code, branch_name FROM branch_list"
    df_branch = pd.DataFrame(db_ops.fetch_data(query1))
    df_branch.columns=['Branch Code', 'Branch']

    query = """
    SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date
    FROM unique_intersection
    WHERE DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i') = (
    SELECT MAX(DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i')) FROM unique_intersection
    )
    """
    
    df_actual = pd.DataFrame(db_ops.fetch_data(query))
    df_actual.columns=['Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine

def load_convactualdata():
    query1 = "SELECT branch_code, branch_name FROM branch_list"
    df_branch = pd.DataFrame(db_ops.fetch_data(query1))
    df_branch.columns=['Branch Code', 'Branch']

    query = """
    SELECT branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date
    FROM conversiondata
    WHERE DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i') = (
    SELECT MAX(DATE_FORMAT(upload_date, '%Y-%m-%d %H:%i')) FROM conversiondata)
    """
    
    df_actual = pd.DataFrame(db_ops.fetch_data(query))
    df_actual.columns=['Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    # Merge the two DataFrames based on 'Branch Code'
    merged_df = pd.merge(df_branch, df_actual, on='Branch Code', how='inner')

    df_combine = merged_df[['Branch', 'Branch Code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']]
    
    return df_combine
@st.cache_data
def load_customer_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    
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
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query))
        df_closed.columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date']
        df_active = pd.DataFrame(db_ops.fetch_data(active_query))
        df_active.columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date']
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query))
        df_arrears.columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date']

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district = db_ops.fetch_data(user_query)
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
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
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
        
        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(db_ops.fetch_data(active_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'District User': 
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        user_dis = user_district[0]['district']
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name = %s
        """
        branch_result = db_ops.fetch_data(code_query, (user_dis,))
        # Convert the result into a DataFrame
        df_branch = pd.DataFrame(branch_result)
        df_branch.columns=['District', 'branch_code', 'Branch']
        # Extract branch codes from the result
        branch_codes = [row['branch_code'] for row in branch_result]
        # branch_code = [f"'{row['branch_code']}'" for row in branch_code_result]  # Get all branch codes from the query result and quote them
        # branch_codes_str = ','.join(f"'{code}'" for code in branch_code)  # Prepare for SQL IN clause
        branch_codes_str = ', '.join(['%s'] * len(branch_codes))
        

        # Queries for different loan statuses
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

        # Fetching the data for each status
        columns = ['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date']

        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query, tuple(branch_codes)))
        df_closed.columns=columns
        df_active = pd.DataFrame(db_ops.fetch_data(active_query, tuple(branch_codes)))
        df_active.columns=columns
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query, tuple(branch_codes)))
        df_arrears.columns=columns
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'Branch User':
        user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
        user_branch_code = db_ops.fetch_data(user_query)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE br.branch_code = '{user_branch_code[0][0]}'
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
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
        
        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(db_ops.fetch_data(active_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

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
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(db_ops.fetch_data(active_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')
        df_merged_active = pd.merge(df_branch, df_active, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_closed = df_merged_closed[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_active = df_merged_active[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]
        df_combine_arrears = df_merged_arrears[['cust_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status']]

        return df_combine_closed, df_combine_active, df_combine_arrears
    
    elif role == 'collection_user':
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district = db_ops.fetch_data(user_query)
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
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
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
        
        df_closed = pd.DataFrame(db_ops.fetch_data(closed_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_active = pd.DataFrame(db_ops.fetch_data(active_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Gender','Phone Number', 'Saving Account', 'Business TIN','Application Status', 'Michu Loan Product', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date', 'Loan Status', 'created_date'])

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



def get_branch_code():
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # Queries with placeholders to prevent SQL injection
    branch_query = f"""
        SELECT ui.branch
        FROM user_infos ui
        WHERE ui.username = '{username}'
    """
    
    col_admin_query = """
        SELECT branch_code
        FROM branch_list
    """

    user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
    
    user_district = db_ops.fetch_data(user_query)
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
        branch_code = db_ops.fetch_data(branch_query)
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
        branch_code = db_ops.fetch_data(col_admin_query)
        if branch_code:
            branchs_code = [row[0] for row in branch_code]
            branch_codes = branchs_code
        
    elif role == 'collection_user':
        branch_code = db_ops.fetch_data(col_user_query)
        if branch_code:
            branchs_code = [row[0] for row in branch_code]
            branch_codes = branchs_code

    if branch_codes:
        return branch_codes, role  # Return a list of branch codes
    else:
        return None



def get_dis_and_branch():
    code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
    df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
    return df_branch





# Function to fetch employee ID from the crm_list table
def get_employe_id(employe_id):
    """
    Fetches an employee ID from the crm_list table in the MySQL server database.

    Args:
        : MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = "SELECT employe_id FROM crm_list WHERE employe_id = %s"
    empid = db_ops.fetch_data(query,(employe_id,))
    
    if empid:
        return empid[0]['employe_id']
    return None

# Function to fetch employee ID from the crm_list table
def get_employe_usename(username):
    """
    Fetches an employee ID from the crm_list table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = "SELECT username FROM crm_user WHERE username = %s"
    username = db_ops.fetch_data(query, (username,))
    
    if username:
        return username[0]['username']
    return None

# Function to fetch employee ID from the crm_user table
def get_employe_user(employe_id):
    """
    Fetches an employee ID from the crm_user table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    query = "SELECT employe_id FROM crm_user WHERE employe_id = %s"
    empid = db_ops.fetch_data(query, (employe_id,))
    
    if empid:
        return empid[0]['employe_id']
    return None

# Function to insert a new user into the crm_user table
def insert_crmuser(employe_id, username, password):
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
        query = """
            INSERT INTO crm_user (employe_id, username, crm_password)
            VALUES (%s, %s, %s)
        """
        db_ops.insert_data(query, (employe_id, username, hashed_password))
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False


def womenCustomer(name, phone_number, Saving_Account, disbursed_Amount, remark):
    username = st.session_state.get("username", "")
    crm_id = get_id(username)

    try:
        processed_phone_number = "+251" + phone_number[1:]
        
        query = """
            INSERT INTO women_product_customer(crm_id, full_name, phone_number, account_no, disbursed_amount, remark)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db_ops.insert_data(query, (crm_id, name, processed_phone_number, Saving_Account, disbursed_Amount, remark))
        return True
    except Exception as e:
        st.error("Failed to create user")
        st.exception(e)
        return False


# Function to fetch employee ID from the crm_user table
def get_id(username):
    """
    Fetches an employee ID from the crm_user table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    try:
        if username in get_usernames():
            query1 = "SELECT userId FROM user_infos WHERE userName = %s"
            result = db_ops.fetch_one(query1, (username,))
            return result['userId']
        else:
            query2 = "SELECT crm_id FROM crm_user WHERE username = %s"
            result = db_ops.fetch_one(query2, (username,))
            return result['crm_id']
        # return result[0] if result else None
    except Exception as e:
        st.error("Failed to fetch user id")
        st.exception(e)
        return None


def get_unquiedureatphone():
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber. kiyya_customer
    """
    query = "SELECT phone_number FROM women_product_customer"
    phone = [user['phone_number'] for user in db_ops.fetch_data(query)]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone

def get_unquiedkiyyaphone():
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber kiyya_customer
    """
    query = "SELECT phone_number FROM kiyya_customer"
    phone = [user['phone_number'] for user in db_ops.fetch_data(query)]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone

def get_unquiedkiyyaphone():
    """
    Fetches a list of phoneNumber from the MySQL server database.

    Returns:
        A list of user phoneNumber. kiyya_customer
    """
    query = "SELECT phone_number FROM kiyya_customer"
    phone = [user['phone_number'] for user in db_ops.fetch_data(query)]
    modified_phone = ['0' + p[4:] if len(p) > 4 else '0' for p in phone]
    # st.write(modified_phone)
    return modified_phone


def check_durationunique_account(account):
    """
    Checks if an account number exists in any of the specified tables with specific conditions.

    Args:
        cursor: MySQL database cursor.
        account: Account number to check.

    Returns:
        True if the account number exists in any of the tables, False otherwise.
    """
    # Retrieve account number from women_product_customer table
    query1 = "SELECT account_no FROM women_product_customer WHERE account_no = %s"
    result4 = db_ops.fetch_one(query1, (account,))  # Only fetch one result, no need to fetch all

    # Retrieve saving account from unique_intersection table with specific product types
    query2 = """
        SELECT saving_account FROM unique_intersection 
        WHERE saving_account = %s AND (product_type = 'Women Formal' OR product_type = 'Women Informal')
    """
    result5 = db_ops.fetch_one(query2, (account,))  # Fetch only one result

    # Retrieve saving account from conversiondata table with specific product types
    query3 = """
        SELECT saving_account FROM conversiondata 
        WHERE saving_account = %s AND (product_type = 'Women Formal' OR product_type = 'Women Informal')
    """
    result6 = db_ops.fetch_one(query3, (account,))  # Fetch only one result

    # Retrieve account number from kiyya_customer table
    query4 = "SELECT account_number FROM kiyya_customer WHERE account_number = %s"
    result7 = db_ops.fetch_one(query4, (account,))  # Fetch only one result

    # # Retrieve account number from branch_customer table  
    # cursor.execute("SELECT Saving_Account FROM branchcustomer WHERE Saving_Account = %s", (account,))
    # result8 = cursor.fetchone()  # Fetch only one result

    # Check if account number exists in any of the tables
    return result4 is not None or result5 is not None or result6 is not None or result7 is not None





def load_women_data():
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    try:
        # Fetch userId based on username
        if role == "CRM":
            crm_id_query = "SELECT crm_id FROM crm_user WHERE username = %s"
            crm_id_result = db_ops.fetch_data(crm_id_query, (username,))
        else:
            crm_id_query = "SELECT userId FROM user_infos WHERE username = %s"
            crm_id_result = db_ops.fetch_data(crm_id_query, (username,))

        # Check if crm_id_result is empty
        if not crm_id_result:
            st.warning("No user ID found for the current user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the id based on the role
        id = crm_id_result[0]['crm_id'] if role == "CRM" else crm_id_result[0]['userId']

        dureti_customer_query = "SELECT * FROM women_product_customer WHERE crm_id = %s and `registered_date` >= '2024-10-01'"
        # st.write(dureti_customer_query)
        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"


        dureti_customer_data = db_ops.fetch_data(dureti_customer_query, (id,)) 
        columns = ['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']  
        if not dureti_customer_data:
            dureti_customer = pd.DataFrame(dureti_customer_data, columns = columns)
        else:
            dureti_customer = pd.DataFrame(dureti_customer_data)
            dureti_customer.columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']                            
        # st.write(dureti_customer)
        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
        unique_customer.columns = ['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
        conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

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
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")

@st.cache_data
def load_all_women_data(username):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # CRM user query
    crm_user_query = """
        SELECT dr.crm_id, br.full_name, br.sub_process 
        FROM crm_list br
        JOIN crm_user dr ON br.employe_id = dr.employe_id
        """
    crm_user_list = pd.DataFrame(db_ops.fetch_data(crm_user_query))
    crm_user_list.columns=['crm_id', 'Recruited by', 'Sub Process']

    # Women product customer query
    women_customer_query = """
        SELECT dr.crm_id, br.full_Name, br.district 
        FROM user_infos br
        JOIN women_product_customer dr ON br.userId = dr.crm_id
        """
    women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query))
    women_customer_list.columns=['crm_id', 'Recruited by', 'Sub Process']

    # Combine user data
    combined_user = pd.concat([crm_user_list, women_customer_list], axis=0).drop_duplicates(subset=['crm_id'])

    # Queries for customer data
    dureti_customer_query = "SELECT * FROM women_product_customer WHERE `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal') and disbursed_date >= '2024-10-01'"
    conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal') and disbursed_date >= '2024-10-01'"

    # Fetching customer data
    dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query))
    dureti_customer.columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']

    unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
    conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

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




def kiyya_customer(username, fullName, phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        userId  = get_id(username)
        if userId:
            # Insert customer information into the customer table
            query = """
                INSERT INTO kiyya_customer(userId, fullName, phone_number, account_number, customer_ident_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, daily_sales, purpose_of_loan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(query, (userId, fullName, processed_phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan))
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create customer due to an unexpected error.")
        st.exception(e)
        return False
@st.cache_data
def load_all_kiyya_data(username):
    # Access the username and role from session state
    # username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    # CRM user query
    crm_user_query = """
        SELECT DISTINCT k.userId, br.full_name, br.sub_process 
        FROM crm_list br
        JOIN crm_user dr ON br.employe_id = dr.employe_id
        JOIN kiyya_customer k ON k.userId = dr.crm_id
        """
    crm_user_list = pd.DataFrame(db_ops.fetch_data(crm_user_query))
    crm_user_list.columns=['userId', 'Recruited by', 'Sub Process']

    # Women product customer query
    women_customer_query = """
    SELECT DISTINCT dr.userId, br.full_Name, br.district 
    FROM user_infos br
    JOIN kiyya_customer dr ON br.userId = dr.userId
    """
    women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query))
    women_customer_list.columns=['userId', 'Recruited by', 'Sub Process']

    # Combine user data
    combined_user = pd.concat([crm_user_list, women_customer_list], axis=0).drop_duplicates(subset=['userId']).reset_index(drop=True).rename(lambda x: x + 1)
  

    # Queries for customer data
    keyya_customer_query = "SELECT * FROM kiyya_customer where userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' and `registered_date` >= '2024-10-01'"
    unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal') and disbursed_date >= '2024-10-01'"
    conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal') and disbursed_date >= '2024-10-01'"

    # Fetching customer data
    dureti_customer = pd.DataFrame(db_ops.fetch_data(keyya_customer_query))
    dureti_customer.columns=['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date']
    unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
    conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

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


def load_kiyya_data():
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")

    try:
        # Fetch userId based on username
        if role == "CRM":
            crm_id_query = "SELECT crm_id FROM crm_user WHERE username = %s"
            crm_id_result = db_ops.fetch_data(crm_id_query, (username,))
        else:
            crm_id_query = "SELECT userId FROM user_infos WHERE username = %s"
            crm_id_result = db_ops.fetch_data(crm_id_query, (username,))

        # Check if crm_id_result is empty
        if not crm_id_result:
            st.warning("No user ID found for the current user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the id based on the role
        id = crm_id_result[0]['crm_id'] if role == "CRM" else crm_id_result[0]['userId']
        # st.write(id)
        # Query for dureti_customer based on userId and registered_date
        dureti_customer_query = """
            SELECT * FROM kiyya_customer 
            WHERE userId = %s 
            AND registered_date >= '2024-10-01'
        """
        
        dureti_customer_data = db_ops.fetch_data(dureti_customer_query, (id,))
        if not dureti_customer_data:
            # Define the expected column names
            columns = ['kiyya_id', 'userId', 'Full Name', 'Phone Number', 
                    'Saving Account', 'Customer Identification Type', 'Gender', 
                    'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 
                    'Woreda', 'Educational Level', 'Business Sector', 
                    'Line of Business', 'Initial Working Capital', 
                    'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 
                    'Register Date']
            dureti_customer = pd.DataFrame(dureti_customer_data, columns=columns)
        else:
            dureti_customer = pd.DataFrame(dureti_customer_data)
            dureti_customer.columns = ['kiyya_id', 'userId', 'Full Name', 'Phone Number', 
                    'Saving Account', 'Customer Identification Type', 'Gender', 
                    'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 
                    'Woreda', 'Educational Level', 'Business Sector', 
                    'Line of Business', 'Initial Working Capital', 
                    'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 
                    'Register Date']
            # st.write(dureti_customer)
        
        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = f"SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"

        
        # dureti_customer.columns =  ['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date']
        # st.write(dureti_customer)
        
        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
        unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
        conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

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
        # st.write(combined_cust_by_crm)
        # st.write(crm_cust_only)
        return combined_cust_by_crm, crm_cust_only
    except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")

def load_kiyya_branch_data():
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    if role == 'District User':
        # Fetch the user's district
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district = db_ops.fetch_data(user_query)

        # Check if a district was found for the user
        if not user_district or len(user_district) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district value from the query result
        district_value = user_district[0][0]

        # Fetch userIds for the corresponding district
        crm_id_query = f"SELECT userId FROM user_infos WHERE district = '{district_value}'"
        crm_id_result = db_ops.fetch_data(crm_id_query)

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

        # Women product customer query
        women_customer_query = f"""
        SELECT DISTINCT dr.userId, br.full_Name
        FROM user_infos br
        JOIN kiyya_customer dr ON br.userId = dr.userId
        WHERE br.district = ('{district_value}')
        """
        women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query), columns=['userId', 'Recruited by'])
        # st.write(women_customer_list)

        dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), 
                                    columns = ['kiyya_id', 'userId', 'Full Name','Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])

        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount',  'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        merged_combined_cust_by_crm = pd.merge(combined_cust_by_crm, women_customer_list, on='userId', how='inner').drop_duplicates()
        # st.write(combined_cust_by_crm)

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['kiyya_id', 'userId','Phone Number', 'Saving Account'], how='left', indicator=True)
        # st.write(merged_df)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity', 'Woreda', 'Register Date']]
        merged_crm_cust_only = pd.merge(crm_cust_only, women_customer_list, on='userId', how='inner').drop_duplicates()
        # st.write(merged_crm_cust_only)

        return merged_combined_cust_by_crm, merged_crm_cust_only
    
    elif role == 'Sales Admin':
        # Fetch the user's district (assuming district is stored as a JSON-like array in the database)
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district_result = db_ops.fetch_data(user_query)

        # Check if districts were found for the user
        if not user_district_result or len(user_district_result) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district list from the query result (assuming it's stored in JSON-like format)
        district_value = user_district_result[0][0]
        # st.write(district_value)  # Debugging statement to check the format

        # Parse the district list (remove brackets and quotes if stored as string, or load as JSON)
        district_list = eval(district_value)  # Converts the string to a Python list, use `json.loads` if it’s in proper JSON format
        # st.write(district_list)

        # Prepare district values for SQL IN clause
        district_in_clause = "', '".join([district.strip() for district in district_list])

        # Fetch userIds for the corresponding districts
        crm_id_query = f"SELECT userId FROM user_infos WHERE district IN ('{district_in_clause}')"
        crm_id_result = db_ops.fetch_data(crm_id_query)
        # st.write(crm_id_result)

        # Check if any userIds were found
        if not crm_id_result or len(crm_id_result) == 0:
            st.warning("No user IDs found for the district.")
            return pd.DataFrame(), pd.DataFrame()

        # Extract the userIds from the result
        crm_ids = [str(row[0]) for row in crm_id_result]

        # Construct the query for the kiyya_customer table using the userIds
        crm_id_list = "', '".join(crm_ids)
        dureti_customer_query = f"SELECT * FROM kiyya_customer WHERE userId IN ('{crm_id_list}') AND `registered_date` >= '2024-10-01'"
        # st.write(dureti_customer_query)

        # Queries for unique_intersection and conversiondata tables
        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"

        # Women product customer query
        women_customer_query = f"""
        SELECT DISTINCT dr.userId, br.full_Name, br.district 
        FROM user_infos br
        JOIN kiyya_customer dr ON br.userId = dr.userId
        WHERE br.district IN ('{district_in_clause}')
        """
        women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query), columns=['userId', 'Recruited by', 'Sub Process'])
        # st.write(women_customer_list)
        
        # Fetch and create DataFrames for each query
        dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), 
                                    columns=['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Customer Identification Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan', 'Register Date'])

        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['kiyya_id', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        merged_combined_cust_by_crm = pd.merge(combined_cust_by_crm, women_customer_list, on='userId', how='inner').drop_duplicates()

        # st.write(combined_cust_by_crm)

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on=['kiyya_id', 'userId', 'Phone Number', 'Saving Account'], how='left', indicator=True)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['kiyya_id', 'userId', 'Full Name', 'Phone Number', 'Saving Account', 'Region', 'Zone/Subcity', 'Woreda', 'Register Date']]
        merged_crm_cust_only = pd.merge(crm_cust_only, women_customer_list, on='userId', how='inner').drop_duplicates()
        # st.write(crm_cust_only)

        return merged_combined_cust_by_crm, merged_crm_cust_only



    else:
        st.warning("User is not a District User.")
        return pd.DataFrame(), pd.DataFrame()

def load_formal_branch_data():
    # Access the username from session state
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    if role == 'District User':
        # Fetch the user's district
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district = db_ops.fetch_data(user_query)

        # Check if a district was found for the user
        if not user_district or len(user_district) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district value from the query result
        district_value = user_district[0][0]

        # Fetch userIds for the corresponding district
        crm_id_query = f"SELECT userId FROM user_infos WHERE district = '{district_value}'"
        crm_id_result = db_ops.fetch_data(crm_id_query)

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


        dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), 
                                    columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date'])

        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        
        # Women product customer query
        women_customer_query = f"""
        SELECT DISTINCT br.userId, br.full_Name
        FROM user_infos br
        JOIN women_product_customer dr ON br.userId = dr.crm_id
        WHERE br.district = ('{district_value}')
        """
        women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query), columns=['crm_id', 'Recruited by'])


        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        merged_combined_cust_by_crm = pd.merge(combined_cust_by_crm, women_customer_list, on='crm_id', how='inner').drop_duplicates()
        # st.write(combined_cust_by_crm)

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on= ['wpc_id', 'crm_id','Phone Number', 'Saving Account', 'remark'], how='left', indicator=True)
        # st.write(merged_df)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']]
        merged_crm_cust_only = pd.merge(crm_cust_only, women_customer_list, on='crm_id', how='inner').drop_duplicates()

        return merged_combined_cust_by_crm, merged_crm_cust_only
    elif role == 'Sales Admin':
        # Fetch the user's district (assuming district is stored as a JSON-like array in the database)
        user_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_district = db_ops.fetch_data(user_query)

        # Check if a district was found for the user
        if not user_district or len(user_district) == 0:
            st.warning("No district found for the user.")
            return pd.DataFrame(), pd.DataFrame()

        # Get the district value from the query result
        district_value = user_district[0][0]

        # Parse the district list (assuming it’s stored as a JSON-like string)
        district_list = eval(district_value)  # Converts the string to a Python list, use `json.loads()` if it's in proper JSON format
        # st.write(district_list)  # Debugging statement to check the parsed districts

        # Prepare district values for SQL IN clause
        district_in_clause = "', '".join([district.strip() for district in district_list])

        # Fetch userIds for the corresponding districts
        crm_id_query = f"SELECT userId FROM user_infos WHERE district IN ('{district_in_clause}')"
        crm_id_result = db_ops.fetch_data(crm_id_query)

        # Check if any userIds were found
        if not crm_id_result or len(crm_id_result) == 0:
            st.warning("No user IDs found for the district.")
            return pd.DataFrame(), pd.DataFrame()

        # Extract the userIds from the result
        crm_ids = [str(row[0]) for row in crm_id_result]

        # Construct the query for the women_product_customer table using the userIds
        crm_id_list = "', '".join(crm_ids)
        dureti_customer_query = f"SELECT * FROM women_product_customer WHERE crm_id IN ('{crm_id_list}') and `registered_date` >= '2024-10-01'"
        # st.write(dureti_customer_query)
        unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"
        conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type = 'Women Informal' OR product_type = 'Women Formal'"

        # Fetch data and create DataFrames
        dureti_customer = pd.DataFrame(db_ops.fetch_data(dureti_customer_query), 
                                    columns=['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date'])

        unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query), 
                                    columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query), 
                                        columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date'])

        # Women product customer query
        women_customer_query = f"""
        SELECT DISTINCT br.userId, br.full_Name, br.district 
        FROM user_infos br
        JOIN women_product_customer dr ON br.userId = dr.crm_id
        WHERE br.district IN ('{district_in_clause}')
        """
        women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query), columns=['crm_id', 'Recruited by', 'Sub Process'])
        # st.write(women_customer_list)

        # Merge DataFrames on 'Saving Account'
        unique_by_crm = pd.merge(dureti_customer, unique_customer, on='Saving Account', how='inner')
        conv_by_crm = pd.merge(dureti_customer, conversion_customer, on='Saving Account', how='inner')

        # Select and concatenate the required columns
        unique_cust_by_crm = unique_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]
        conv_cust_by_crm = conv_by_crm[['wpc_id', 'crm_id', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed Amount', 'remark', 'Disbursed Date']]

        combined_cust_by_crm = pd.concat([unique_cust_by_crm, conv_cust_by_crm], axis=0).drop_duplicates()
        merged_combined_cust_by_crm = pd.merge(combined_cust_by_crm, women_customer_list, on='crm_id', how='inner').drop_duplicates()

        # Perform a left join to identify customers only in dureti_customer
        merged_df = pd.merge(dureti_customer, combined_cust_by_crm, on=['wpc_id', 'crm_id', 'Phone Number', 'Saving Account', 'remark'], how='left', indicator=True)

        # Filter to keep only rows that are in dureti_customer but not in combined_cust_by_crm
        crm_only = merged_df[merged_df['_merge'] == 'left_only']
        crm_cust_only = crm_only[['wpc_id', 'crm_id', 'Full Name', 'Phone Number', 'Saving Account', 'disbursed_amount', 'remark', 'registered_date']]
        merged_crm_cust_only = pd.merge(crm_cust_only, women_customer_list, on='crm_id', how='inner').drop_duplicates()
        # st.write(merged_crm_cust_only)
        return merged_combined_cust_by_crm, merged_crm_cust_only


    else:
        st.warning("User is not a District User.")
        return pd.DataFrame(), pd.DataFrame()


def load_kiyya_report_data():
    

    # df_user_infos = pd.DataFrame(db_ops.fetch_data(f"SELECT * FROM user_infos WHERE userId = '{user_id}'"), columns=['userId', 'full_Name', 'userName', 'District', 'Branch', 'role', 'password', 'ccreatedAt'])
    # Filtered queries for data starting from July 1
    keyya_customer_query = f"SELECT count(kiyya_id) as total FROM kiyya_customer"
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Build the query to count records from today
    kiyya_customer_query = f"""
        SELECT COUNT(kiyya_id) as total
        FROM kiyya_customer 
        WHERE DATE(registered_date) >= '{today_date}'
    """
    
    # Fetch data and extract the counts
    kiyya_customer = db_ops.fetch_data(keyya_customer_query)[0]['total']  # Extract the count value
    kiyya_customer_today = db_ops.fetch_data(kiyya_customer_query)[0]['total']  # Extract the count value

    formal_women_query = f"SELECT count(wpc_id) as total FROM women_product_customer"
    formaltodays_query = f"""
        SELECT COUNT(wpc_id) as total
        FROM women_product_customer 
        WHERE DATE(registered_date) = '{today_date}'
    """
    # Fetch data and extract the counts
    formal_customer = db_ops.fetch_data(formal_women_query)[0]['total']  # Extract the count value
    formal_customer_today = db_ops.fetch_data(formaltodays_query)[0]['total']  # Extract the count value
    

    return kiyya_customer, kiyya_customer_today, formal_customer, formal_customer_today



@st.cache_data
def load_kiyya_actual_vs_targetdata(role, username):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        try:
            # CRM user query
            crm_user_query = """
                SELECT DISTINCT dr.crm_id, br.full_name, br.sub_process, br.employe_id 
                FROM crm_list br
                LEFT JOIN crm_user dr ON br.employe_id = dr.employe_id
                """
            crm_user_list = pd.DataFrame(db_ops.fetch_data(crm_user_query))
            # st.write(crm_user_list)
            crm_user_list.columns=['user_Id', 'Recruited by', 'Sub Process', 'branch_code']
            # st.write(crm_user_list)
            # Women product customer query
            women_customer_query = """
            SELECT DISTINCT br.userId, br.full_Name, br.district, br.branch 
            FROM user_infos br
            """
            women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query))
            women_customer_list.columns=['user_Id', 'Recruited by', 'Sub Process', 'branch_code']

            # Combine user data
            combined_user = pd.concat([crm_user_list, women_customer_list], axis=0).drop_duplicates(subset=['branch_code']).reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(combined_user)
        
            # st.write(combined_user)
            # Queries for customer data
            in_customer_query = "SELECT kiyya_id, userId, fullName, phone_number, account_number, registered_date FROM kiyya_customer where userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' and `registered_date` >= '2024-10-01'"
            # Queries for customer data
            formal_customer_query = "SELECT wpc_id, crm_id, full_name, phone_number, account_no, registered_date FROM women_product_customer WHERE `registered_date` >= '2024-10-01'"

            unique_customer_query = "SELECT * FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal') AND disbursed_date >= '2024-10-01'AND saving_account NOT IN (SELECT saving_account FROM unique_intersection WHERE product_type IN ('Women Informal', 'Women Formal') AND disbursed_date < '2024-10-01')"
            conversion_customer_query = "SELECT * FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal') AND disbursed_date >= '2024-10-01' AND saving_account NOT IN (SELECT saving_account FROM conversiondata WHERE product_type IN ('Women Informal', 'Women Formal') AND disbursed_date < '2024-10-01')"

            # Fetching customer data for informal customers
            informal_customer = pd.DataFrame(db_ops.fetch_data(in_customer_query))
            informal_customer.columns=['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']

            # Add product_type column as 'Informal' for informal_customer
            informal_customer['product_type'] = 'Women Informal'


            # Convert 'Register Date' to match the format of formal_customer ('YYYY-MM-DD')
            informal_customer['Register Date'] = pd.to_datetime(informal_customer['Register Date']).dt.strftime('%Y-%m-%d')

            # Fetching customer data for formal customers
            formal_customer = pd.DataFrame(db_ops.fetch_data(formal_customer_query))
            formal_customer.columns=['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']

            # Add product_type column as 'Formal' for formal_customer
            formal_customer['product_type'] = 'Women Formal'
            unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
            unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

            conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query))
            conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            
            # Merge DataFrames on 'Saving Account'
            unique_conversation = pd.concat([unique_customer, conversion_customer], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(unique_conversation)
            bf_kiyya = "select saving_account from misseddata"
            bf_kiyya_customer = pd.DataFrame(db_ops.fetch_data(bf_kiyya))
            bf_kiyya_customer.columns=['Saving Account']
            unique_conversation = unique_conversation.merge(bf_kiyya_customer, on='Saving Account', how='left', indicator=True)

            # Filter rows where bf_kiyya_customer doesn't have a match in unique_conversation
            unique_not_in_bf_kiyya = unique_conversation[unique_conversation['_merge'] == 'left_only']

            # Drop the _merge column (optional)
            unique_conversation = unique_not_in_bf_kiyya.drop(columns=['_merge'])
            # st.write(unique_conversation)
            infrmal_formal = pd.concat([informal_customer, formal_customer], axis=0).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(combined_user)
            informal_formal_code = infrmal_formal.merge(combined_user, on='user_Id', how='inner')
            # st.write(informal_formal_code)
            # disbersed_by_recurate = pd.merge(infrmal_formal, unique_conversation, on='Saving Account', how='inner')
            # st.write(disbersed_by_recurate)
            full_disb = unique_conversation.merge(informal_formal_code, on='Saving Account', how='left').drop_duplicates(subset=['Saving Account'], keep='first')
            # st.write(full_disb)

            
            
            # st.write(merged_df)
            # Replace null values in user_Id of full_disb with user_Id from combined_user when branch_code matches
            full_disb['branch_code_y'] = np.where(
                full_disb['branch_code_y'].isnull(),    # Check if user_Id is null
                full_disb['branch_code_x'],    # Replace with user_Id_combined if condition is met
                full_disb['branch_code_y']              # Keep the original user_Id otherwise
            )
            # st.write(full_disb)

            # Drop the extra combined columns that were added during the merge
            full_disberment_user = pd.merge(full_disb, combined_user, left_on='branch_code_y', right_on='branch_code', how='outer')
            # st.write(full_disberment_user)
            full_disberment_user.drop_duplicates(subset=['branch_code'])
            # st.write(full_disberment_user)

        

            target_query = "SELECT target_id, user_id, target_amount, catagory, registered_date FROM kiyya_target"
            df_target = pd.DataFrame(db_ops.fetch_data(target_query))
            df_target.columns=['target_id', 'branch_code', 'Target Customer', 'Catagory', 'registered_date'] 
            # st.write(df_target)

            return  full_disberment_user, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame()
    

    elif role == "District User":
        try:
            # Fetch district for the given username
            user_id_query = "SELECT district FROM user_infos WHERE userName = %s"
            user_id_result = db_ops.fetch_data(user_id_query, (username,))
            if not user_id_result:
                st.warning("No user found with the given username.")
                return pd.DataFrame(), pd.DataFrame()

            # district = user_id_result[0][0]  # Assuming district is the first element in the first row of the result
            district = user_id_result[0]['district']

            # Fetch branch codes based on district
            # user_branch_code_query = "SELECT employe_id FROM crm_list"
            user_branch_code_query = "SELECT branch FROM user_infos where district = %s"
            branch_code_result = db_ops.fetch_data(user_branch_code_query, (district,))
            # st.write(branch_code_result)
            if not branch_code_result:
                st.warning(f"No branches found for the district: {district}.")
                return pd.DataFrame(), pd.DataFrame()

            # Ensure that the result is a list of branch codes
            branch_codes = [row['branch'] for row in branch_code_result]

            # Join branch codes into a comma-separated string for the IN clause
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))


            # Women product customer query
            women_customer_query = "SELECT DISTINCT userId, full_Name, district, branch FROM user_infos WHERE district = %s"
            women_customer_list = pd.DataFrame(db_ops.fetch_data(women_customer_query, (district,)))
            women_customer_list.columns = ['user_Id', 'Recruited by', 'Sub Process', 'branch_code']

            # Combine user data and rename columns properly
            combined_user = women_customer_list.drop_duplicates(subset=['branch_code']).reset_index(drop=True)

            # Queries for customer data (informal customers)
            in_customer_query = """
                SELECT kiyya_id, userId, fullName, phone_number, account_number, registered_date 
                FROM kiyya_customer 
                WHERE userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' 
                AND registered_date >= '2024-10-01'
            """
            informal_customer = pd.DataFrame(db_ops.fetch_data(in_customer_query))
            informal_customer.columns = ['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']
            informal_customer['product_type'] = 'Women Informal'
            informal_customer['Register Date'] = pd.to_datetime(informal_customer['Register Date']).dt.strftime('%Y-%m-%d')


            # Queries for customer data (formal customers)
            formal_customer_query = """
                SELECT wpc_id, crm_id, full_name, phone_number, account_no, registered_date 
                FROM women_product_customer 
                WHERE registered_date >= '2024-10-01'
            """
            formal_customer = pd.DataFrame(db_ops.fetch_data(formal_customer_query))
            formal_customer.columns = ['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']
            formal_customer['product_type'] = 'Women Formal'

            # Fetch the userId for the corresponding district
            user_branch_code_query = "SELECT userId FROM user_infos WHERE district = %s"
            branch_code_result = db_ops.fetch_data(user_branch_code_query, (district,))

            # Convert the result into a tuple of userIds
            userid_tuple = tuple([row['userId'] for row in branch_code_result])

          

            # Construct the account query
            # Dynamically create the placeholders for the IN clause based on the number of userIds
            placeholders = ', '.join(['%s'] * len(userid_tuple))

            # Adjust the account query to use the dynamically created placeholders
            account_query = f"SELECT account_number FROM kiyya_customer WHERE userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND userId NOT IN ({placeholders})"
            account_query_formal = f"SELECT account_no FROM women_product_customer WHERE crm_id != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND crm_id NOT IN ({placeholders})"

            # Execute the query, unpacking the tuple using *
            account_result = db_ops.fetch_data(account_query, userid_tuple)
            # st.write(account_result)
            account_query_f = db_ops.fetch_data(account_query_formal, userid_tuple)
            account_query_f_tuple = tuple([row['account_no'] for row in account_query_f])

            # Convert the list of account numbers to a tuple for parameterized queries
            account_numbers_tuple = tuple([row['account_number'] for row in account_result])
            # st.write(account_numbers_tuple)
            placeholders2 = ', '.join(['%s'] * len(account_numbers_tuple))
            # st.write(placeholders2)
            placeholders3 = ', '.join(['%s'] * len(account_query_f_tuple))

            # if not account_numbers_tuple:
            #     st.warning("No account numbers found that match the conditions.")
            #     return pd.DataFrame()

            # Construct the final query, using account numbers fetched in the subquery
            unique_customer_query = f"""
                SELECT * FROM unique_intersection 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date >= '2024-10-01'
                AND saving_account NOT IN ({placeholders2})
                AND saving_account NOT IN ({placeholders3})
                AND saving_account NOT IN (
                    SELECT saving_account FROM unique_intersection 
                    WHERE product_type IN ('Women Informal', 'Women Formal') 
                    AND disbursed_date < '2024-10-01'
                )
            """
            params = account_numbers_tuple + account_query_f_tuple

            # Execute the query, passing the account numbers as parameters
            unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query, params))

            # st.write(unique_customer)
            
            conversion_customer_query = f"""
                SELECT * FROM conversiondata 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date >= '2024-10-01'
                AND saving_account NOT IN ({placeholders2})
                AND saving_account NOT IN ({placeholders3})
                AND saving_account NOT IN (
                    SELECT saving_account FROM conversiondata 
                    WHERE product_type IN ('Women Informal', 'Women Formal') 
                    AND disbursed_date < '2024-10-01'
                )
            """
            # Execute the unique customer query with the fetched account numbers
            # unique_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query, (account_numbers_tuple,)))

            unique_customer.columns = ['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            conversion_customer = pd.DataFrame(db_ops.fetch_data(conversion_customer_query, params))
            conversion_customer.columns = ['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

            
            # Merge DataFrames on 'Saving Account'
            unique_conversation = pd.concat([unique_customer, conversion_customer], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True)

            # Fetching missed data
            bf_kiyya_query = "SELECT saving_account FROM misseddata"
            bf_kiyya_customer = pd.DataFrame(db_ops.fetch_data(bf_kiyya_query))
            bf_kiyya_customer.columns = ['Saving Account']

            unique_conversation = unique_conversation.merge(bf_kiyya_customer, on='Saving Account', how='left', indicator=True)

            # Filter rows where bf_kiyya_customer doesn't have a match in unique_conversation
            unique_not_in_bf_kiyya = unique_conversation[unique_conversation['_merge'] == 'left_only']

            # Drop the _merge column (optional)
            unique_conversation = unique_not_in_bf_kiyya.drop(columns=['_merge'])
            # st.write(unique_conversation)
            infrmal_formal = pd.concat([informal_customer, formal_customer], axis=0).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(combined_user)
            informal_formal_code = infrmal_formal.merge(combined_user, on='user_Id', how='inner')
            # st.write(informal_formal_code)
            # disbersed_by_recurate = pd.merge(infrmal_formal, unique_conversation, on='Saving Account', how='inner')
            # st.write(disbersed_by_recurate)
            full_disb = unique_conversation.merge(informal_formal_code, on='Saving Account', how='left').drop_duplicates(subset=['Saving Account'], keep='first')
            # st.write(full_disb)

            # st.write(merged_df)
            # Replace null values in user_Id of full_disb with user_Id from combined_user when branch_code matches
            full_disb['branch_code_y'] = np.where(
                full_disb['branch_code_y'].isnull(),    # Check if user_Id is null
                full_disb['branch_code_x'],    # Replace with user_Id_combined if condition is met
                full_disb['branch_code_y']              # Keep the original user_Id otherwise
            )
            # st.write(full_disb)

            # Drop the extra combined columns that were added during the merge
            full_disberment_user = pd.merge(full_disb, combined_user, left_on='branch_code_y', right_on='branch_code', how='outer')
            # st.write(full_disberment_user)
            full_disberment_user.drop_duplicates(subset=['branch_code'])

            # Fetch target data (ensure correct parameter passing for branch codes)
            df_target_query = f"SELECT target_id, user_id, target_amount, catagory, registered_date FROM kiyya_target WHERE user_id IN ({branch_codes_str})"
            df_target = pd.DataFrame(db_ops.fetch_data(df_target_query, tuple(branch_codes)))
            df_target.columns = ['target_id', 'branch_code', 'Target Customer', 'Catagory', 'registered_date']

            

            return  full_disberment_user, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame()


    elif role == "Sales Admin":
        district_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        district_result = db_ops.fetch_data(district_query)

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
        district_result = db_ops.fetch_data(district_query)
        if not district_result:
            st.warning("No district found with the given district names.")
            return pd.DataFrame()  # Return an empty DataFrame if no districts are found

        dis_ids = [row[0] for row in district_result]

        # Convert the list of dis_Id to a string suitable for the SQL IN clause
        dis_ids_str = ', '.join(f"'{d}'" for d in dis_ids)

        # Fetch branch code and branch name
        branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id IN ({dis_ids_str})"
        branch_code_result = db_ops.fetch_data(branch_code_query)
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
            db_ops.fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code IN ({branch_codes_str})"), 
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )

        # Fetch target data
        df_target = pd.DataFrame(
            db_ops.fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code IN ({branch_codes_str})"),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        return act_dis_branch, df_actual, df_target

    elif role == "Branch User":
       
        # Query to fetch user information for the given username
        women_customer_query = """
            SELECT DISTINCT br.userId, br.full_Name, br.district, br.branch 
            FROM user_infos br
            WHERE br.userName = %s
        """
        
        # Fetching the result using a parameterized query to prevent SQL injection
        result = db_ops.fetch_data(women_customer_query, (username,))
        # st.write(result)

        # Check if a result was returned before accessing it
        if result:
            user_id = result[0]['userId']  # Accessing the first result's 'userId'
            branch_code = result[0]['branch']

            # Query for informal customer data using user_id
            in_customer_query = """
                SELECT kiyya_id, userId, fullName, phone_number, account_number, registered_date
                FROM kiyya_customer
                WHERE userId != %s 
                AND registered_date >= '2024-10-01'
                AND userId = %s
            """
            # Formal customer query
            formal_customer_query = """
                SELECT wpc_id, crm_id, full_name, phone_number, account_no, registered_date 
                FROM women_product_customer 
                WHERE registered_date >= '2024-10-01' AND crm_id = %s
            """
            # Adjust the account query to use the dynamically created placeholders
            account_query = "SELECT account_number FROM kiyya_customer WHERE userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND userId != %s"
            account_query_formal = "SELECT account_no FROM women_product_customer WHERE crm_id != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND crm_id != %s"

            # Execute the query, unpacking the tuple using *
            account_result = db_ops.fetch_data(account_query, (user_id,))
            # st.write(account_result)
            account_query_f = db_ops.fetch_data(account_query_formal, (user_id,))

            # Check if the results are empty and set to an empty tuple if they are
            account_numbers_tuple = tuple([row['account_number'] for row in account_result]) if account_result else ()
            account_query_tuple = tuple([row['account_no'] for row in account_query_f]) if account_query_f else ()

            # Generate placeholders for SQL query
            placeholders2 = ', '.join(['%s'] * len(account_numbers_tuple)) if account_numbers_tuple else '%s'
            placeholders3 = ', '.join(['%s'] * len(account_query_tuple)) if account_query_tuple else '%s'



            # Unique customer query for disbursements after October 1st, 2024
            unique_customer_query = f"""
                SELECT * 
                FROM unique_intersection 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date >= '2024-10-01'
                AND saving_account NOT IN ({placeholders2})
                AND saving_account NOT IN ({placeholders3})
                AND saving_account NOT IN (
                    SELECT saving_account 
                    FROM unique_intersection 
                    WHERE product_type IN ('Women Informal', 'Women Formal') 
                    AND disbursed_date < '2024-10-01'
                ) 
                AND branch_code = %s
            """
            
            # Conversion customer query for similar data
            conversion_customer_query = f"""
                SELECT * 
                FROM conversiondata 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date >= '2024-10-01' 
                AND saving_account NOT IN ({placeholders2})
                AND saving_account NOT IN ({placeholders3})
                AND saving_account NOT IN (
                    SELECT saving_account 
                    FROM conversiondata 
                    WHERE product_type IN ('Women Informal', 'Women Formal') 
                    AND disbursed_date < '2024-10-01'
                ) 
                AND branch_code = %s
            """

            combined_user = pd.DataFrame(result)
            combined_user.columns=['user_Id', 'Recruited by', 'Sub Process', 'branch_code']
            # Fetching customer data for informal customers
            # st.write(combined_user)
            informal_customer_data = db_ops.fetch_data(in_customer_query, ('1cc2ceef-fc07-44b9-9696-86d734d1dd59', user_id))
            if not informal_customer_data:
                inf_columns = ['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']
                informal_customer = pd.DataFrame(informal_customer_data, columns= inf_columns)
            else:
                informal_customer = pd.DataFrame(informal_customer_data)
                informal_customer.columns=['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']

            # Add product_type column as 'Informal' for informal_customer
            informal_customer['product_type'] = 'Women Informal'


            # Convert 'Register Date' to match the format of formal_customer ('YYYY-MM-DD')
            informal_customer['Register Date'] = pd.to_datetime(informal_customer['Register Date']).dt.strftime('%Y-%m-%d')

            # Fetching customer data for formal customers
            formal_customer_data = db_ops.fetch_data(formal_customer_query, (user_id,))
            if not formal_customer_data:
                f_columns=['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']
                formal_customer = pd.DataFrame(formal_customer_data, columns=f_columns)
            else:
                formal_customer = pd.DataFrame(formal_customer_data)
                formal_customer.columns=['kiyya_id', 'user_Id', 'Full Name', 'Phone Number', 'Saving Account', 'Register Date']

            # Add product_type column as 'Formal' for formal_customer
            formal_customer['product_type'] = 'Women Formal'
            params = account_numbers_tuple + account_query_tuple + (branch_code,)
            unique_customer_data = db_ops.fetch_data(unique_customer_query, params)
            if not unique_customer_data:
                u_columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
                unique_customer = pd.DataFrame(unique_customer_data, columns=u_columns)
            else:
                unique_customer = pd.DataFrame(unique_customer_data)
                unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

            conversion_customer_data = db_ops.fetch_data(conversion_customer_query, params)
            if not conversion_customer_data:
                c_columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
                conversion_customer = pd.DataFrame(conversion_customer_data, columns=c_columns)

            else:
                conversion_customer = pd.DataFrame(conversion_customer_data)
                conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            
            # Merge DataFrames on 'Saving Account'
            unique_conversation = pd.concat([unique_customer, conversion_customer], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(unique_conversation)
            bf_kiyya = "select saving_account from misseddata"
            bf_kiyya_customer = pd.DataFrame(db_ops.fetch_data(bf_kiyya))
            bf_kiyya_customer.columns=['Saving Account']
            
            unique_conversation = unique_conversation.merge(bf_kiyya_customer, on='Saving Account', how='left', indicator=True)

            # Filter rows where bf_kiyya_customer doesn't have a match in unique_conversation
            unique_not_in_bf_kiyya = unique_conversation[unique_conversation['_merge'] == 'left_only']

            # Drop the _merge column (optional)
            unique_conversation = unique_not_in_bf_kiyya.drop(columns=['_merge'])
            # st.write(unique_conversation)
            infrmal_formal = pd.concat([informal_customer, formal_customer], axis=0).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1)
            # st.write(combined_user)
            informal_formal_code = infrmal_formal.merge(combined_user, on='user_Id', how='inner')
            # st.write(informal_formal_code)
            # disbersed_by_recurate = pd.merge(infrmal_formal, unique_conversation, on='Saving Account', how='inner')
            # st.write(disbersed_by_recurate)
            full_disb = unique_conversation.merge(informal_formal_code, on='Saving Account', how='left').drop_duplicates(subset=['Saving Account'], keep='first')
            # st.write(full_disb)

       
            
            
            # st.write(merged_df)
            # Replace null values in user_Id of full_disb with user_Id from combined_user when branch_code matches
            full_disb['branch_code_y'] = np.where(
                full_disb['branch_code_y'].isnull(),    # Check if user_Id is null
                full_disb['branch_code_x'],    # Replace with user_Id_combined if condition is met
                full_disb['branch_code_y']              # Keep the original user_Id otherwise
            )
            # st.write(full_disb)

            # Drop the extra combined columns that were added during the merge
            full_disberment_user = pd.merge(full_disb, combined_user, left_on='branch_code_y', right_on='branch_code', how='outer')
            # st.write(full_disberment_user)
            full_disberment_user.drop_duplicates(subset=['branch_code'])
            # st.write(full_disberment_user)

            # Fetch target data based on branch code
            target_query = "SELECT target_id, user_id, target_amount, catagory, registered_date FROM kiyya_target WHERE user_id = %s"
            df_target = pd.DataFrame(
                db_ops.fetch_data(target_query,(branch_code,)))
            df_target.columns=['target_id', 'branch_code', 'Target Customer', 'Category', 'registered_date']
            # st.write(df_target)

            # Return the final merged dataframes
            return full_disberment_user, df_target


    else:
        # Fetch branch and district for the given username
        user_id_query = f"SELECT district FROM user_infos WHERE userName = '{username}'"
        user_id_result = db_ops.fetch_data(user_id_query)

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame()  # Return an empty DataFrame if no user is found

        # district = user_id_result[0][0]  # Assuming district is the first element in the first row of the result
        district = user_id_result[0][0]

        # Fetch dis_Id for the district
        district_query = f"SELECT dis_Id, district_name FROM district_list WHERE district_name = '{district}'"
        district_result = db_ops.fetch_data(district_query)
        if not district_result:
            st.warning("No district found with the given district name.")
            return pd.DataFrame()  # Return an empty DataFrame if no district is found

        dis_id = district_result[0][0]

        # Fetch branch code and branch name
        branch_code_query = f"SELECT dis_Id, branch_code, branch_name FROM branch_list WHERE dis_Id = '{dis_id}'"
        branch_code_result = db_ops.fetch_data(branch_code_query)
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
            db_ops.fetch_data(f"SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date, created_date FROM actual WHERE branch_code IN ({','.join(branch_code)})"), 
            columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date', 'created_date']
        )

        # Fetch target data
        df_target = pd.DataFrame(
            db_ops.fetch_data(f"SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date, created_date FROM target WHERE branch_code IN ({','.join(branch_code)})"),
            columns=['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date', 'created_date']
        )

        return act_dis_branch, df_actual, df_target



# Check if all branches exist in the branch_list table
def all_branch_code_exist(branch_code):
    
    query1 = "SELECT branch_code FROM branch_list"
    br_existing_data = db_ops.fetch_data(query1)
    
    existing_branches = [row['branch_code'] for row in br_existing_data]
    
    missing_branch_code = [branch for branch in branch_code if branch not in existing_branches]
    
    return missing_branch_code

# Format target_date to yy/mm/dd
def format_target_date(date):
    return date.strftime('%y/%m/%d')

# Check if any target_date from the uploaded file already exists in the target table
def any_target_date_exists(df):
    # Format the dates using the format_target_date function
    formatted_dates = tuple(df['disbursed_date'].apply(format_target_date).tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT disbursed_date FROM unique_intersection WHERE disbursed_date = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT disbursed_date FROM unique_intersection WHERE disbursed_date IN ({placeholders})"
        result = db_ops.fetch_data(query, formatted_dates)

    return len(result) > 0

def upload_to_unique(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['product_type'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['product_type'] == 'Women Formal']['saving_account'].tolist()
        # st.write(informal_accounts)
        # st.write(formal_accounts)

        # Initialize the dataframes to avoid referencing issues
        kiyya_customer_df = pd.DataFrame(columns=['Saving_Account', 'userId'])
        women_customer_df = pd.DataFrame(columns=['Saving_Account', 'userId'])

        
        # Prepare placeholders for informal_accounts in the query
        if informal_accounts:
            # Convert the list to tuple format
            informal_accounts_tuple = tuple(informal_accounts)
            
            if informal_accounts_tuple:
                # Handle case where there is only one element in the tuple
                if len(informal_accounts_tuple) == 1:
                    informal_accounts_tuple = f"('{informal_accounts_tuple[0]}')"
                else:
                    informal_accounts_tuple = str(informal_accounts_tuple)

                # Fetch kiyya_customer data for accounts in informal_accounts
                query = f"""
                    SELECT account_number, userId 
                    FROM kiyya_customer 
                    WHERE account_number IN {informal_accounts_tuple}
                        AND userId IN (SELECT userId FROM user_infos)
                """
                
                # kiyya_customer_data = db_ops.fetch_data(query)
                kiyya_customer_df = pd.DataFrame(db_ops.fetch_data(query))
                
                kiyya_customer_df.columns=['Saving_Account', 'userId']
                # st.write(kiyya_customer_df)
        # st.write(formal_accounts)
        if formal_accounts:
            formal_accounts_tuple = tuple(formal_accounts)
            
            # Ensure the tuple is not empty
            if formal_accounts_tuple:
                
                # Convert to a string format compatible with SQL, especially for single elements
                if len(formal_accounts_tuple) == 1:
                    formal_accounts_tuple = f"('{formal_accounts_tuple[0]}')"
                else:
                    formal_accounts_tuple = str(formal_accounts_tuple)
                
                query = f"""
                    SELECT account_no, crm_id 
                    FROM women_product_customer 
                    WHERE account_no IN {formal_accounts_tuple}
                        AND crm_id IN (SELECT userId FROM user_infos)
                """
                
                women_customer_df = pd.DataFrame(db_ops.fetch_data(query))
                women_customer_df.columns=['Saving_Account', 'userId']
                # st.write(women_customer_df)

        # Fetch branchcustomer data
        querry1 = "SELECT Saving_Account, userId FROM branchcustomer"
        branchcustomer_df = pd.DataFrame(db_ops.fetch_data(querry1))
        branchcustomer_df.columns=['Saving_Account', 'userId']

        # Fetch all user_info data
        querry2 = "SELECT userId, branch FROM user_infos where branch like 'ET%'"
        user_info_df = pd.DataFrame(db_ops.fetch_data(querry2))
        user_info_df.columns=['userId', 'branch_code']

      

        # Concatenate customer data in reverse order to prioritize kiyya_customer and women_customer
        combined_customer_df = pd.concat([branchcustomer_df, women_customer_df, kiyya_customer_df], ignore_index=True)
        combined_customer_df = combined_customer_df.drop_duplicates(subset=['Saving_Account'], keep='last')

        # # Close cursor after data fetching
        # cursor.close()

        # Merge combined customer data with user_info
        merged_df = combined_customer_df.merge(user_info_df, on='userId', how='left')

        # Merge the original df with merged_df on 'Saving_Account'
        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO unique_intersection (branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
             # Ensure data_to_insert is not empty
            if data_to_insert:
                # Make sure data_to_insert is a list of tuples
                if all(isinstance(item, tuple) for item in data_to_insert):
                    rows_inserted = db_ops.insert_many(insert_query, data_to_insert)
                    st.success(f"{rows_inserted} rows uploaded successfully.")
                    return True
                else:
                    st.error("Data to insert should be a list of tuples.")
            else:
                st.warning("No data to insert into the unique_intersection table.")
        except Exception as e:
            st.error(f"Error can't upload data: {e}")

    except Exception as e:
        st.error(f"Error: {e}")
        # db_ops.rollback()  # Rollback in case of error
        return False


def any_target_date_exists_conv(df):
     # Format the dates using the format_target_date function
    formatted_dates = tuple(df['convdisbursed_date'].apply(format_target_date).tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT disbursed_date FROM conversiondata WHERE disbursed_date = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT disbursed_date FROM conversiondata WHERE disbursed_date IN ({placeholders})"
        result = db_ops.fetch_data(query, formatted_dates)

    return len(result) > 0



def upload_to_conv(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['product_type'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['product_type'] == 'Women Formal']['saving_account'].tolist()
        # st.write(informal_accounts)
        # st.write(formal_accounts)

        # Initialize the dataframes to avoid referencing issues
        kiyya_customer_df = pd.DataFrame(columns=['Saving_Account', 'userId'])
        women_customer_df = pd.DataFrame(columns=['Saving_Account', 'userId'])

        
        # Prepare placeholders for informal_accounts in the query
        if informal_accounts:
            # Convert the list to tuple format
            informal_accounts_tuple = tuple(informal_accounts)
            
            if informal_accounts_tuple:
                # Handle case where there is only one element in the tuple
                if len(informal_accounts_tuple) == 1:
                    informal_accounts_tuple = f"('{informal_accounts_tuple[0]}')"
                else:
                    informal_accounts_tuple = str(informal_accounts_tuple)

                # Fetch kiyya_customer data for accounts in informal_accounts
                query = f"""
                    SELECT account_number, userId 
                    FROM kiyya_customer 
                    WHERE account_number IN {informal_accounts_tuple}
                        AND userId IN (SELECT userId FROM user_infos)
                """
                
                # kiyya_customer_data = db_ops.fetch_data(query)
                kiyya_customer_df = pd.DataFrame(db_ops.fetch_data(query))
                
                kiyya_customer_df.columns=['Saving_Account', 'userId']
                # st.write(kiyya_customer_df)

        if formal_accounts:
            formal_accounts_tuple = tuple(formal_accounts)
            
            # Ensure the tuple is not empty
            if formal_accounts_tuple:
                
                # Convert to a string format compatible with SQL, especially for single elements
                if len(formal_accounts_tuple) == 1:
                    formal_accounts_tuple = f"('{formal_accounts_tuple[0]}')"
                else:
                    formal_accounts_tuple = str(formal_accounts_tuple)
                
                query = f"""
                    SELECT account_no, crm_id 
                    FROM women_product_customer 
                    WHERE account_no IN {formal_accounts_tuple}
                        AND crm_id IN (SELECT userId FROM user_infos)
                """
                
                women_customer_df = pd.DataFrame(db_ops.fetch_data(query))
                women_customer_df.columns=['Saving_Account', 'userId']
                # st.write(women_customer_df)

        # Fetch branchcustomer data
        querry1 = "SELECT Saving_Account, userId FROM branchcustomer"
        branchcustomer_df = pd.DataFrame(db_ops.fetch_data(querry1))
        branchcustomer_df.columns=['Saving_Account', 'userId']

        # Fetch all user_info data
        querry2 = "SELECT userId, branch FROM user_infos where branch like 'ET%'"
        user_info_df = pd.DataFrame(db_ops.fetch_data(querry2))
        user_info_df.columns=['userId', 'branch_code']

      

        # Concatenate customer data in reverse order to prioritize kiyya_customer and women_customer
        combined_customer_df = pd.concat([branchcustomer_df, women_customer_df, kiyya_customer_df], ignore_index=True)
        combined_customer_df = combined_customer_df.drop_duplicates(subset=['Saving_Account'], keep='last')

        # # Close cursor after data fetching
        # cursor.close()

        # Merge combined customer data with user_info
        merged_df = combined_customer_df.merge(user_info_df, on='userId', how='left')

        # Merge the original df with merged_df on 'Saving_Account'
        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'convdisbursed_date']].values.tolist()]
        # st.write(data_to_insert)
        try:
            insert_query = """
                INSERT INTO conversiondata (branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
             # Ensure data_to_insert is not empty
            if data_to_insert:
                # Make sure data_to_insert is a list of tuples
                if all(isinstance(item, tuple) for item in data_to_insert):
                    rows_inserted = db_ops.insert_many(insert_query, data_to_insert)
                    st.success(f"{rows_inserted} rows uploaded successfully.")
                    return True
                else:
                    st.error("Data to insert should be a list of tuples.")
            else:
                st.warning("No data to insert into the unique_intersection table.")
        except Exception as e:
            st.error(f"Error can't upload data: {e}")

    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")

        # Rollback in case of error
        # db_ops.rollback()
        
        return False





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
