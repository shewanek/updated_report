from narwhals import col
import pandas as pd
import traceback
import streamlit as st
import hashlib
import re
# from typing import Optional, Tuple, Dict, Any
import json
from decimal import Decimal
from datetime import date, datetime, timedelta
# from TheStream.AddingCollection import fetch_data
from db_connection import DatabaseOperations
from session_manager import handle_websocket_errors  # initialize_session, update_activity, check_session_timeout
# from navigation import logout
import time
from typing import List, Tuple



# Initialize session when loading dependencies
# initialize_session()

# # Initialize DatabaseOperations once
# db_ops = DatabaseOperations()
@handle_websocket_errors
@st.cache_resource(show_spinner=False)
def get_db_ops():
    try:
        # Initialize session when loading dependencies
        # update_activity()
        return DatabaseOperations()
    except Exception as e:
        st.error("Could not connect to the database.")
        st.exception(e)
        raise

# Check session timeout on every interaction
# check_session_timeout()
db_ops = get_db_ops()

# Session timeout in minutes
SESSION_TIMEOUT = 20

def initialize_session(username):
    """Initialize session tracking"""
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()
        st.session_state.logged_in = True

        """Create or update a user session record"""
        query = """
        INSERT INTO user_sessions (username, is_active)
        VALUES (%s, TRUE)
        ON DUPLICATE KEY UPDATE
            is_active = VALUES(is_active),
            login_time = CURRENT_TIMESTAMP,
            last_activity = CURRENT_TIMESTAMP
        """
        db_ops.insert_data(query, (username,))

def update_activity():
    username = st.session_state.get("username", "")
    """Update the last activity timestamp"""
    st.session_state.last_activity = datetime.now()

    """Update the last activity timestamp"""
    query = """
    UPDATE user_sessions 
    SET last_activity = CURRENT_TIMESTAMP 
    WHERE username = %s AND is_active = TRUE
    """
    db_ops.update_data(query, (username,))

def check_session_timeout():
    """Check if session has expired and call logout if needed"""
    if 'last_activity' in st.session_state:
        inactive_duration = datetime.now() - st.session_state.last_activity
        if inactive_duration > timedelta(minutes=SESSION_TIMEOUT):  
            # Call your existing logout function
            st.session_state["logged_in"] = False
            # logout()
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state.clear()
            # st.rerun()
            st.info("Logged out successfully!")
            
            # sleep(0.5)
            st.switch_page("main.py")
            # Additional timeout-specific handling
            st.warning("Session timed out due to inactivity")
            time.sleep(0.5)
            st.rerun()


# # Add to your existing dependence.py
# @handle_websocket_errors
# def create_user_session(username):
#     """Create or update a user session record"""
#     query = """
#     INSERT INTO user_sessions (username, is_active)
#     VALUES (%s, TRUE)
#     ON DUPLICATE KEY UPDATE
#         is_active = VALUES(is_active),
#         login_time = CURRENT_TIMESTAMP,
#         last_activity = CURRENT_TIMESTAMP
#     """
#     return db_ops.insert_data(query, (username,))

# @handle_websocket_errors
# def update_user_activity(username):
#     """Update the last activity timestamp"""
#     query = """
#     UPDATE user_sessions 
#     SET last_activity = CURRENT_TIMESTAMP 
#     WHERE username = %s AND is_active = TRUE
#     """
#     return db_ops.update_data(query, (username,))

@handle_websocket_errors
def end_user_session(username):
    """Mark session as inactive"""
    query = "UPDATE user_sessions SET is_active = FALSE WHERE username = %s"
    return db_ops.update_data(query, (username,))

@handle_websocket_errors
def check_active_session(username):
    """Check if user has an active session within timeout"""
    query = """
    SELECT 1 FROM user_sessions 
    WHERE username = %s 
    AND is_active = TRUE 
    AND last_activity > NOW() - INTERVAL 2 MINUTE
    """
    return db_ops.fetch_one(query, (username,)) is not None

# @handle_websocket_errors
# def cleanup_expired_sessions():
#     """Clean up sessions older than 20 minutes"""
#     query = """
#     UPDATE user_sessions 
#     SET is_active = FALSE 
#     WHERE last_activity < NOW() - INTERVAL 20 MINUTE
#     """
#     return db_ops.update_data(query, ())



    


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

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_unquie(role, usrname, fy_start, fy_end):
    query = """
    SELECT d.district_name, bl.branch_code, bl.branch_name
    FROM branch_list bl
    JOIN district_list d ON bl.dis_Id = d.dis_Id
    """

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT uni_id, branch_code, product_type, disbursed_date FROM unique_intersection WHERE `Disbursed_Date` BETWEEN '{fy_start}' AND '{fy_end}'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    if not df_customer.empty:
        df_customer.columns = ['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date']
    else:
        df_customer = pd.DataFrame(columns=['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date'])
    
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'District', 'Branch', 'Product Type',  'Disbursed Date']]
    
    return df_combine






# @handle_session
@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_account(role, usrname, fy_start, fy_end):
    query = """
    SELECT d.district_name, bl.branch_code, bl.branch_name
    FROM branch_list bl
    JOIN district_list d ON bl.dis_Id = d.dis_Id
    """

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT uni_id, branch_code, product_type, disbursed_date FROM unique_intersection WHERE `Disbursed_Date` BETWEEN '{fy_start}' AND '{fy_end}'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    if not df_customer.empty:
        df_customer.columns = ['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date']
    else:
        df_customer = pd.DataFrame(columns=['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date'])

    conv_customer_query = f"SELECT conv_id, branch_code, product_type, disbursed_date FROM conversiondata WHERE `Disbursed_Date` BETWEEN '{fy_start}' AND '{fy_end}'"
    df_conv = pd.DataFrame(db_ops.fetch_data(conv_customer_query))
    if not df_conv.empty:
        df_conv.columns = ['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date']
    else:
        df_conv = pd.DataFrame(columns=['uniqueId', 'branch_code', 'Product Type', 'Disbursed Date'])
    
    df_data = pd.concat([df_customer, df_conv], axis=0).reset_index(drop=True).rename(lambda x: x + 1)
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_data, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'District', 'Branch', 'Product Type',  'Disbursed Date']]
    
    return df_combine

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_disbursment(role, usrname, fy_start, fy_end):
    query = """
    SELECT d.district_name, bl.branch_code, bl.branch_name
    FROM branch_list bl
    JOIN district_list d ON bl.dis_Id = d.dis_Id
    """

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT uni_id, branch_code, product_type, disbursed_amount, disbursed_date FROM unique_intersection WHERE `Disbursed_Date` BETWEEN '{fy_start}' AND '{fy_end}'"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    if not df_customer.empty:
        df_customer.columns = ['uniqueId', 'branch_code', 'Product Type', 'disbursed_amount', 'Disbursed Date']
    else:
        df_customer = pd.DataFrame(columns=['uniqueId', 'branch_code', 'Product Type', 'disbursed_amount', 'Disbursed Date'])

    conv_customer_query = f"SELECT conv_id, branch_code, product_type, disbursed_amount, disbursed_date FROM conversiondata WHERE `Disbursed_Date` BETWEEN '{fy_start}' AND '{fy_end}'"
    df_conv = pd.DataFrame(db_ops.fetch_data(conv_customer_query))
    if not df_conv.empty:
        df_conv.columns = ['uniqueId', 'branch_code', 'Product Type', 'disbursed_amount', 'Disbursed Date']
    else:
        df_conv = pd.DataFrame(columns=['uniqueId', 'branch_code', 'Product Type', 'disbursed_amount', 'Disbursed Date'])
    
    df_data = pd.concat([df_customer, df_conv], axis=0).reset_index(drop=True).rename(lambda x: x + 1)
    # Merge the two DataFrames based on 'userId'
    merged_df = pd.merge(df_user_infos, df_data, on='branch_code', how='inner')
    
    df_combine = merged_df[['uniqueId', 'District', 'Branch', 'Product Type', 'disbursed_amount', 'Disbursed Date']]
    
    return df_combine


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
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
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01' and (product_type = 'Wabbi' or product_type = 'Guyya')"
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


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_unquiekiyya(role, username):
    query = """
    SELECT ui.userId, ui.userName, ui.district, branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    """
    kiyya_informal = f"SELECT userId, fullName, phone_number, account_number, CAST(registered_date AS DATE) AS registered_date FROM kiyya_customer"
    kiya_formal = "SELECT crm_id, full_name, phone_number, account_no, registered_date FROM women_product_customer"

    kyya_infromall = db_ops.fetch_data(kiyya_informal)
    if not kyya_infromall:
        columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
        kyya_infromall = pd.DataFrame(kyya_infromall, columns=columns)
    else:
        kyya_infromall = pd.DataFrame(kyya_infromall)
        kyya_infromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']

    kyya_infromall['Product_Type'] = 'Women Informal'

    kyya_fromall = db_ops.fetch_data(kiya_formal)
    if not kyya_fromall:
        columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
        kyya_fromall = pd.DataFrame(kyya_fromall, columns=columns)
    else:
        kyya_fromall = pd.DataFrame(kyya_fromall)
        kyya_fromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
    
    # Add product_type column as 'Formal' for formal_customer
    kyya_fromall['Product_Type'] = 'Women Formal'
    # Fetch data and create DataFrame
    
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query))
    df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `Disbursed_Date` >= '2024-07-01' AND product_type IN ('Women Informal', 'Women Formal')"
    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    branch_customer = pd.concat([kyya_infromall, kyya_fromall], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
    # st.write(branch_customer)
    
    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]

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
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]

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

def load_districtuniquedata_try(username):
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


def load_branchdata(username):
    try:

        # Fetch userId based on username
        user_id_query = "SELECT userId, branch FROM user_infos WHERE userName = %s"
        user_id_result = db_ops.fetch_data(user_id_query, (username,))

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame(), 0  # Return an empty DataFrame if no user is found

        user_id = user_id_result[0]['userId']
        branch = user_id_result[0]['branch']

        # Fetch user_infos with selected columns
        query = """
        SELECT ui.userId, ui.userName, ui.district, ui.branch, bl.branch_name
        FROM user_infos ui
        JOIN branch_list bl ON ui.branch = bl.branch_code
        WHERE ui.userId = %s
        """
        df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (user_id,)))
        df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']

        # st.write(df_user_infos)

        # Ensure 'branch_code' is a string
        df_user_infos['branch_code'] = df_user_infos['branch_code'].astype(str)

        
        unique_customer_query = """
        SELECT uni_id, branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date 
        FROM unique_intersection 
        WHERE `disbursed_date` >= '2024-07-01'
            AND branch_code = %s
            AND product_type IN ('Wabbi', 'Guyya')
        """
        
        branch_customer_query = """
        SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name, Disbursed_date 
        FROM branchcustomer
        where userId = %s
        """

        customer_branch = db_ops.fetch_data(unique_customer_query, (branch,))
        if not customer_branch:
            columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            df_customer = pd.DataFrame(customer_branch, columns=columns)
        else:
            df_customer = pd.DataFrame(customer_branch)
            df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
        cust_br = db_ops.fetch_data(branch_customer_query, (user_id,))
        if not cust_br:
            columns=['userId', 'Full Name', 'Product_Type', 'Phone Number', 'TIN', 'Saving Account', 'Disbursed_Amount', 'Recruiter (Staff Name)','Disbursed_Date']
            branch_customer = pd.DataFrame(cust_br, columns=columns)
        else:
            branch_customer = pd.DataFrame(cust_br)
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

    except Exception as e:
        st.error("Failed to load branch data.")
        print("Database fetch error:", e)
        traceback.print_exc()
        return None, None, None, None
    
def load_branch_kiyya_data(username):
    try:

        # Fetch userId based on username
        user_id_query = "SELECT userId, branch FROM user_infos WHERE userName = %s"
        user_id_result = db_ops.fetch_data(user_id_query, (username,))

        if not user_id_result:
            st.warning("No user found with the given username.")
            return pd.DataFrame(), 0  # Return an empty DataFrame if no user is found

        user_id = user_id_result[0]['userId']
        branch = user_id_result[0]['branch']

        # Fetch user_infos with selected columns
        query = """
        SELECT ui.userId, ui.userName, ui.district, ui.branch, bl.branch_name
        FROM user_infos ui
        JOIN branch_list bl ON ui.branch = bl.branch_code
        WHERE ui.userId = %s
        """
        df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (user_id,)))
        df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']

        # st.write(df_user_infos)

        # Ensure 'branch_code' is a string
        df_user_infos['branch_code'] = df_user_infos['branch_code'].astype(str)

        
        unique_customer_query = """
        SELECT uni_id, branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date, upload_date 
        FROM unique_intersection 
        WHERE `disbursed_date` >= '2024-07-01'
            AND branch_code = %s
            AND product_type IN ('Women Informal', 'Women Formal')
        """
        
        kiyya_informal = "SELECT userId, fullName, phone_number, account_number, CAST(registered_date AS DATE) AS registered_date FROM kiyya_customer where userId = %s"
        kiya_formal = "SELECT crm_id, full_name, phone_number, account_no, registered_date FROM women_product_customer where crm_id = %s"

        kyya_infromall = db_ops.fetch_data(kiyya_informal,(user_id,))
        if not kyya_infromall:
            columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
            kyya_infromall = pd.DataFrame(kyya_infromall, columns=columns)
        else:
            kyya_infromall = pd.DataFrame(kyya_infromall)
            kyya_infromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']

        kyya_infromall['Product_Type'] = 'Women Informal'

        kyya_fromall = db_ops.fetch_data(kiya_formal, (user_id,))
        if not kyya_fromall:
            columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
            kyya_fromall = pd.DataFrame(kyya_fromall, columns=columns)
        else:
            kyya_fromall = pd.DataFrame(kyya_fromall)
            kyya_fromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
        
        # Add product_type column as 'Formal' for formal_customer
        kyya_fromall['Product_Type'] = 'Women Formal'

       
        df_customer = db_ops.fetch_data(unique_customer_query, (branch,))
        if not df_customer:
            columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            df_customer = pd.DataFrame(df_customer, columns=columns)
        else:
            df_customer = pd.DataFrame(df_customer)
            df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']


        branch_customer = pd.concat([kyya_infromall, kyya_fromall], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
        # st.write(branch_customer)
        unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
        unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
        unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]

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
        registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]
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

    except Exception as e:
        st.error("Failed to load branch data.")
        print("Database fetch error:", e)
        traceback.print_exc()
        return None, None, None, None



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

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
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
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `disbursed_date` >= '2024-07-01' AND product_type IN ('Wabbi', 'Guyya')"
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


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_districtuniquekiya(username):
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
    unique_customer_query = f"SELECT * FROM unique_intersection WHERE `disbursed_date` >= '2024-07-01' AND product_type IN ('Women Informal', 'Women Formal')"
    query = """
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = %s
    """
    # branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (district,)))
    df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])

    kiyya_informal = f"SELECT userId, fullName, phone_number, account_number, CAST(registered_date AS DATE) AS registered_date FROM kiyya_customer"
    kiya_formal = "SELECT crm_id, full_name, phone_number, account_no, registered_date FROM women_product_customer"

    kyya_infromall = db_ops.fetch_data(kiyya_informal)
    if not kyya_infromall:
        columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
        kyya_infromall = pd.DataFrame(kyya_infromall, columns=columns)
    else:
        kyya_infromall = pd.DataFrame(kyya_infromall)
        kyya_infromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']

    kyya_infromall['Product_Type'] = 'Women Informal'

    kyya_fromall = db_ops.fetch_data(kiya_formal)
    if not kyya_fromall:
        columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
        kyya_fromall = pd.DataFrame(kyya_fromall, columns=columns)
    else:
        kyya_fromall = pd.DataFrame(kyya_fromall)
        kyya_fromall.columns=['userId', 'Full Name', 'Phone Number', 'Saving Account', 'Disbursed_Date']
    
    # Add product_type column as 'Formal' for formal_customer
    kyya_fromall['Product_Type'] = 'Women Formal'
    # Fetch data and create DataFrame


    df_customer = pd.DataFrame(db_ops.fetch_data(unique_customer_query))
    df_customer.columns=['uniqueId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']

    branch_customer = pd.concat([kyya_infromall, kyya_fromall], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
    # st.write(branch_customer)
    unique_by_branch = pd.merge(branch_customer, df_customer, on='Saving Account', how='inner')
    unique_bybranch = pd.merge(unique_by_branch, df_user_infos, on='branch_code', how='inner')
    unique_cust_by_branch = unique_bybranch[['District', 'Branch', 'Full Name', 'Product Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]

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
    registed_by_branch = result_with_details[['District', 'Branch', 'Full Name', 'Product_Type', 'Phone Number', 'Saving Account', 'Disbursed_Date']]
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


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_districtuniquedash(username,fy_start,fy_end):
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
    unique_customer_query = f"SELECT uni_id, branch_code, saving_account, product_type, disbursed_date FROM unique_intersection WHERE `disbursed_date` BETWEEN '{fy_start}' AND '{fy_end}'"
    query = """
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district = %s
    """
    branch_customer_query = f"SELECT userId, Product_Type, Saving_Account, Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query, (district,)))
    df_user_infos.columns=['userId', 'userName', 'District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    fetch_data = db_ops.fetch_data(unique_customer_query)
    if not fetch_data:
        columns=['uniqueId', 'branch_code', 'Saving Account', 'Product Type', 'Disbursed Date']
        df_customer = pd.DataFrame(fetch_data, columns=columns)
    else:
        df_customer = pd.DataFrame(fetch_data)
        df_customer.columns=['uniqueId', 'branch_code', 'Saving Account', 'Product Type', 'Disbursed Date']

    branch_customer = pd.DataFrame(db_ops.fetch_data(branch_customer_query))
    branch_customer.columns=['userId', 'Product_Type', 'Saving Account', 'Disbursed_Date']

    
    # Perform a right join
    merged_df = pd.merge(df_customer, branch_customer,  on='Saving Account', how='left', indicator=True)
    
    merged_df = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    df_combine = merged_df[['uniqueId', 'userName', 'District', 'Branch', 'Product Type', 'Disbursed Date']]
    
    return  df_combine




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
        SELECT branch_code, saving_account, disbursed_amount, disbursed_date, uni_id
        FROM unique_intersection
        WHERE disbursed_date = %s
            AND product_type IN ('Wabbi', 'Guyya')
    """
    conversion_query = """
        SELECT branch_code, saving_account, disbursed_amount, disbursed_date, conv_id
        FROM conversiondata
        WHERE disbursed_date = %s
            AND product_type IN ('Wabbi', 'Guyya')
    """
    
    unique_data = db_ops.fetch_data(unique_query, (latest_disbursed_date,))
    conversion_data = db_ops.fetch_data(conversion_query, (latest_disbursed_date,))
    
    # Convert fetched data to DataFrames
    unique_df = pd.DataFrame(unique_data)
    unique_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'uni_id']
    conversion_df = pd.DataFrame(conversion_data)
    conversion_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'conv_id']
    
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
    
    


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_actual_vs_targetdata(role, username, fy_start, fy_end):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        try:
            # Fetch districts from user_infos
            # aggregate_and_insert_actual_data()
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual 
                WHERE branch_code IN ({placeholders})
                AND (actual_date BETWEEN %s AND %s)
            """

            # Fetch actual data using a parameterized query
            query_params = tuple(branch_codes) + (fy_start, fy_end)
            fetch_actual = db_ops.fetch_data(actual_query, query_params)  # Ensure the tuple is passed correctly
            # Debugging: Print the raw data fetched
            # st.write("Actual Data Fetched:", fetch_actual)

            # Check if fetch_actual has data
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                # Convert the data to a DataFrame and handle data type conversions
                df_actual = pd.DataFrame(fetch_actual)
                # Rename columns for 'actual' data
                df_actual.columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # Apply data type conversions
            df_actual['Actual Unique Customer'] = df_actual['Actual Unique Customer'].apply(convert_decimal)
            df_actual['Actual Number Of Account'] = df_actual['Actual Number Of Account'].apply(convert_decimal)
            df_actual['Actual Disbursed Amount'] = df_actual['Actual Disbursed Amount'].apply(convert_decimal)
            df_actual['Actual Date'] = df_actual['Actual Date'].apply(convert_date)
            # df_actual['created_date'] = df_actual['created_date'].apply(convert_date)
            # st.write(df_actual)
            
            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target WHERE (target_date BETWEEN %s AND %s)
            """
            tquery_params = (fy_start, fy_end)
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(fetch_target, columns=columns)
            else:
                # st.write(fetch_target)
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            # Apply data type conversions
            df_target['Target Unique Customer'] = df_target['Target Unique Customer'].apply(convert_decimal)
            df_target['Target Number Of Account'] = df_target['Target Number Of Account'].apply(convert_decimal)
            df_target['Target Disbursed Amount'] = df_target['Target Disbursed Amount'].apply(convert_decimal)
            df_target['Target Date'] = df_target['Target Date'].apply(convert_date)
            # df_target['created_date'] = df_target['created_date'].apply(convert_date)

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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual WHERE branch_code IN ({branch_codes_str})
                AND (actual_date BETWEEN %s AND %s)
            """
            query_params = tuple(branch_codes) + (fy_start, fy_end)
            fetch_actual = db_ops.fetch_data(actual_query, query_params)
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # st.write(df_actual)

            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target WHERE branch_code IN ({branch_codes_str})
                AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = tuple(branch_codes) + (fy_start, fy_end)
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual 
                WHERE branch_code = %s AND (actual_date BETWEEN %s AND %s)
            """
            query_params = (branch_code, fy_start, fy_end)
            fetch_actual = db_ops.fetch_data(actual_query, query_params)
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data
            target_query = """
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date 
                FROM target 
                WHERE branch_code = %s AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = (branch_code, fy_start, fy_end)
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

            
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date
                FROM actual 
                WHERE branch_code IN ({branch_codes_str})
                AND (actual_date BETWEEN %s AND %s)
            """
            query_params = tuple(branch_codes) + (fy_start, fy_end)
            fetch_actual = db_ops.fetch_data(actual_query, query_params)
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data using parameterized query
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target 
                WHERE branch_code IN ({branch_codes_str})
                AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = tuple(branch_codes) + (fy_start, fy_end)
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

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

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_salesuniquedata(username):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = "SELECT  district FROM user_infos WHERE userName = %s"
    user_id_result = db_ops.fetch_data(user_id_query, (username,))

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0]['district']  # Assuming userId is the first element in the first row of the result
    # Parse the JSON format district
    # districts = json.loads(district)

    # Convert the list of districts to a string suitable for the SQL IN clause
    # districts_str = ', '.join(f"'{district}'" for district in districts)

    if isinstance(district, str):
        try:
            districts = json.loads(district)
        except json.JSONDecodeError:
            districts = [district]  # If not JSON-encoded, treat it as a single district
    else:
        districts = [district]

    # Use placeholders for parameterized queries
    placeholders = ', '.join(['%s'] * len(districts))



    # SQL query using the IN clause
    # query = f"SELECT * FROM user_infos WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.userId, ui.userName, ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({placeholders})
    """
    branch_customer_query = f"SELECT userId, fullName, Product_Type, phoneNumber, TIN_Number, Saving_Account, disbursed_Amount, Staff_Name,Disbursed_date FROM branchcustomer"

    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query, tuple(districts)))
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

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_salesuniquedash(username, fy_start, fy_end):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # st.write(username)
    # Fetch userId based on username
    user_id_query = "SELECT  district FROM user_infos WHERE userName = %s "
    user_id_result = db_ops.fetch_data(user_id_query, (username,))

    if not user_id_result:
        st.warning("No user found with the given username.")
        return pd.DataFrame()  # Return an empty DataFrame if no user is found

    district = user_id_result[0]['district']  # Assuming userId is the first element in the first row of the result
    # Parse the JSON format district
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


    # SQL query using the IN clause
    # query = f"SELECT * FROM user_infos WHERE district IN ({districts_str})"
    query = f"""
    SELECT ui.district, bl.branch_code, bl.branch_name
    FROM user_infos ui
    JOIN branch_list bl ON ui.branch = bl.branch_code
    WHERE ui.district IN ({placeholders})
    """
   
    # Fetch data and create DataFrame
    df_user_infos = pd.DataFrame(db_ops.fetch_data(query, tuple(districts)))
    df_user_infos.columns=['District', 'branch_code', 'Branch']
    # df_user_infos = pd.DataFrame(db_ops.fetch_data("SELECT userId, userName, district, branch FROM user_infos"), columns=['userId', 'userName','District','Branch'])
    unique_customer_query = f"SELECT uni_id, branch_code, saving_account, product_type, disbursed_date FROM unique_intersection WHERE `Disbursed_Date`  BETWEEN '{fy_start}' AND '{fy_end}'"
    fetch_actual = db_ops.fetch_data(unique_customer_query)
    if not fetch_actual:
        columns = ['uniqueId', 'branch_code', 'Saving Account', 'Product Type', 'Disbursed Date']
        df_customer = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
    else:
        df_customer = pd.DataFrame(fetch_actual)
        df_customer.columns=['uniqueId', 'branch_code', 'Saving Account', 'Product Type', 'Disbursed Date']

    # Merge the two DataFrames based on 'userId'
    merged_df_uni = pd.merge(df_user_infos, df_customer, on='branch_code', how='inner')
    
    df_combine = merged_df_uni[['uniqueId', 'District', 'Branch',  'Product Type', 'Saving Account', 'Disbursed Date']]
    

    return df_combine

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
        print((e))

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
        # st.exception(e)

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

        # # Retrieve phone number from actualdata table
        # query4 = "SELECT saving_account FROM actualdata WHERE saving_account = %s"
        # result4 = db_ops.fetch_one(query4, (account,))

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
        return result1 is not None or result2 is not None or result3 is not None or result5 is not None or result6 is not None or result7 is not None or result8 is not None
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



@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_customer_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    
    if role == 'Admin' or role == 'under_admin' or role == 'collection_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        collection_query = """
                            SELECT 
                            Loan_Id,
                            MAX(Branch_Code) AS Branch_Code,
                            MAX(Customer_Name) AS Customer_Name,
                            MAX(Phone_Number) AS Phone_Number,
                            MAX(Saving_Account) AS Saving_Account,
                            SUM(Principal_Collected) AS Total_Principal_Collected,
                            SUM(Interest_Collected) AS Total_Interest_Collected,
                            SUM(Penality_Collected) AS Total_Penality_Collected,
                            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
                            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
                            MAX(Paid_Status) AS Paid_Status
                            
                        FROM actual_collection
                        WHERE Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
                        GROUP BY Loan_Id"""  
        conversion_query = """
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data 
        where Loan_Status = 'active'
            and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
        """
        arrears_query = """
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
        where Loan_Status = 'In Arrears'
            and Loan_Id not in (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
            and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        collection_query = f"""
        SELECT coll_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Principal_Collected, Interest_Collected, Penality_Collected, Collected_Date, Michu_Loan_Product, Paid_Status FROM actual_collection
        WHERE  Branch_Code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
        WHERE Loan_Status = 'active'
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
            SELECT 
            Loan_Id,
            MAX(Branch_Code) AS Branch_Code,
            MAX(Customer_Name) AS Customer_Name,
            MAX(Phone_Number) AS Phone_Number,
            MAX(Saving_Account) AS Saving_Account,
            SUM(Principal_Collected) AS Total_Principal_Collected,
            SUM(Interest_Collected) AS Total_Interest_Collected,
            SUM(Penality_Collected) AS Total_Penality_Collected,
            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
            MAX(Paid_Status) AS Paid_Status            
            FROM actual_collection
            GROUP BY Loan_Id
            WHERE Loan_Status = 'In Arrears'
            and Branch_Code IN ({branch_codes_str})
        """
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['coll_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['coll_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        # branch_codes = [row['branch_code'] for row in branch_code_result]
        # branch_codes_str = ', '.join(['%s'] * len(branch_codes))


        # Queries for different loan statuses
        collection_query = f"""
        SELECT 
        Loan_Id,
        MAX(Branch_Code) AS Branch_Code,
        MAX(Customer_Name) AS Customer_Name,
        MAX(Phone_Number) AS Phone_Number,
        MAX(Saving_Account) AS Saving_Account,
        SUM(Principal_Collected) AS Total_Principal_Collected,
        SUM(Interest_Collected) AS Total_Interest_Collected,
        SUM(Penality_Collected) AS Total_Penality_Collected,
        MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
        MAX(Michu_Loan_Product) AS Michu_Loan_Product,
        MAX(Paid_Status) AS Paid_Status            
        FROM actual_collection
        WHERE Branch_Code IN ({branch_codes_str})
            and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
        GROUP BY Loan_Id
        
        """
        conversion_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
        WHERE Loan_Status = 'active'
            and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
        where Loan_Status = 'In Arrears'
            and Loan_Id NOT IN (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
            and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
            and Branch_Code IN ({branch_codes_str})
        """

        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Branch User':
        try:
            user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
            user_branch_code = db_ops.fetch_data(user_query)
            code_query = f"""
            SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
            JOIN district_list dr ON br.dis_Id = dr.dis_Id
            WHERE br.branch_code = '{user_branch_code[0]['branch']}'
            """
            branch_result = db_ops.fetch_data(code_query)
            df_branch = pd.DataFrame(branch_result)
            df_branch.columns=['District', 'branch_code', 'Branch']

            branch_codes = [row['branch_code'] for row in branch_result]
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))
            # st.write(branch_codes_str)

            collection_query = f"""
            SELECT 
            Loan_Id,
            MAX(Branch_Code) AS Branch_Code,
            MAX(Customer_Name) AS Customer_Name,
            MAX(Phone_Number) AS Phone_Number,
            MAX(Saving_Account) AS Saving_Account,
            SUM(Principal_Collected) AS Total_Principal_Collected,
            SUM(Interest_Collected) AS Total_Interest_Collected,
            SUM(Penality_Collected) AS Total_Penality_Collected,
            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
            MAX(Paid_Status) AS Paid_Status            
            FROM actual_collection
            WHERE Branch_Code IN ({branch_codes_str})
                and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
            GROUP BY Loan_Id
            
            """
            conversion_query = f"""
            SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
            WHERE Loan_Status = 'active'
                and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
                and branch_code IN ({branch_codes_str})
            """
            arrears_query = f"""
            SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
            where Loan_Status = 'In Arrears'
                and Loan_Id NOT IN (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
                and Michu_Loan_Product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
                and Branch_Code IN ({branch_codes_str})
            """
            
            # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
            collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
            if not collectiond:
                df_collection = pd.DataFrame(collectiond, columns=[ 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
            else:
                df_collection = pd.DataFrame(collectiond)
                df_collection.columns=[ 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
                # st.write(df_collection)
            
            conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
            if not conversion:
                df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
            else:
                df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
            arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
            if not arrears:
                df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
            else:
                df_arrears = pd.DataFrame(arrears)
                df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

            df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
            df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
            df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


            df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
            df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
            df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

            return df_combine_collection, df_combine_conversion, df_combine_arrears
        except Exception as e:
            st.error("Failed to fetch data")
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
    
    # elif role == 'collection_admin':
    #     code_query = """
    #     SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
    #     JOIN district_list dr ON br.dis_Id = dr.dis_Id
    #     """
    #     collection_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'collection'
    #     """
    #     conversion_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'conversion'
    #     """
    #     arrears_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'In Arrears'
    #     """
    #     df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
    #     df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

    #     df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
    #     df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
    #     df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


    #     df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
    #     df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    #     df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

    #     return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        collection_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'collection'
        AND branch_code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'conversion'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
        df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    else:
        st.warning("No data for this user")
        quit()
        return None


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_customer_detail_informal(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    
    if role == 'Admin' or role == 'under_admin' or role == 'collection_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        collection_query = """
                            SELECT 
                            Loan_Id,
                            MAX(Branch_Code) AS Branch_Code,
                            MAX(Customer_Name) AS Customer_Name,
                            MAX(Phone_Number) AS Phone_Number,
                            MAX(Saving_Account) AS Saving_Account,
                            SUM(Principal_Collected) AS Total_Principal_Collected,
                            SUM(Interest_Collected) AS Total_Interest_Collected,
                            SUM(Penality_Collected) AS Total_Penality_Collected,
                            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
                            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
                            MAX(Paid_Status) AS Paid_Status
                            
                        FROM actual_collection
                        WHERE Michu_Loan_Product IN ('Guyya', 'Women Informal')
                        GROUP BY Loan_Id"""  
        conversion_query = """
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data 
        where Loan_Status = 'active'
            and Michu_Loan_Product IN ('Guyya', 'Women Informal')
        """
        arrears_query = """
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
        where Loan_Status = 'In Arrears'
            and Loan_Id not in (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
            and Michu_Loan_Product IN ('Guyya', 'Women Informal')
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        collection_query = f"""
        SELECT coll_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Principal_Collected, Interest_Collected, Penality_Collected, Collected_Date, Michu_Loan_Product, Paid_Status FROM actual_collection
        WHERE  Branch_Code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
        WHERE Loan_Status = 'active'
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
            SELECT 
            Loan_Id,
            MAX(Branch_Code) AS Branch_Code,
            MAX(Customer_Name) AS Customer_Name,
            MAX(Phone_Number) AS Phone_Number,
            MAX(Saving_Account) AS Saving_Account,
            SUM(Principal_Collected) AS Total_Principal_Collected,
            SUM(Interest_Collected) AS Total_Interest_Collected,
            SUM(Penality_Collected) AS Total_Penality_Collected,
            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
            MAX(Paid_Status) AS Paid_Status            
            FROM actual_collection
            GROUP BY Loan_Id
            WHERE Loan_Status = 'In Arrears'
            and Branch_Code IN ({branch_codes_str})
        """
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['coll_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['coll_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        # branch_codes = [row['branch_code'] for row in branch_code_result]
        # branch_codes_str = ', '.join(['%s'] * len(branch_codes))


        # Queries for different loan statuses
        collection_query = f"""
        SELECT 
        Loan_Id,
        MAX(Branch_Code) AS Branch_Code,
        MAX(Customer_Name) AS Customer_Name,
        MAX(Phone_Number) AS Phone_Number,
        MAX(Saving_Account) AS Saving_Account,
        SUM(Principal_Collected) AS Total_Principal_Collected,
        SUM(Interest_Collected) AS Total_Interest_Collected,
        SUM(Penality_Collected) AS Total_Penality_Collected,
        MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
        MAX(Michu_Loan_Product) AS Michu_Loan_Product,
        MAX(Paid_Status) AS Paid_Status            
        FROM actual_collection
        WHERE Branch_Code IN ({branch_codes_str})
            and Michu_Loan_Product IN ('Guyya', 'Women Informal')
        GROUP BY Loan_Id
        
        """
        conversion_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
        WHERE Loan_Status = 'active'
            and Michu_Loan_Product IN ('Guyya', 'Women Informal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
        where Loan_Status = 'In Arrears'
            and Loan_Id NOT IN (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
            and Michu_Loan_Product IN ('Guyya', 'Women Informal')
            and Branch_Code IN ({branch_codes_str})
        """

        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
        arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Branch User':
        try:
            user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
            user_branch_code = db_ops.fetch_data(user_query)
            code_query = f"""
            SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
            JOIN district_list dr ON br.dis_Id = dr.dis_Id
            WHERE br.branch_code = '{user_branch_code[0]['branch']}'
            """
            branch_result = db_ops.fetch_data(code_query)
            df_branch = pd.DataFrame(branch_result)
            df_branch.columns=['District', 'branch_code', 'Branch']

            branch_codes = [row['branch_code'] for row in branch_result]
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))
            # st.write(branch_codes_str)

            collection_query = f"""
            SELECT 
            Loan_Id,
            MAX(Branch_Code) AS Branch_Code,
            MAX(Customer_Name) AS Customer_Name,
            MAX(Phone_Number) AS Phone_Number,
            MAX(Saving_Account) AS Saving_Account,
            SUM(Principal_Collected) AS Total_Principal_Collected,
            SUM(Interest_Collected) AS Total_Interest_Collected,
            SUM(Penality_Collected) AS Total_Penality_Collected,
            MAX(Collected_Date) AS Collected_Date,  -- Latest collection date
            MAX(Michu_Loan_Product) AS Michu_Loan_Product,
            MAX(Paid_Status) AS Paid_Status            
            FROM actual_collection
            WHERE Branch_Code IN ({branch_codes_str})
                and Michu_Loan_Product IN ('Guyya', 'Women Informal')
            GROUP BY Loan_Id
            
            """
            conversion_query = f"""
            SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status, conversion_date FROM arrears_data
            WHERE Loan_Status = 'active'
                and Michu_Loan_Product IN ('Guyya', 'Women Informal')
                and branch_code IN ({branch_codes_str})
            """
            arrears_query = f"""
            SELECT arr_Id, Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, Loan_Status FROM arrears_data 
            where Loan_Status = 'In Arrears'
                and Loan_Id NOT IN (select Loan_Id from actual_collection where Paid_Status = 'CLOSED')
                and Michu_Loan_Product IN ('Guyya', 'Women Informal')
                and Branch_Code IN ({branch_codes_str})
            """
            
            # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
            collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
            if not collectiond:
                df_collection = pd.DataFrame(collectiond, columns=[ 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
            else:
                df_collection = pd.DataFrame(collectiond)
                df_collection.columns=[ 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
                # st.write(df_collection)
            
            conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
            if not conversion:
                df_conversion = pd.DataFrame(conversion, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date'])
            else:
                df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']
            arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
            if not arrears:
                df_arrears = pd.DataFrame(arrears, columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status'])
            else:
                df_arrears = pd.DataFrame(arrears)
                df_arrears.columns=['arr_Id', 'Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']

            df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
            df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
            df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


            df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
            df_combine_conversion = df_merged_conversion[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status', 'Conversion Date']]
            df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

            return df_combine_collection, df_combine_conversion, df_combine_arrears
        except Exception as e:
            st.error("Failed to fetch data")
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
    
    # elif role == 'collection_admin':
    #     code_query = """
    #     SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
    #     JOIN district_list dr ON br.dis_Id = dr.dis_Id
    #     """
    #     collection_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'collection'
    #     """
    #     conversion_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'conversion'
    #     """
    #     arrears_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'In Arrears'
    #     """
    #     df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
    #     df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

    #     df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
    #     df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
    #     df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


    #     df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
    #     df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    #     df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

    #     return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        collection_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'collection'
        AND branch_code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'conversion'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
        df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
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
        LIMIT 1
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

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
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
        # phonenumber_processed = "+251" + phonenumber[1:]
        userId  = get_id(username)
        if userId:
            query1 = """
                INSERT INTO kiyya_customer_status(userId, phone_number, account_number, total_score, eligible)
                VALUES (%s, %s, %s, %s, %s)
            """

            # Insert customer information into the customer table
            query = """
                INSERT INTO kiyya_customer(userId, fullName, phone_number, account_number, customer_ident_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, daily_sales, purpose_of_loan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(query, (userId, fullName, processed_phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan))
            # db_ops.insert_data(query1, (userId, phonenumber_processed, account_number, eligible, total_score))
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create customer due to an unexpected error.")
        st.exception(e)
        return False
    
def kiyya_customer_notegible(username, fullName, phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan, phonenumber, account_number, eligible, total_score):
    try:
        processed_phone_number = "+251" + phone_number[1:]
        phonenumber_processed = "+251" + phonenumber[1:]
        userId  = get_id(username)
        if userId:

            #  # Check if account_number exists in kiyya_customer_notelgiable table
            # query_check = """
            #     SELECT account_number FROM kiyya_customer_notelgiable WHERE account_number = %s
            # """
            # result = db_ops.fetch_one(query_check, (account_number,))
            # if result:
            #     # If account_number exists, skip registration but return success
            #     # st.warning("Account number already exists in the database. No new entry created.")
            #     return True



            query1 = """
                INSERT INTO kiyya_customer_status(userId, phone_number, account_number, total_score, eligible)
                VALUES (%s, %s, %s, %s, %s)
            """

            # Insert customer information into the customer table
            query = """
                INSERT INTO kiyya_customer_notelgiable(userId, fullName, phone_number, account_number, customer_ident_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, daily_sales, purpose_of_loan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(query, (userId, fullName, processed_phone_number, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan))
            db_ops.insert_data(query1, (userId, phonenumber_processed, account_number, eligible, total_score))
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create customer due to an unexpected error.")
        st.exception(e)
        return False

@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
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
    unique_cust_by_crm = unique_by_crm[['kiyya_id', 'branch_code', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan',  'Disbursed Amount', 'Disbursed Date']]
    conv_cust_by_crm = conv_by_crm[['kiyya_id', 'branch_code', 'userId', 'Customer Name', 'Product Type', 'Phone Number', 'Saving Account', 'Customer Identification  Type', 'Gender', 'Marital Status', 'Date of Birth', 'Region', 'Zone/Subcity', 'Woreda', 'Educational Level', 'Business Sector', 'Line of Business', 'Initial Working Capital', 'Source of Initial Capital', 'Daily Sales', 'Purpose of the loan',  'Disbursed Amount', 'Disbursed Date']]
    
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


def aggregate_and_insert_actual_data_kiyya():
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
        SELECT MAX(actual_date) as actual_date FROM actual_kiyya WHERE actual_date = %s
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
        SELECT branch_code, saving_account, disbursed_amount, disbursed_date, uni_id
        FROM unique_intersection
        WHERE disbursed_date = %s
            AND product_type IN ('Women Informal', 'Women Formal') 
    """
    conversion_query = """
        SELECT branch_code, saving_account, disbursed_amount, disbursed_date, conv_id
        FROM conversiondata
        WHERE disbursed_date = %s
            AND product_type IN ('Women Informal', 'Women Formal') 
    """
    
    unique_data = db_ops.fetch_data(unique_query, (latest_disbursed_date,))
    conversion_data = db_ops.fetch_data(conversion_query, (latest_disbursed_date,))
    
    # Convert fetched data to DataFrames
    unique_df = pd.DataFrame(unique_data)
    unique_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'uni_id']
    conversion_df = pd.DataFrame(conversion_data)
    conversion_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'conv_id']
    
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
            SELECT MAX(actual_date) as actual_date FROM actual_kiyya 
                WHERE branch_code = %s AND actual_date = %s
        """
        # db_ops.fetch_one(check_record_query, (row['branch_code'], row['actual_date']))
        record_exists = db_ops.fetch_one(check_record_query, (row['branch_code'], row['actual_date']))
        
        if not record_exists['actual_date']:
            # Insert the new record only if it doesn't already exist
            querry = """
                INSERT INTO actual_kiyya (branch_code, unique_actual, account_actual, disbursment_actual, actual_date)
                VALUES (%s, %s, %s, %s, %s)
            """
            db_ops.insert_data(querry, (row['branch_code'], row['unique_actual'], row['account_actual'], row['disbursment_actual'], row['actual_date']))
    


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_kiyya_actual_vs_targetdata(role, username, fy_start, fy_end):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        try:
            # Fetch districts from user_infos
            # aggregate_and_insert_actual_data_kiyya()
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_kiyya 
                WHERE branch_code IN ({placeholders})
                AND (actual_date BETWEEN %s AND %s)
            """
            query_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end dates

            # Fetch actual data using a parameterized query
            fetch_actual = db_ops.fetch_data(actual_query, query_params)  # Ensure the tuple is passed correctly
            # Debugging: Print the raw data fetched
            # st.write("Actual Data Fetched:", fetch_actual)

            # # Check if fetch_actual has data
            # if not fetch_actual:
            #     st.warning("No actual data found for the selected branch codes.")
            #     return pd.DataFrame()

            # Convert the data to a DataFrame and handle data type conversions
            
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # Rename columns for 'actual' data
            # df_actual.columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # Apply data type conversions
            df_actual['Actual Unique Customer'] = df_actual['Actual Unique Customer'].apply(convert_decimal)
            df_actual['Actual Number Of Account'] = df_actual['Actual Number Of Account'].apply(convert_decimal)
            df_actual['Actual Disbursed Amount'] = df_actual['Actual Disbursed Amount'].apply(convert_decimal)
            df_actual['Actual Date'] = df_actual['Actual Date'].apply(convert_date)
            # df_actual['created_date'] = df_actual['created_date'].apply(convert_date)
            # st.write(df_actual)
            
            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target_kiyya WHERE target_date BETWEEN %s AND %s
            """
            tquery_params = (fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            # st.write(fetch_target)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(fetch_target, columns= columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            # Apply data type conversions
            df_target['Target Unique Customer'] = df_target['Target Unique Customer'].apply(convert_decimal)
            df_target['Target Number Of Account'] = df_target['Target Number Of Account'].apply(convert_decimal)
            df_target['Target Disbursed Amount'] = df_target['Target Disbursed Amount'].apply(convert_decimal)
            df_target['Target Date'] = df_target['Target Date'].apply(convert_date)
            # df_target['created_date'] = df_target['created_date'].apply(convert_date)

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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_kiyya WHERE branch_code IN ({branch_codes_str}) AND (actual_date BETWEEN %s AND %s)
            """
            query_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end dates
            fetch_actual = db_ops.fetch_data(actual_query, query_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # st.write(df_actual)

            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target_kiyya WHERE branch_code IN ({branch_codes_str}) AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = tuple(branch_codes) + (fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            # st.write(fetch_target)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(fetch_target, columns= columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            
            # df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_kiyya 
                WHERE branch_code = %s AND (actual_date BETWEEN %s AND %s)
            """
            query_params = (branch_code, fy_start, fy_end)  # Combine branch code with fiscal year start and end dates
            fetch_actual = db_ops.fetch_data(actual_query, query_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data
            target_query = """
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date 
                FROM target_kiyya 
                WHERE branch_code = %s AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = (branch_code, fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            # st.write(fetch_target)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(fetch_target, columns= columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            
            # df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

            
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
                SELECT actual_Id, branch_code, unique_actual, account_actual, disbursment_actual, actual_date
                FROM actual_kiyya 
                WHERE branch_code IN ({branch_codes_str}) AND (actual_date BETWEEN %s AND %s)
            """
            query_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end dates
            fetch_actual = db_ops.fetch_data(actual_query, query_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with specified columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data using parameterized query
            target_query = f"""
                SELECT target_Id, branch_code, unique_target, account_target, disbursment_target, target_date
                FROM target_kiyya 
                WHERE branch_code IN ({branch_codes_str}) AND (target_date BETWEEN %s AND %s)
            """
            tquery_params = tuple(branch_codes) + (fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquery_params)
            # st.write(fetch_target)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(fetch_target, columns= columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            
            # df_target.columns = ['target_Id', 'Branch Code', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()




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
    st.write(result)
    return len(result) > 0

def any_targetperpro_date_exists(df):
    # Format the dates using the format_target_date function
    formatted_dates = tuple(df['target_date'].apply(format_target_date).tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT target_date FROM target_per_product WHERE target_date = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT target_date FROM target_per_product WHERE target_date IN ({placeholders})"
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
                kcinf = db_ops.fetch_data(query)
                if not kcinf:
                    columns=['Saving_Account', 'userId']
                    kiyya_customer_df = pd.DataFrame(kcinf, columns=columns)
                else:
                    kiyya_customer_df = pd.DataFrame(kcinf)
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
                wcf = db_ops.fetch_data(query)
                if not wcf:
                    columns=['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(wcf, columns=columns)
                else:
                    women_customer_df = pd.DataFrame(wcf)
                    women_customer_df.columns=['Saving_Account', 'userId']
                

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

                    arrears_accounts = final_merged_df['saving_account'].tolist()
                    # st.write(arrears_accounts)
                    if arrears_accounts:
                        arrears_accounts_tuple = tuple(arrears_accounts)
                        if len(arrears_accounts_tuple) == 1:
                            arrears_accounts_tuple = f"('{arrears_accounts_tuple[0]}')"
                        else:
                            arrears_accounts_tuple = str(arrears_accounts_tuple)

                        update_query = f"""
                            UPDATE arrers_conversion 
                            SET statuss = 'active'
                            WHERE saving_account IN {arrears_accounts_tuple}
                        """

                        update_query1 = f"""
                            UPDATE closed 
                            SET statuss = 'active'
                            WHERE Saving_Account IN {arrears_accounts_tuple}
                        """
                        update_query2 = f"""
                            UPDATE prospect_data 
                            SET statuss = 'active'
                            WHERE saving_account IN {arrears_accounts_tuple}
                        """
                        update_query3 = f"""
                            UPDATE rejected_customer 
                            SET statuss = 'active'
                            WHERE Saving_Account IN {arrears_accounts_tuple}
                        """
                        rows_updated = db_ops.update_data(update_query)
                        rows_updated1 = db_ops.update_data(update_query1)
                        rows_updated2 = db_ops.update_data(update_query2)
                        rows_updated3 = db_ops.update_data(update_query3)
                        aggregate_and_insert_actual_data_per_product_anydate()
                        st.success(f"{rows_updated}, {rows_updated1}, {rows_updated2}, {rows_updated3} records updated to active.")



                    return True
                else:
                    st.error("Data to insert should be a list of tuples.")
            else:
                st.warning("No data to insert into the unique_intersection table.")
        except Exception as e:
            st.error(f"Error can't upload data: {e}")
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal

    except Exception as e:
        st.error(f"Error:")
        # Print a full stack trace for debugging
        print("Database fetch error:", e)
        traceback.print_exc()  # This prints the full error trace to the terminal
        # db_ops.rollback()  # Rollback in case of error
        return False


def upload_to_target(df):
    try:
        insert_query = """
            INSERT INTO target_per_product (branch_code, product_type, unique_target, account_target, disbursment_target, target_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        data_to_insert = [tuple(x) for x in df[['branch_code', 'product_type', 'unique_target', 'account_target', 'disbursment_target', 'target_date']].values.tolist()]
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
        # Print a full stack trace for debugging
        print("Database fetch error:", e)
        traceback.print_exc()  # This prints the full error trace to the terminal
        



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
                
                kcinf = db_ops.fetch_data(query)
                # kiyya_customer_data = db_ops.fetch_data(query)
                if not kcinf:
                    columns=['Saving_Account', 'userId']
                    kiyya_customer_df = pd.DataFrame(kcinf, columns=columns)
                else:
                    kiyya_customer_df = pd.DataFrame(kcinf)    
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
                wcf = db_ops.fetch_data(query)
                if not wcf:
                    columns=['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(wcf, columns=columns)
                else:
                    women_customer_df = pd.DataFrame(wcf)
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

                    arrears_accounts = final_merged_df['saving_account'].tolist()
                    # st.write(arrears_accounts)
                    if arrears_accounts:
                        arrears_accounts_tuple = tuple(arrears_accounts)
                        if len(arrears_accounts_tuple) == 1:
                            arrears_accounts_tuple = f"('{arrears_accounts_tuple[0]}')"
                        else:
                            arrears_accounts_tuple = str(arrears_accounts_tuple)

                        update_query = f"""
                            UPDATE arrers_conversion 
                            SET statuss = 'active'
                            WHERE saving_account IN {arrears_accounts_tuple}
                        """
                        update_query1 = f"""
                            UPDATE closed 
                            SET statuss = 'active'
                            WHERE Saving_Account IN {arrears_accounts_tuple}
                        """
                        update_query2 = f"""
                            UPDATE prospect_data 
                            SET statuss = 'active'
                            WHERE saving_account IN {arrears_accounts_tuple}
                        """
                        update_query3 = f"""
                            UPDATE rejected_customer 
                            SET statuss = 'active'
                            WHERE Saving_Account IN {arrears_accounts_tuple}
                        """
                        rows_updated = db_ops.update_data(update_query)
                        rows_updated1 = db_ops.update_data(update_query1)
                        rows_updated2 = db_ops.update_data(update_query2)
                        rows_updated3 = db_ops.update_data(update_query3)
                        aggregate_and_insert_actual_data_per_product_anydate()
                        

                        st.success(f"{rows_updated}, {rows_updated1}, {rows_updated2}, {rows_updated3} records updated to active.")

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



def load_crmdata(username):
    # CRM user query
    crm_user_query = """
        SELECT DISTINCT dr.crm_id, br.full_name, br.sub_process, br.employe_id 
        FROM crm_list br
        inner JOIN crm_user dr ON br.employe_id = dr.employe_id
        where dr.username = %s
        """
   
    # Fetching the result using a parameterized query to prevent SQL injection
    result = db_ops.fetch_data(crm_user_query, (username,))
    # st.write(result)

    # Check if a result was returned before accessing it
    if result:
        user_id = result[0]['crm_id']
        branch_code = result[0]['employe_id']  

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
        account_query = "SELECT account_number FROM kiyya_customer WHERE userId != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND userId = %s"
        account_query_formal = "SELECT account_no FROM women_product_customer WHERE crm_id != '1cc2ceef-fc07-44b9-9696-86d734d1dd59' AND crm_id = %s"

        # Execute the query, unpacking the tuple using *
        account_result = db_ops.fetch_data(account_query, (user_id,))
        # st.write(account_result)
        account_query_f = db_ops.fetch_data(account_query_formal, (user_id,))
        # st.write(account_result)
        # Check if the results are empty and set to an empty tuple if they are
        account_numbers_tuple = tuple([row['account_number'] for row in account_result]) if account_result else ()
        account_query_tuple = tuple([row['account_no'] for row in account_query_f]) if account_query_f else ()

        # Generate placeholders for SQL query, only if tuples are not empty
        if account_numbers_tuple:
            placeholders2 = ', '.join(['%s'] * len(account_numbers_tuple))
        else:
            placeholders2 = ''

        if account_query_tuple:
            placeholders3 = ', '.join(['%s'] * len(account_query_tuple))
        else:
            placeholders3 = ''



        # Unique customer query for disbursements after October 1st, 2024
        unique_customer_query = f"""
            SELECT * 
            FROM unique_intersection 
            WHERE product_type IN ('Women Informal', 'Women Formal') 
            AND disbursed_date >= '2024-10-01'
            AND (
                {'saving_account IN (' + placeholders2 + ')' if placeholders2 else '1=0'}
                OR
                {'saving_account IN (' + placeholders3 + ')' if placeholders3 else '1=0'}
            )
            AND saving_account NOT IN (
                SELECT saving_account 
                FROM unique_intersection 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date < '2024-10-01'
            )
        """
        
        # Conversion customer query for similar data
        conversion_customer_query = f"""
            SELECT * 
            FROM conversiondata 
            WHERE product_type IN ('Women Informal', 'Women Formal') 
            AND disbursed_date >= '2024-10-01' 
            AND (
                {'saving_account IN (' + placeholders2 + ')' if placeholders2 else '1=0'}
                OR
                {'saving_account IN (' + placeholders3 + ')' if placeholders3 else '1=0'}
            )
            AND saving_account NOT IN (
                SELECT saving_account 
                FROM conversiondata 
                WHERE product_type IN ('Women Informal', 'Women Formal') 
                AND disbursed_date < '2024-10-01'
            )
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

        # st.write(informal_customer)
        # st.write(formal_customer)
        # Add product_type column as 'Formal' for formal_customer
        formal_customer['product_type'] = 'Women Formal'
        params = account_numbers_tuple + account_query_tuple
        unique_customer_data = db_ops.fetch_data(unique_customer_query, params)
        if not unique_customer_data:
            u_columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            unique_customer = pd.DataFrame(unique_customer_data, columns=u_columns)
        else:
            unique_customer = pd.DataFrame(unique_customer_data)
            unique_customer.columns=['uniqId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
        # st.write(unique_customer)
        conversion_customer_data = db_ops.fetch_data(conversion_customer_query, params)
        if not conversion_customer_data:
            c_columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
            conversion_customer = pd.DataFrame(conversion_customer_data, columns=c_columns)

        else:
            conversion_customer = pd.DataFrame(conversion_customer_data)
            conversion_customer.columns=['conId', 'branch_code', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date', 'Upload Date']
        # st.write(conversion_customer)
        # Merge DataFrames on 'Saving Account'
        # Filter out DataFrames with all-NaN columns
        if  conversion_customer_data or  unique_customer_data:
            non_empty_dfs = [df for df in [unique_customer, conversion_customer] if not df.isna().all().all()]

            # Concatenate only non-empty DataFrames
            unique_conversation = pd.concat(non_empty_dfs, axis=0).drop_duplicates(
                subset=['Saving Account'], keep='first'
            ).reset_index(drop=True).rename(lambda x: x + 1)
        else:
            unique_conversation = pd.concat([unique_customer, conversion_customer], axis=0).drop_duplicates(subset=['Saving Account'], keep='first').reset_index(drop=True).rename(lambda x: x + 1)
        # st.write(unique_conversation)
        bf_kiyya = "select saving_account from misseddata"
        bf_kiyya_customer = pd.DataFrame(db_ops.fetch_data(bf_kiyya))
        bf_kiyya_customer.columns=['Saving Account']
        # st.write(bf_kiyya_customer)
        
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

        # Query to fetch user information for the given username
        women_customer_queryy = """
            SELECT DISTINCT br.full_name, br.sub_process, br.employe_id 
            FROM crm_list br
            inner JOIN crm_user dr ON br.employe_id = dr.employe_id
            where dr.username = %s
        """
        
        women_customer_listt = pd.DataFrame(db_ops.fetch_data(women_customer_queryy, (username,)))
        women_customer_listt.columns=['Recruited by', 'Sub Process', 'branch_code']

        # Return the final merged dataframes
        return full_disberment_user, df_target, women_customer_listt




def upload_all_Data(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Michu-Kiyya/Inf']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Michu-Kiyya/F']['saving_account'].tolist()
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
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'customer_number', 'customer_name', 'gender', 'phone_number', 'saving_account', 'business_tin', 'application_status', 'michu_loan_product', 'approved_amount', 'approved_date', 'expiry_date', 'oustanding_total', 'arrears_start_date', 'loan_status']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO customer_list (branch_code, customer_number, customer_name, gender, phone_number, saving_account, business_tin, application_status, michu_loan_product, approved_amount, approved_date, expiry_date, oustanding_total, arrears_start_date, loan_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    




def random_upload_actual_data(date1, date2):
    # Fetch data from unique_intersection and conversiondata tables where disbursed_date is the latest
    # Check if data exists between the given dates
    try:
        check_dates_query = """
            SELECT COUNT(*) as count 
            FROM actual 
            WHERE actual_date BETWEEN %s AND %s
        """
        result = db_ops.fetch_one(check_dates_query, (date1, date2))
        # Add one day to date2 to include the end date in the range
        # date2 = date2 + pd.Timedelta(days=1)
        # st.write(result)
        
        if result and result['count'] > 0:
            st.warning(f"Data already exists between {date1} and {date2}. No new data will be inserted.")
            return
        unique_query = """
            SELECT branch_code, saving_account, disbursed_amount, disbursed_date, uni_id
            FROM unique_intersection
            WHERE disbursed_date between %s and %s
                AND product_type IN ('Wabbi', 'Guyya')
        """
        conversion_query = """
            SELECT branch_code, saving_account, disbursed_amount, disbursed_date, conv_id
            FROM conversiondata
            WHERE disbursed_date between %s and %s
                AND product_type IN ('Wabbi', 'Guyya')
        """
        
        unique_data = db_ops.fetch_data(unique_query, (date1, date2))
        conversion_data = db_ops.fetch_data(conversion_query, (date1, date2))
        # st.write(unique_data)
        # st.write(conversion_data)
        
        # Convert fetched data to DataFrames
        unique_df = pd.DataFrame(unique_data)
        unique_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'uni_id']
        conversion_df = pd.DataFrame(conversion_data)
        conversion_df.columns=['branch_code', 'saving_account', 'disbursed_amount', 'disbursed_date', 'conv_id']
        
        # Concatenate both DataFrames
        combined_df = pd.concat([unique_df, conversion_df])
        
        if combined_df.empty:
            st.warning("No data found in unique_intersection or conversiondata tables for the latest disbursed_date.")
            return

        # Group by branch_code and disbursed_date and aggregate the required columns
        aggregated_df = combined_df.groupby(['branch_code', 'disbursed_date']).agg(
            unique_actual=('uni_id', 'nunique'),
            account_actual=('saving_account', 'count'),
            disbursment_actual=('disbursed_amount', 'sum')
        ).reset_index()
        # st.write(aggregated_df)
        
        # Rename disbursed_date column to actual_date
        aggregated_df = aggregated_df.rename(columns={'disbursed_date': 'actual_date'})
        
        # Insert aggregated data into the actual table
        for index, row in aggregated_df.iterrows():
            # Check if this branch_code and actual_date combination already exists
            check_record_query = """
                SELECT COUNT(*) as count FROM actual 
                WHERE branch_code = %s AND actual_date = %s
            """
            record_exists = db_ops.fetch_one(check_record_query, (row['branch_code'], row['actual_date']))
            
            if not record_exists or record_exists['count'] == 0:
                # Insert the new record only if it doesn't already exist
                query = """
                    INSERT INTO actual (branch_code, unique_actual, account_actual, disbursment_actual, actual_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db_ops.insert_data(query, (
                    row['branch_code'], 
                    row['unique_actual'], 
                    row['account_actual'], 
                    row['disbursment_actual'], 
                    row['actual_date']
                ))
                # st.success(f"Data uploaded successfully for {row['branch_code']} on {row['actual_date']}")
            
    except Exception as e:
        st.error("Failed to upload data")
        # Print a full stack trace for debugging
        print("Database fetch error:", e)
        traceback.print_exc()  # This prints the full error trace to the terminal








def upload_arrears_Data(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'approved_amount', 'approved_date', 'maturity_date', 'michu_loan_product', 'loan_status']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO arrears_data (Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Approved_Amount, Approved_Date, Maturity_Date, Michu_Loan_Product, loan_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        # db_ops.rollback()  # Rollback in case of error
        return False

def get_natinal_id(id):
    # Retrieve account number from kiyya_customer table
    query4 = "SELECT nationalId FROM nationaldata WHERE nationalId = %s"
    result = db_ops.fetch_one(query4, (id,))  # Fetch only one result
    return result is not None


def aggregate_and_insert_actual_data_per_product():
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
        SELECT MAX(actual_date) as actual_date FROM actual_per_product WHERE actual_date = %s
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
        SELECT branch_code, product_type, saving_account, disbursed_amount, disbursed_date, uni_id
        FROM unique_intersection
        WHERE disbursed_date = %s
    """
    conversion_query = """
        SELECT branch_code, product_type, saving_account, disbursed_amount, disbursed_date, conv_id
        FROM conversiondata
        WHERE disbursed_date = %s
    """
    
    unique_data = db_ops.fetch_data(unique_query, (latest_disbursed_date,))
    conversion_data = db_ops.fetch_data(conversion_query, (latest_disbursed_date,))
    
    # Convert fetched data to DataFrames
    unique_df = pd.DataFrame(unique_data)
    unique_df.columns=['branch_code', 'product_type', 'saving_account', 'disbursed_amount', 'disbursed_date', 'uni_id']
    conversion_df = pd.DataFrame(conversion_data)
    conversion_df.columns=['branch_code', 'product_type', 'saving_account', 'disbursed_amount', 'disbursed_date', 'conv_id']
    
    # Concatenate both DataFrames
    combined_df = pd.concat([unique_df, conversion_df])
    # st.write(combined_df)
    
    if combined_df.empty:
        st.warning("No data found in unique_intersection or conversiondata tables for the latest disbursed_date.")
        return
    
    

    # Group by branch_code and aggregate the required columns
    aggregated_df = combined_df.groupby(['branch_code', 'product_type']).agg(
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
            SELECT 1 FROM actual_per_product 
            WHERE branch_code = %s AND product_type = %s AND actual_date = %s LIMIT 1
        """
        record_exists = db_ops.fetch_one(check_record_query, (row['branch_code'], row['product_type'], row['actual_date']))

        
        if not record_exists:
            # Insert the new record only if it doesn't already exist
            querry = """
                INSERT INTO actual_per_product (branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(querry, (row['branch_code'], row['product_type'], row['unique_actual'], row['account_actual'], row['disbursment_actual'], row['actual_date']))
    










@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_actual_vs_targetdata_per_product(role, username, fy_start, fy_end):
    # Access the username from session state
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")

    # st.write(role)
    # st.write(username)

    if role == "Admin" or role == 'under_admin':
        try:
            # Fetch districts from user_infos
            aggregate_and_insert_actual_data_per_product()
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
                SELECT actual_Id, branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_per_product 
                WHERE branch_code IN ({placeholders})
                AND (actual_date BETWEEN %s AND %s)
            """

            # Fetch actual data using a parameterized query
            quary_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end
            fetch_actual = db_ops.fetch_data(actual_query, quary_params)  # Ensure the tuple is passed correctly
            # Debugging: Print the raw data fetched
            # st.write("Actual Data Fetched:", fetch_actual)

            # Check if fetch_actual has data
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with the expected columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns = ['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # Apply data type conversions
            df_actual['Actual Unique Customer'] = df_actual['Actual Unique Customer'].apply(convert_decimal)
            df_actual['Actual Number Of Account'] = df_actual['Actual Number Of Account'].apply(convert_decimal)
            df_actual['Actual Disbursed Amount'] = df_actual['Actual Disbursed Amount'].apply(convert_decimal)
            df_actual['Actual Date'] = df_actual['Actual Date'].apply(convert_date)
            # df_actual['created_date'] = df_actual['created_date'].apply(convert_date)
            # st.write(df_actual)
            
            # Fetch target data
            target_query = F"""
                SELECT target_Id, branch_code, product_type, unique_target, account_target, disbursment_target, target_date
                FROM target_per_product WHERE (target_date BETWEEN %s AND %s)
            """
            tquary_params = (fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquary_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)  # Create an empty DataFrame with the expected columns
            else:
                df_target = pd.DataFrame(fetch_target)
                # Rename columns for 'target' data
                df_target.columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
            # Apply data type conversions
            df_target['Target Unique Customer'] = df_target['Target Unique Customer'].apply(convert_decimal)
            df_target['Target Number Of Account'] = df_target['Target Number Of Account'].apply(convert_decimal)
            df_target['Target Disbursed Amount'] = df_target['Target Disbursed Amount'].apply(convert_decimal)
            df_target['Target Date'] = df_target['Target Date'].apply(convert_date)
            # df_target['created_date'] = df_target['created_date'].apply(convert_date)

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
                SELECT actual_Id, branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_per_product WHERE branch_code IN ({branch_codes_str}) AND (actual_date BETWEEN %s AND %s)
            """
            quary_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end
            fetch_actual = db_ops.fetch_data(actual_query, quary_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
            # st.write(df_actual)

            # Fetch target data
            target_query = f"""
                SELECT target_Id, branch_code, product_type,  unique_target, account_target, disbursment_target, target_date
                FROM target_per_product WHERE branch_code IN ({branch_codes_str}) AND (target_date BETWEEN %s AND %s)
            """
            tquary_params = tuple(branch_codes) + (fy_start, fy_end) 
            fetch_target = db_ops.fetch_data(target_query, tquary_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
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
                SELECT actual_Id, branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date 
                FROM actual_per_product 
                WHERE branch_code = %s AND (actual_date BETWEEN %s AND %s)
            """
            quary_params = (branch_code, fy_start, fy_end)  # Combine branch code with fiscal year start and end
            fetch_actual = db_ops.fetch_data(actual_query, quary_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with the expected columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data
            target_query = """
                SELECT target_Id, branch_code, product_type, unique_target, account_target, disbursment_target, target_date 
                FROM target_per_product 
                WHERE branch_code = %s AND (target_date BETWEEN %s AND %s)
            """
            tquary_params = (branch_code, fy_start, fy_end)  # Fiscal year start and end dates
            fetch_target = db_ops.fetch_data(target_query, tquary_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)  # Create an empty DataFrame with the expected columns
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

            
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
                SELECT actual_Id, branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date
                FROM actual_per_product 
                WHERE branch_code IN ({branch_codes_str}) AND (actual_date BETWEEN %s AND %s)
            """
            quary_params = tuple(branch_codes) + (fy_start, fy_end)  # Combine branch codes with fiscal year start and end
            fetch_actual = db_ops.fetch_data(actual_query, quary_params)  # Ensure the tuple is passed correctly
            if not fetch_actual:
                columns = ['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']
                df_actual = pd.DataFrame(columns=columns)  # Create an empty DataFrame with the expected columns
            else:
                df_actual = pd.DataFrame(fetch_actual)
                df_actual.columns=['actual_Id', 'Branch Code', 'Product Type', 'Actual Unique Customer', 'Actual Number Of Account', 'Actual Disbursed Amount', 'Actual Date']

            # Fetch target data using parameterized query
            target_query = f"""
                SELECT target_Id, branch_code, product_type, unique_target, account_target, disbursment_target, target_date
                FROM target_per_product 
                WHERE branch_code IN ({branch_codes_str}) AND (target_date BETWEEN %s AND %s)
            """
            tquary_params = tuple(branch_codes) + (fy_start, fy_end) 
            fetch_target = db_ops.fetch_data(target_query, tquary_params)
            if not fetch_target:
                columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']
                df_target = pd.DataFrame(columns=columns)
            else:
                df_target = pd.DataFrame(fetch_target)
                df_target.columns = ['target_Id', 'Branch Code', 'Product Type', 'Target Unique Customer', 'Target Number Of Account', 'Target Disbursed Amount', 'Target Date']

            return act_dis_branch, df_actual, df_target
        except Exception as e:
            st.error("An error occurred while loading data.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()





def upload_collection(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'principal_collected', 'interest_collected', 'penality_collected', 'collected_date', 'michu_loan_product', 'paid_status']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO actual_collection (Loan_Id, Branch_Code, Customer_Name, Phone_Number, Saving_Account, Principal_Collected, Interest_Collected, Penality_Collected, Collected_Date, Michu_Loan_Product, Paid_Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False

def upload_sales(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'customer_name', 'saving_account', 'phone_number', 'business_tin_number', 'association_type', 'michu_loan_product', 'statuss', 'application_date_rejection_date', 'rejection_reason_remark', 'customer_feedback']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO sales_data (branch_code, Customer_Name, Saving_Account, Phone_Number, Business_Tin_Number, Association_Type, michu_loan_product, statuss, Application_Date_Rejection_Date, Rejection_Reason_Remark, Customer_Feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False




@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_sales_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    # st.write(role)
    
    if role == 'Admin' or role == 'under_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        prospect_query = """
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        """  
        Rejected_query = """
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        """
        closed_query = """
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        """
        emergance = """
        SELECT em_id, phone, full_name, statuss from emargance_data
        """
        marchent = """
        SELECT me_id, phone, full_name, statuss from Marchent_data
        """
        agents = """SELECT
        (SELECT count(agent_id) FROM agents WHERE status = 'active') AS active_sum,
        '/',
        (SELECT count(agent_id) FROM agents WHERE status != 'active') AS inactive_sum
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # st.write(df_branch)
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        rejected = db_ops.fetch_data(Rejected_query)
        if not rejected:
            df_rejected = pd.DataFrame(rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_rejected = pd.DataFrame(rejected)
            df_rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        emegancce = db_ops.fetch_data(emergance)
        if not emegancce:
            df_emegancce = pd.DataFrame(emegancce, columns=['em_id', 'phone', 'full_name', 'statuss'])
        else:
            df_emegancce = pd.DataFrame(emegancce)
            df_emegancce.columns=['em_id', 'phone', 'full_name', 'statuss']

        marecnt = db_ops.fetch_data(marchent)
        if not marecnt:
            df_marecnt = pd.DataFrame(marecnt, columns=['me_id', 'phone', 'full_name', 'statuss'])
        else:
            df_marecnt = pd.DataFrame(marecnt)
            df_marecnt.columns=['me_id', 'phone', 'full_name', 'statuss']
        
        agents = db_ops.fetch_data(agents)
        if not agents:
            df_agents = pd.DataFrame(agents, columns=['active_sum', '/', 'inactive_sum'])
        else:
            df_agents = pd.DataFrame(agents)
            df_agents.columns=['active_sum', '/', 'inactive_sum']
        # st.write(df_agents)


        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_rejected = pd.merge(df_branch, df_rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected= df_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_merged_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]
        df_merged_emegancce = df_emegancce[['em_id', 'phone', 'full_name', 'statuss']]
        df_merged_marchent = df_marecnt[['me_id', 'phone', 'full_name', 'statuss']]

        return df_combine_collection, df_combine_rejected, df_merged_closed, df_merged_emegancce, df_merged_marchent, df_agents
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed
    
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
        # st.write(df_branch)
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed
    
    elif role == 'Branch User':
        user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
        user_branch_code = db_ops.fetch_data(user_query)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE br.branch_code = '{user_branch_code[0]['branch']}'
        """
        branch_result = db_ops.fetch_data(code_query)
        df_branch = pd.DataFrame(branch_result)
        # st.write(df_branch)
        df_branch.columns=['District', 'branch_code', 'Branch']

        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed

    
    
    

def upload_rejected(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'michu_id', 'customer_name', 'phone_number', 'customer_number', 'saving_account', 'business_tin_number', 'gender', 'michu_loan_product', 'prefered_language', 'customeraddress__region', 'customeraddress__subcity_zone', 'customeraddress__woreda', 'statuss', 'rejection_reason_remark', 'customer_feedback']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO rejected_customer (
                                branch_code, michu_id, Customer_Name, Phone_Number, customer_number,
                                Saving_Account, Business_Tin_Number, gender, michu_loan_product, 
                                prefered_language, CustomerAddress__region, CustomerAddress__subcity_zone, 
                                CustomerAddress__woreda, statuss, Rejection_Reason_Remark, Customer_Feedback
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False
    



def upload_closed(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['branch_code', 'customer_number', 'loan_id', 'customer_name', 'age', 'gender', 'phone_number', 'bussiness_region', 'michu_loan_product', 'statuss', 'saving_account', 'business_tin_number', 'customer_feedback']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO closed (
                                branch_code, customer_number, loan_id, customer_name, age,
                                gender, phone_number, bussiness_region, michu_loan_product, 
                                statuss, Saving_Account, business_tin_number, Customer_Feedback
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False





def update_rejected_customers(edited_data):
    """Updates the 'rejected_customer' table based on edited data."""
    try:
        for row_index, edits in edited_data.items():
            michu_id = edits.get("michu_id")  
            if not michu_id:
                print(f"⚠️ Skipping row {row_index}: Missing michu_id")
                continue  # Skip update if michu_id is missing

            if not edits:
                print(f"⚠️ Skipping row {row_index}: No changes to update")
                continue  # Skip if there are no fields to update

            # Prepare the dynamic SET clause
            set_clause = ", ".join(f"{col} = %s" for col in edits.keys())
            values = list(edits.values()) + [michu_id]

            # Construct the SQL UPDATE query
            query = f"""
                UPDATE rejected_customer
                SET {set_clause}
                WHERE michu_id = %s
            """

            # Execute update query
            rows_updated = db_ops.update_data(query, values)

            if rows_updated > 0:
                print(f"✅ Successfully updated row {row_index}")
            else:
                print(f"⚠️ No changes made for row {row_index}")

    except Exception as e:
        print(f"❌ Error updating rejected customers: {e}")
        traceback.print_exc()
        st.error("⚠️ Error updating rejected customers")



def upload_prospect(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        final_merged_df['active_date'] =None
        data_to_insert = [tuple(x) for x in final_merged_df[['customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO prospect_data (customer_id_michu, age, branch_code, phone, full_name, gender, customer_account_current_stage, michu_loan_product, saving_account,
                                customer_number,
                                marital_status,
                                region,
                                statuss,
                                active_date 
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False



@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_sconversion_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    # st.write(role)
    
    if role == 'Admin' or role == 'under_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        prospect_query = """
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        """  
        Rejected_query = """
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        """
        closed_query = """
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # st.write(df_branch)
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        rejected = db_ops.fetch_data(Rejected_query)
        if not rejected:
            df_rejected = pd.DataFrame(rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_rejected = pd.DataFrame(rejected)
            df_rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_rejected = pd.merge(df_branch, df_rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected= df_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_merged_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_merged_closed
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed
    
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
        # st.write(df_branch)
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed
    
    elif role == 'Branch User':
        user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
        user_branch_code = db_ops.fetch_data(user_query)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE br.branch_code = '{user_branch_code[0]['branch']}'
        """
        branch_result = db_ops.fetch_data(code_query)
        df_branch = pd.DataFrame(branch_result)
        # st.write(df_branch)
        df_branch.columns=['District', 'branch_code', 'Branch']

        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        prospect_query = f"""
                            SELECT 
                            customer_id_michu, 
                            age, branch_code, 
                            phone, full_name, 
                            gender, 
                            customer_account_current_stage, 
                            michu_loan_product, saving_account,
                            customer_number,
                            marital_status,
                            region,
                            statuss,
                            active_date
                            
                        FROM prospect_data
                        WHERE branch_code IN ({branch_codes_str})
                        """  
        Rejected_query = f"""
        SELECT branch_code, michu_id, Customer_Name, Phone_Number,
        Saving_Account, gender, michu_loan_product, 
        statuss, Rejection_Reason_Remark, Customer_Feedback from rejected_customer
        WHERE branch_code IN ({branch_codes_str})
        """
        closed_query = f"""
        SELECT branch_code, customer_number, loan_id, customer_name,
        gender, phone_number, michu_loan_product, 
        statuss, Saving_Account, business_tin_number from closed
        WHERE branch_code IN ({branch_codes_str})
        """
        
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(prospect_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['customer_id_michu', 'age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']
        # st.write(df_collection)
        
        Rejected = db_ops.fetch_data(Rejected_query)
        if not Rejected:
            df_Rejected = pd.DataFrame(Rejected, columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback'])
        else:
            df_Rejected = pd.DataFrame(Rejected)
            df_Rejected.columns=['branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']
        
        closed = db_ops.fetch_data(closed_query)
        if not closed:
            df_closed = pd.DataFrame(closed, columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number'])
        else:
            df_closed = pd.DataFrame(closed)
            df_closed.columns=['branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='right')
        df_merged_rejected = pd.merge(df_branch, df_Rejected, on='branch_code', how='inner')
        df_merged_closed = pd.merge(df_branch, df_closed, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['District', 'Branch', 'customer_id_michu','age', 'branch_code', 'phone', 'full_name', 'gender', 'customer_account_current_stage', 'michu_loan_product', 'saving_account', 'customer_number', 'marital_status', 'region', 'statuss', 'active_date']]
        df_combine_rejected = df_merged_rejected[['District', 'Branch', 'branch_code', 'michu_id', 'Customer_Name', 'Phone_Number', 'Saving_Account', 'gender', 'michu_loan_product', 'statuss', 'Rejection_Reason_Remark', 'Customer_Feedback']]
        # st.write(df_combine_rejected)
        df_combine_closed = df_merged_closed[['District', 'Branch', 'branch_code', 'customer_number', 'loan_id', 'customer_name', 'gender', 'phone_number', 'michu_loan_product', 'statuss', 'Saving_Account', 'business_tin_number']]

        return df_combine_collection, df_combine_rejected, df_combine_closed



def upload_arrers_conver(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['loan_id', 'branch_code', 'customer_number', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO arrers_conversion (
                                loan_id, branch_code, customer_number, 
                                customer_name, phone_number, saving_account, 
                                michu_loan_product, approved_amount,  approved_date, 
                                maturity_date, outstanding_balance,	arrears_start_date, 
                                statuss
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_arrers_conver_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    
    if role == 'Admin' or role == 'under_admin' or role == 'collection_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        collection_query = """
                            SELECT 
                            loan_id,
                            MAX(branch_code) AS branch_code,
                            MAX(customer_name) AS customer_name,
                            MAX(phone_number) AS phone_number,
                            MAX(collected_from) AS collected_from,
                            SUM(principal_collected) AS Total_principal_collected,
                            SUM(interest_collected) AS Total_interest_collected,
                            SUM(penalty_collected) AS Total_penalty_collected,
                            MAX(collection_date) AS collection_date,  -- Latest collection date
                            MAX(michu_loan_product) AS michu_loan_product,
                            MAX(application_status) AS application_status
                            
                        FROM actual_coll
                        WHERE michu_loan_product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
                              AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
                        GROUP BY loan_id"""  
        conversion_query = """
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
        """
        arrears_query = """
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
        AND ac.michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )

        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']
        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')
        # st.write(df_merged_arrears)


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        collection_query = f"""
        SELECT 
            loan_id,
            MAX(branch_code) AS branch_code,
            MAX(customer_name) AS customer_name,
            MAX(phone_number) AS phone_number,
            MAX(collected_from) AS collected_from,
            SUM(principal_collected) AS Total_principal_collected,
            SUM(interest_collected) AS Total_interest_collected,
            SUM(penalty_collected) AS Total_penalty_collected,
            MAX(collection_date) AS collection_date,  -- Latest collection date
            MAX(michu_loan_product) AS michu_loan_product,
            MAX(application_status) AS application_status
            
        FROM actual_coll
        WHERE michu_loan_product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
        AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
        and branch_code IN ({branch_codes_str})
        GROUP BY loan_id               
        """
        conversion_query = f"""
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
        AND ac.michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
        AND Branch_Code IN ({branch_codes_str})
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )
        """
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        # branch_codes = [row['branch_code'] for row in branch_code_result]
        # branch_codes_str = ', '.join(['%s'] * len(branch_codes))


        # Queries for different loan statuses
        collection_query = f"""
        SELECT 
            loan_id,
            MAX(branch_code) AS branch_code,
            MAX(customer_name) AS customer_name,
            MAX(phone_number) AS phone_number,
            MAX(collected_from) AS collected_from,
            SUM(principal_collected) AS Total_principal_collected,
            SUM(interest_collected) AS Total_interest_collected,
            SUM(penalty_collected) AS Total_penalty_collected,
            MAX(collection_date) AS collection_date,  -- Latest collection date
            MAX(michu_loan_product) AS michu_loan_product,
            MAX(application_status) AS application_status
            
        FROM actual_coll
        WHERE michu_loan_product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
        AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
        and branch_code IN ({branch_codes_str})
        GROUP BY loan_id
        
        """
        conversion_query = f"""
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
        AND ac.michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
        AND Branch_Code IN ({branch_codes_str})
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )
        """

        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Branch User':
        try:
            user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
            user_branch_code = db_ops.fetch_data(user_query)
            code_query = f"""
            SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
            JOIN district_list dr ON br.dis_Id = dr.dis_Id
            WHERE br.branch_code = '{user_branch_code[0]['branch']}'
            """
            branch_result = db_ops.fetch_data(code_query)
            df_branch = pd.DataFrame(branch_result)
            df_branch.columns=['District', 'branch_code', 'Branch']

            branch_codes = [row['branch_code'] for row in branch_result]
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))
            # st.write(branch_codes_str)

            collection_query = f"""
            SELECT 
                loan_id,
                MAX(branch_code) AS branch_code,
                MAX(customer_name) AS customer_name,
                MAX(phone_number) AS phone_number,
                MAX(collected_from) AS collected_from,
                SUM(principal_collected) AS Total_principal_collected,
                SUM(interest_collected) AS Total_interest_collected,
                SUM(penalty_collected) AS Total_penalty_collected,
                MAX(collection_date) AS collection_date,  -- Latest collection date
                MAX(michu_loan_product) AS michu_loan_product,
                MAX(application_status) AS application_status
                
            FROM actual_coll
            WHERE michu_loan_product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
            AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
            and branch_code IN ({branch_codes_str})
            GROUP BY loan_id
            
            """
            conversion_query = f"""
            SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
            FROM arrers_conversion
            where statuss = 'active'
                and michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
                and branch_code IN ({branch_codes_str})
            """
            arrears_query = f"""
            SELECT 
                ac.loan_id, 
                ac.branch_code,
                ac.customer_name, 
                ac.phone_number, 
                ac.saving_account, 
                ac.michu_loan_product, 
                ac.approved_amount, 
                ac.approved_date, 
                ac.maturity_date, 
                ac.outstanding_balance, 
                ac.arrears_start_date, 
                ac.statuss
            FROM arrers_conversion ac
            WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
            AND ac.michu_loan_product IN ('Michu Wabii', 'Michu 1.0', 'Michu Kiyya Formal')
            AND Branch_Code IN ({branch_codes_str})
            AND NOT EXISTS (
                SELECT 1 
                FROM actual_collection col 
                WHERE col.Loan_Id = ac.loan_id
                AND col.Paid_Status = 'CLOSED'
            )
            """

            # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
            collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
            if not collectiond:
                df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
            else:
                df_collection = pd.DataFrame(collectiond)
                df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
                # st.write(df_collection)
            
            conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
            if not conversion:
                df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
            else:
                df_conversion = pd.DataFrame(conversion)
                df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
            arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
            if not arrears:
                df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
            else:
                df_arrears = pd.DataFrame(arrears)
                df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

            df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
            df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
            df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


            df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
            df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
            df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

            return df_combine_collection, df_combine_conversion, df_combine_arrears
        except Exception as e:
            st.error("Failed to fetch data")
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc()  # This prints the full error trace to the terminal
    
    # elif role == 'collection_admin':
    #     code_query = """
    #     SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
    #     JOIN district_list dr ON br.dis_Id = dr.dis_Id
    #     """
    #     collection_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'collection'
    #     """
    #     conversion_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'conversion'
    #     """
    #     arrears_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'In Arrears'
    #     """
    #     df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
    #     df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

    #     df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
    #     df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
    #     df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


    #     df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
    #     df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    #     df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

    #     return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        collection_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'collection'
        AND branch_code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'conversion'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
        df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    else:
        st.warning("No data for this user")
        quit()
        return None





@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_arrers_informal_detail(role, username):
    # username = st.session_state.get("username", "")
    # role = st.session_state.get("role", "")
    
    if role == 'Admin' or role == 'under_admin' or role == 'collection_admin':
        code_query = """
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        """
        collection_query = """
                            SELECT 
                                loan_id,
                                MAX(branch_code) AS branch_code,
                                MAX(customer_name) AS customer_name,
                                MAX(phone_number) AS phone_number,
                                MAX(collected_from) AS collected_from,
                                SUM(principal_collected) AS Total_principal_collected,
                                SUM(interest_collected) AS Total_interest_collected,
                                SUM(penalty_collected) AS Total_penalty_collected,
                                MAX(collection_date) AS collection_date,  -- Latest collection date
                                MAX(michu_loan_product) AS michu_loan_product,
                                MAX(application_status) AS application_status
                                
                            FROM actual_coll
                        WHERE michu_loan_product IN ('Guyya', 'Women InFormal')
                        AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
                        GROUP BY loan_id"""  
        conversion_query = """
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
        """
        arrears_query = """
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE TRIM(ac.statuss) = 'In Arrears'
        AND TRIM(ac.michu_loan_product) IN ('Michu Guyya', 'Michu Kiyya Informal')
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query))
        df_branch.columns=['District', 'branch_code', 'Branch']
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']
        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')
        # st.write(df_merged_conversion)


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Sales Admin':
        user_query = "SELECT district FROM user_infos WHERE userName = %s"
        user_district = db_ops.fetch_data(user_query, (username,))
        district = user_district[0]['district']
        # Handle the possibility of the district being a JSON-encoded string
        if isinstance(district, str):
            districts = json.loads(district)
        else:
            districts = [district]
        # st.write(districts)
        # Convert the list of districts to a string suitable for the SQL IN clause
        # districts_str = ', '.join(f"'{d}'" for d in districts)
        districts_str = ', '.join(['%s'] * len(districts))
        # st.write(districts_str)
        code_query = f"""
        SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
        JOIN district_list dr ON br.dis_Id = dr.dis_Id
        WHERE dr.district_name IN ({districts_str})
        """
        df_branch = pd.DataFrame(db_ops.fetch_data(code_query, tuple(districts)))
        df_branch.columns=['District', 'branch_code', 'Branch']
        branch_codes_str = ', '.join([f"'{code}'" for code in df_branch['branch_code']])
        # st.write(branch_codes_str)

        collection_query = f"""
        SELECT 
            loan_id,
            MAX(branch_code) AS branch_code,
            MAX(customer_name) AS customer_name,
            MAX(phone_number) AS phone_number,
            MAX(collected_from) AS collected_from,
            SUM(principal_collected) AS Total_principal_collected,
            SUM(interest_collected) AS Total_interest_collected,
            SUM(penalty_collected) AS Total_penalty_collected,
            MAX(collection_date) AS collection_date,  -- Latest collection date
            MAX(michu_loan_product) AS michu_loan_product,
            MAX(application_status) AS application_status
            
        FROM actual_coll
        WHERE michu_loan_product IN ('Guyya', 'Women InFormal')
        AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
        and branch_code IN ({branch_codes_str})
        GROUP BY loan_id               
        """
        conversion_query = f"""
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
        AND ac.michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
        AND Branch_Code IN ({branch_codes_str})
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )
        """
        
        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query)
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query)
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query)
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')



        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        # branch_codes = [row['branch_code'] for row in branch_code_result]
        # branch_codes_str = ', '.join(['%s'] * len(branch_codes))


        # Queries for different loan statuses
        collection_query = f"""
        SELECT 
            loan_id,
            MAX(branch_code) AS branch_code,
            MAX(customer_name) AS customer_name,
            MAX(phone_number) AS phone_number,
            MAX(collected_from) AS collected_from,
            SUM(principal_collected) AS Total_principal_collected,
            SUM(interest_collected) AS Total_interest_collected,
            SUM(penalty_collected) AS Total_penalty_collected,
            MAX(collection_date) AS collection_date,  -- Latest collection date
            MAX(michu_loan_product) AS michu_loan_product,
            MAX(application_status) AS application_status
            
        FROM actual_coll
        WHERE michu_loan_product IN ('Guyya', 'Women InFormal')
        AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
        and branch_code IN ({branch_codes_str})
        GROUP BY loan_id
        
        """
        conversion_query = f"""
        SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
        FROM arrers_conversion
        where statuss = 'active'
            and michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
            and branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT 
            ac.loan_id, 
            ac.branch_code,
            ac.customer_name, 
            ac.phone_number, 
            ac.saving_account, 
            ac.michu_loan_product, 
            ac.approved_amount, 
            ac.approved_date, 
            ac.maturity_date, 
            ac.outstanding_balance, 
            ac.arrears_start_date, 
            ac.statuss
        FROM arrers_conversion ac
        WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
        AND ac.michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
        AND Branch_Code IN ({branch_codes_str})
        AND NOT EXISTS (
            SELECT 1 
            FROM actual_coll col 
            WHERE col.loan_id = ac.loan_id
            AND col.application_status = 'CLOSED'
        )
        """

        # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
        collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
        if not collectiond:
            df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
        else:
            df_collection = pd.DataFrame(collectiond)
            df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
            # st.write(df_collection)
        
        conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
        if not conversion:
            df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
        else:
            df_conversion = pd.DataFrame(conversion)
            df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
        arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
        if not arrears:
            df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
        else:
            df_arrears = pd.DataFrame(arrears)
            df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
        df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
        df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    
    elif role == 'Branch User':
        try:
            user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
            user_branch_code = db_ops.fetch_data(user_query)
            code_query = f"""
            SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
            JOIN district_list dr ON br.dis_Id = dr.dis_Id
            WHERE br.branch_code = '{user_branch_code[0]['branch']}'
            """
            branch_result = db_ops.fetch_data(code_query)
            df_branch = pd.DataFrame(branch_result)
            df_branch.columns=['District', 'branch_code', 'Branch']

            branch_codes = [row['branch_code'] for row in branch_result]
            branch_codes_str = ', '.join(['%s'] * len(branch_codes))
            # st.write(branch_codes_str)

            collection_query = f"""
            SELECT 
                loan_id,
                MAX(branch_code) AS branch_code,
                MAX(customer_name) AS customer_name,
                MAX(phone_number) AS phone_number,
                MAX(collected_from) AS collected_from,
                SUM(principal_collected) AS Total_principal_collected,
                SUM(interest_collected) AS Total_interest_collected,
                SUM(penalty_collected) AS Total_penalty_collected,
                MAX(collection_date) AS collection_date,  -- Latest collection date
                MAX(michu_loan_product) AS michu_loan_product,
                MAX(application_status) AS application_status
                
            FROM actual_coll
            WHERE michu_loan_product IN ('Guyya', 'Women InFormal')
            AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
            and branch_code IN ({branch_codes_str})
            GROUP BY loan_id
            
            """
            conversion_query = f"""
            SELECT loan_id, branch_code, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, outstanding_balance, statuss
            FROM arrers_conversion
            where statuss = 'active'
                and michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
                and branch_code IN ({branch_codes_str})
            """
            arrears_query = f"""
            SELECT 
                ac.loan_id, 
                ac.branch_code,
                ac.customer_name, 
                ac.phone_number, 
                ac.saving_account, 
                ac.michu_loan_product, 
                ac.approved_amount, 
                ac.approved_date, 
                ac.maturity_date, 
                ac.outstanding_balance, 
                ac.arrears_start_date, 
                ac.statuss
            FROM arrers_conversion ac
            WHERE LOWER(TRIM(ac.statuss)) = 'In Arrears'
            AND ac.michu_loan_product IN ('Michu Guyya', 'Michu Kiyya Informal')
            AND Branch_Code IN ({branch_codes_str})
            AND NOT EXISTS (
                SELECT 1 
                FROM actual_collection col 
                WHERE col.Loan_Id = ac.loan_id
                AND col.Paid_Status = 'CLOSED'
            )
            """

            # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
            collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
            if not collectiond:
                df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
            else:
                df_collection = pd.DataFrame(collectiond)
                df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
                # st.write(df_collection)
            
            conversion = db_ops.fetch_data(conversion_query, tuple(branch_codes))
            if not conversion:
                df_conversion = pd.DataFrame(conversion, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss'])
            else:
                df_conversion = pd.DataFrame(conversion)
                df_conversion.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']
            arrears = db_ops.fetch_data(arrears_query, tuple(branch_codes))
            if not arrears:
                df_arrears = pd.DataFrame(arrears, columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss'])
            else:
                df_arrears = pd.DataFrame(arrears)
                df_arrears.columns=['loan_id', 'branch_code', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance',	'arrears_start_date', 'statuss']

            df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
            df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
            df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


            df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
            df_combine_conversion = df_merged_conversion[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'outstanding_balance', 'statuss']]
            df_combine_arrears = df_merged_arrears[['loan_id', 'District', 'Branch', 'customer_name', 'phone_number', 'saving_account', 'michu_loan_product', 'approved_amount',  'approved_date', 'maturity_date', 'outstanding_balance', 'arrears_start_date', 'statuss']]

            return df_combine_collection, df_combine_conversion, df_combine_arrears
        except Exception as e:
            st.error("Failed to fetch data")
            # Print a full stack trace for debugging
            print("Database fetch error:", e)
            traceback.print_exc() 
    
    # elif role == 'collection_admin':
    #     code_query = """
    #     SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
    #     JOIN district_list dr ON br.dis_Id = dr.dis_Id
    #     """
    #     collection_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'collection'
    #     """
    #     conversion_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'conversion'
    #     """
    #     arrears_query = """
    #     SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list WHERE loan_status = 'In Arrears'
    #     """
    #     df_branch = pd.DataFrame(db_ops.fetch_data(code_query), columns=['District', 'branch_code', 'Branch'])
    #     df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
    #     df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

    #     df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
    #     df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
    #     df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


    #     df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
    #     df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
    #     df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

    #     return df_combine_collection, df_combine_conversion, df_combine_arrears
    
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

        collection_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'collection'
        AND branch_code IN ({branch_codes_str})
        """
        conversion_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'conversion'
        AND branch_code IN ({branch_codes_str})
        """
        arrears_query = f"""
        SELECT cust_id, branch_code, customer_number, customer_name, phone_number, saving_account, michu_loan_product, approved_amount, approved_date, loan_status FROM customer_list 
        WHERE loan_status = 'In Arrears'
        AND branch_code IN ({branch_codes_str})
        """
        
        df_collection = pd.DataFrame(db_ops.fetch_data(collection_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_conversion = pd.DataFrame(db_ops.fetch_data(conversion_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])
        df_arrears = pd.DataFrame(db_ops.fetch_data(arrears_query), columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status'])

        df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
        df_merged_conversion = pd.merge(df_branch, df_conversion, on='branch_code', how='inner')
        df_merged_arrears = pd.merge(df_branch, df_arrears, on='branch_code', how='inner')


        df_combine_collection = df_merged_collection[['coll_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Collected Amount', 'Collection Status', 'Collected Date', 'Michu Loan Product', 'Loan Status']]
        df_combine_conversion = df_merged_conversion[['conv_id', 'District', 'Branch', 'Customer Number', 'Customer Name', 'Saving Account', 'Product Type', 'Disbursed Amount', 'Disbursed Date']]
        df_combine_arrears = df_merged_arrears[['arr_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Approved Amount', 'Approved Date', 'Maturity Date', 'Michu Loan Product', 'Loan Status']]

        return df_combine_collection, df_combine_conversion, df_combine_arrears
    else:
        st.warning("No data for this user")
        quit()
        return None




def upload_coll(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['michu_loan_product'] == 'Women Informal']['collected_from'].tolist()

        # Display the collected_from as list where product_type is 'Women Formal'
        formal_accounts = df[df['michu_loan_product'] == 'Women Formal']['collected_from'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['collected_from'] = df['collected_from'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='collected_from', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['loan_id', 'branch_code', 'customer_number', 'customer_name', 'phone_number', 'business_tin_number', 'michu_loan_product', 'product_group', 'application_status', 'approved_date', 'maturity_date', 'approved_amount', 'collection_date', 'principal_collected', 'interest_collected', 'penalty_collected', 'total_collected',  'collected_from', 'reason']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO actual_coll (loan_id, branch_code, customer_number, customer_name, phone_number, business_tin_number, michu_loan_product, product_group, application_status, approved_date, maturity_date, approved_amount, collection_date, principal_collected, interest_collected, penalty_collected, total_collected,  collected_from, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
             # Ensure data_to_insert is not empty
            if data_to_insert:
                # Make sure data_to_insert is a list of tuples
                if all(isinstance(item, tuple) for item in data_to_insert):
                    rows_inserted = db_ops.insert_many(insert_query, data_to_insert)
                    st.success(f"{rows_inserted} rows uploaded successfully.")

                    update_query = f"""
                    UPDATE arrers_conversion ac
                    JOIN (
                        SELECT Loan_Id, 
                            SUM(Principal_Collected) AS total_collected
                        FROM actual_collection
                        GROUP BY Loan_Id
                    ) col ON ac.loan_id = col.Loan_Id
                    SET ac.statuss = 'CLOSED'
                    WHERE col.total_collected >= ac.approved_amount
                        and ac.statuss != 'active';
                    """
                    rows_updated = db_ops.update_data(update_query)
                    st.success(f"{rows_updated} records in arrears_data updated to closed.")
                
                    return True
                else:
                    st.error("Data to insert should be a list of tuples.")
            else:
                st.warning("No data to insert into the unique_intersection table.")
        except Exception as e:
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False


def upload_dueloans(df):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['product_type'] == 'Michu-Kiyya Informal']['saving_account'].tolist()

        # Display the collected_from as list where product_type is 'Women Formal'
        formal_accounts = df[df['product_type'] == 'Michu Kiyya - Formal']['saving_account'].tolist()
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
                w_customer_df = db_ops.fetch_data(query)
                if not w_customer_df:
                    columns = ['Saving_Account', 'userId']
                    women_customer_df = pd.DataFrame(w_customer_df,columns=columns)
                else:
                    women_customer_df = pd.DataFrame(w_customer_df)
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
        df['saving_account'] = df['saving_account'].astype(str)
        merged_df['Saving_Account'] = merged_df['Saving_Account'].astype(str)

        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')
        # st.write(final_merged_df)
        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )
        # st.write(final_merged_df)

        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in final_merged_df[['loan_id', 'branch_code', 'customer_name', 'customer_number', 'phone_number', 'saving_account', 'approved_amount', 'product_type', 'approved_date', 'maturity_date', 'outstanding_balance', 'due_principal', 'due_interest', 'due_penalty', 'total_due_amount', 'arrears_start_date']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table Error: "['total_dueAmount'] not in index"
        try:
            insert_query = """
                INSERT INTO due_loan_datas (loan_id, branch_code, customer_name, customer_number, phone_number, saving_account, approved_amount, product_type, approved_date, maturity_date, outstanding_balance, due_principal, due_interest, due_penalty, total_dueAmount, arrears_start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False




# Check if any target_date from the uploaded file already exists in the target table
def any_actula_coll_exists(df):
    # Format the dates using the format_target_date function
    formatted_dates = tuple(df['collection_date'].tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT collection_date FROM actual_coll WHERE collection_date = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT collection_date FROM actual_coll WHERE collection_date IN ({placeholders})"
        result = db_ops.fetch_data(query, formatted_dates)

    return len(result) > 0

# Check if any target_date from the uploaded file already exists in the target table
def any_loan_id_exists(df):
    # Format the dates using the format_target_date function
    formatted_dates = tuple(df['loan_id'].tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT loan_id FROM due_loan_datas WHERE loan_id = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT loan_id FROM due_loan_datas WHERE loan_id IN ({placeholders})"
        result = db_ops.fetch_data(query, formatted_dates)

    return len(result) > 0

# Check if any target_date from the uploaded file already exists in the target table
def any_actula_disb_exists(df):
    # Format the dates using the format_target_date function
    formatted_dates = tuple(df['approved_date'].tolist())
    
    if len(formatted_dates) == 1:
        # Single date case
        query = "SELECT approved_date FROM disbursement WHERE approved_date = %s"
        result = db_ops.fetch_data(query, (formatted_dates[0],))  # Access the first date
        st.write(result)
    else:
        # Multiple dates case, dynamically generate placeholders
        placeholders = ', '.join(['%s'] * len(formatted_dates))
        query = f"SELECT approved_date FROM disbursement WHERE approved_date IN ({placeholders})"
        result = db_ops.fetch_data(query, formatted_dates)
        st.write(result)

    return len(result) > 0




def upload_emergance(df):
    try:
        data_to_insert = [tuple(x) for x in df[['phone', 'full_name', 'statuss']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO emargance_data (phone, full_name, statuss) 
                            VALUES (%s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False



def upload_disb(df):
    try:
        
        # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()
        # Prepare data for insertion
        data_to_insert = [tuple(x) for x in df[["branch_code", "customer_number", "loan_id", "application_status", "customer_name", "age", "sex", "phone_number", "business_tin_number", "michu_loan_product", "approved_date", "maturity_date", "approved_amount", "disbursed_amount", "disbursed_to"]].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                INSERT INTO disbursement (branch_code, customer_number, loan_id, application_status, customer_name, age, sex, phone_number, business_tin_number, michu_loan_product, approved_date, maturity_date, approved_amount, disbursed_amount, disbursed_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
             # Ensure data_to_insert is not empty
            if data_to_insert:
                # Make sure data_to_insert is a list of tuples
                if all(isinstance(item, tuple) for item in data_to_insert):
                    rows_inserted = db_ops.insert_many(insert_query, data_to_insert)
                    st.success(f"{rows_inserted} rows uploaded successfully.")

                    
                    # st.success(f"records in arrears_data updated to closed.")
                
                    return True
                else:
                    st.error("Data to insert should be a list of tuples.")
            else:
                st.warning("No data to insert into the unique_intersection table.")
        except Exception as e:
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False



def aggregate_and_insert_actual_data_per_product_anydate():
    try:
        date_query = """
            SELECT ui.disbursed_date
            FROM unique_intersection ui
            INNER JOIN conversiondata cd ON ui.disbursed_date = cd.disbursed_date
            WHERE ui.disbursed_date > %s
            AND ui.disbursed_date NOT IN (
                SELECT actual_date FROM actual_per_product
            )
            ORDER BY ui.disbursed_date
        """

        available_dates = db_ops.fetch_data(date_query, ('2025-01-01',))
        date_exists = [row['disbursed_date'] for row in available_dates]
        # print("Eligible Dates:", target_dates)


        # Now date_exists will be 1 if the date exists or 0 if it does not exist
        if not date_exists:
            st.warning("No new disbursed_date found in unique_intersection and conversiondata tables.")
            return
        
        # Build placeholders string
        placeholders = ', '.join(['%s'] * len(date_exists))
        # Fetch data from unique_intersection and conversiondata tables where disbursed_date is the latest
        unique_query = f"""
            SELECT branch_code, product_type, saving_account, disbursed_amount, disbursed_date, uni_id
            FROM unique_intersection
            WHERE disbursed_date IN ({placeholders})
        """
        conversion_query = f"""
            SELECT branch_code, product_type, saving_account, disbursed_amount, disbursed_date, conv_id
            FROM conversiondata
            WHERE disbursed_date IN ({placeholders})
        """
        
        unique_data = db_ops.fetch_data(unique_query, tuple(date_exists))
        conversion_data = db_ops.fetch_data(conversion_query, tuple(date_exists))
        
        # Convert fetched data to DataFrames
        unique_df = pd.DataFrame(unique_data)
        unique_df.columns=['branch_code', 'product_type', 'saving_account', 'disbursed_amount', 'disbursed_date', 'uni_id']
        conversion_df = pd.DataFrame(conversion_data)
        conversion_df.columns=['branch_code', 'product_type', 'saving_account', 'disbursed_amount', 'disbursed_date', 'conv_id']
        
        # Concatenate both DataFrames
        combined_df = pd.concat([unique_df, conversion_df])
        # st.write(combined_df)
        
        if combined_df.empty:
            st.warning("No data found in unique_intersection or conversiondata tables for the latest disbursed_date.")
            return
        
        

        # Group by branch_code and aggregate the required columns
        aggregated_df = combined_df.groupby(['branch_code', 'product_type', 'disbursed_date']).agg(
            unique_actual=('uni_id', 'nunique'),
            account_actual=('saving_account', 'count'),
            disbursment_actual=('disbursed_amount', 'sum')
        ).reset_index()
        # st.write(aggregated_df)
        # Insert aggregated data into the actual table
        for index, row in aggregated_df.iterrows():
            # Check if this branch_code and actual_date already exist in the actual table
            check_record_query = """
                SELECT 1 FROM actual_per_product 
                WHERE branch_code = %s AND product_type = %s AND actual_date = %s LIMIT 1
            """
            record_exists = db_ops.fetch_one(check_record_query, (row['branch_code'], row['product_type'], row['disbursed_date']))

            
            if not record_exists:
                # Insert the new record only if it doesn't already exist
                querry = """
                    INSERT INTO actual_per_product (branch_code, product_type, unique_actual, account_actual, disbursment_actual, actual_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                db_ops.insert_data(querry, (row['branch_code'], row['product_type'], row['unique_actual'], row['account_actual'], row['disbursment_actual'], row['disbursed_date']))
        st.success("data aggregated successfully.")
    except Exception as e:
        st.error(f"Error all: {e}")
        traceback.print_exc() 
        


def recommendation(username, full_name, customer_phone, customer_account, reason, file_path, filename, file_type):
    try:
        processed_phone_number = "+251" + customer_phone[1:]
        # phonenumber_processed = "+251" + phonenumber[1:]
        userId  = get_id(username)
        
        if userId:
            # Insert customer information into the customer table
            query = """
                INSERT INTO loan_recommendation(by_user_id, full_name, customer_phone, customer_account, reason, document_path, filename, file_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_ops.insert_data(query, (userId, full_name, processed_phone_number, customer_account, reason, file_path, filename, file_type))
            # db_ops.insert_data(query1, (userId, phonenumber_processed, account_number, eligible, total_score))
            return True
        else:
            st.error("User not found with the provided username.")
            return False
    except Exception as e:
        st.error("Failed to create customer due to an unexpected error.")
        st.exception(e)
        traceback.print_exc()
        return False


@handle_websocket_errors
@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def load_recomadation(role, username):
    if role == 'Branch User':
            try:
                user_query = f"SELECT branch FROM user_infos WHERE userName = '{username}'"
                user_branch_code = db_ops.fetch_data(user_query)
                code_query = f"""
                SELECT dr.district_name, br.branch_code, br.branch_name FROM branch_list br
                JOIN district_list dr ON br.dis_Id = dr.dis_Id
                WHERE br.branch_code = '{user_branch_code[0]['branch']}'
                """
                branch_result = db_ops.fetch_data(code_query)
                df_branch = pd.DataFrame(branch_result)
                df_branch.columns=['District', 'branch_code', 'Branch']

                branch_codes = [row['branch_code'] for row in branch_result]
                branch_codes_str = ', '.join(['%s'] * len(branch_codes))
                # st.write(branch_codes_str)
                query = """
                    SELECT 
                        lr.rec_id,
                        lr.by_user_id,
                        ui.full_name AS submitted_by,
                        lr.customer_phone,
                        lr.customer_account,
                        lr.reason,
                        lr.document_path,
                        lr.filename,
                        lr.file_type,
                        lr.status,
                        lr.register_date
                    FROM 
                        loan_recommendation lr
                    JOIN 
                        user_infos ui ON lr.by_user_id = ui.userId
                    ORDER BY 
                        lr.register_date DESC
                """


                collection_query = f"""
                SELECT 
                    loan_id,
                    MAX(branch_code) AS branch_code,
                    MAX(customer_name) AS customer_name,
                    MAX(phone_number) AS phone_number,
                    MAX(collected_from) AS collected_from,
                    SUM(principal_collected) AS Total_principal_collected,
                    SUM(interest_collected) AS Total_interest_collected,
                    SUM(penalty_collected) AS Total_penalty_collected,
                    MAX(collection_date) AS collection_date,  -- Latest collection date
                    MAX(michu_loan_product) AS michu_loan_product,
                    MAX(application_status) AS application_status
                    
                FROM actual_coll
                WHERE michu_loan_product IN ('Michu 1.0', 'Wabbi', 'Women Formal')
                AND loan_id IN (SELECT DISTINCT loan_id FROM arrers_conversion)
                and branch_code IN ({branch_codes_str})
                GROUP BY loan_id
                
                """
               

                # columns=['cust_id', 'branch_code', 'Customer Number', 'Customer Name', 'Phone Number', 'Saving Account', 'Michu Loan Product', 'Approved Amount','Approved Date', 'Loan Status']
                collectiond = db_ops.fetch_data(collection_query, tuple(branch_codes))
                if not collectiond:
                    df_collection = pd.DataFrame(collectiond, columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status'])
                else:
                    df_collection = pd.DataFrame(collectiond)
                    df_collection.columns=['Loan_Id', 'branch_code', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']
                    # st.write(df_collection)
                
                
                df_merged_collection = pd.merge(df_branch, df_collection, on='branch_code', how='inner')
                

                df_combine_collection = df_merged_collection[['Loan_Id', 'District', 'Branch', 'Customer Name', 'Phone Number', 'Saving Account', 'Principal Collected', 'Interest Collected', 'Penality Collected', 'Collected Date', 'Michu Loan Product', 'Paid Status']]
                
                return df_combine_collection
            except Exception as e:
                st.error("Failed to fetch data")
                # Print a full stack trace for debugging
                print("Database fetch error:", e)
                traceback.print_exc()  # This prints the full error trace to the terminal
    else:
        st.warning("No data for this user")
        quit()
        return None




def get_recommendations(username):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
    
    query = """
    SELECT ui.district, ui.full_Name, r.full_name, r.customer_phone, r.customer_account, r.reason, r.document_path, r.filename, r.file_type, r.status, r.register_date
    FROM loan_recommendation r 
    join user_infos ui on ui.userId = r.by_user_id
    WHERE by_user_id = %s
        AND r.status = 'Pending'
        AND DATE(r.register_date) = CURRENT_DATE
    ORDER BY register_date DESC
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (userId,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result

def apr_get_recommendations(username):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
    
    query = """
    SELECT ui.district, ui.full_Name, r.full_name, r.customer_phone, r.customer_account, r.reason, r.document_path, r.filename, r.file_type, r.status, r.register_date
    FROM loan_recommendation r 
    join user_infos ui on ui.userId = r.by_user_id
    WHERE by_user_id = %s
        AND r.status = 'Approved'
        AND DATE(r.register_date) = CURRENT_DATE
    ORDER BY register_date DESC
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (userId,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result

def rej_get_recommendations(username):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
    
    query = """
    SELECT 
        ui.district, 
        ui.full_Name,
        r.full_name, 
        r.customer_phone, 
        r.customer_account, 
        r.reason, 
        r.document_path, 
        r.filename, 
        r.file_type, 
        r.status, 
        r.register_date, 
        l.notes
    FROM 
        loan_recommendation r 
    JOIN 
        user_infos ui ON ui.userId = r.by_user_id
    JOIN 
        (
            SELECT 
                rec_id, 
                notes,
                ROW_NUMBER() OVER (PARTITION BY rec_id ORDER BY log_date DESC) as rn
            FROM 
                recommendation_audit_log
        ) l ON r.rec_id = l.rec_id AND l.rn = 1
    WHERE 
        r.rec_id IN (
            SELECT 
                MAX(rec_id)
            FROM 
                loan_recommendation
            WHERE 
                by_user_id = %s
                AND status = 'Rejected'
                AND DATE(register_date) = CURRENT_DATE
            GROUP BY 
                customer_phone
        )
    ORDER BY 
        r.register_date DESC
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (userId,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result

def block_get_recommendations(username):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
    
    query = """
        SELECT 
        ui.district, 
        ui.full_Name,
        r.full_name, 
        r.customer_phone, 
        r.customer_account, 
        r.reason, 
        r.document_path, 
        r.filename, 
        r.file_type, 
        r.status, 
        r.register_date, 
        l.notes
    FROM 
        loan_recommendation r 
    JOIN 
        user_infos ui ON ui.userId = r.by_user_id
    JOIN 
        (
            SELECT 
                rec_id, 
                notes,
                ROW_NUMBER() OVER (PARTITION BY rec_id ORDER BY log_date DESC) as rn
            FROM 
                recommendation_audit_log
        ) l ON r.rec_id = l.rec_id AND l.rn = 1
    WHERE 
        r.rec_id IN (
            SELECT 
                MAX(rec_id)
            FROM 
                loan_recommendation
            WHERE 
                by_user_id = %s
                AND status = 'Blocked'
                AND DATE(register_date) = CURRENT_DATE
            GROUP BY 
                customer_phone
        )
    ORDER BY 
        r.register_date DESC
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (userId,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result

def search_get_recommendations(username, phone):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
  
    # Normalize phone number to +251 format
    if phone.startswith('09') and len(phone) == 10:
        phone = '+251' + phone[1:]
    elif phone.startswith('+2519') and len(phone) == 13:
        pass  # Already in correct format
    else:
        return [], "Invalid phone format"  # Return empty list and status message
    
    query0 = """ SELECT status
    FROM loan_recommendation 
    WHERE customer_phone = %s
    """
    check = db_ops.fetch_data(query0, (phone,))
    # Handle cases where no record exists
    if not check or len(check) == 0:
        return [], "No record found"
        
    status = check[0]['status']
    if status == 'Rejected' or status == 'Blocked':
        query = """
        SELECT 
            ui.district, 
            ui.full_Name,
            r.full_name, 
            r.customer_phone, 
            r.customer_account, 
            r.reason, 
            r.document_path, 
            r.filename, 
            r.file_type, 
            r.status, 
            r.register_date, 
            l.notes
        FROM 
            loan_recommendation r 
        JOIN 
            user_infos ui ON ui.userId = r.by_user_id
        JOIN 
            (
                SELECT 
                    rec_id, 
                    notes,
                    ROW_NUMBER() OVER (PARTITION BY rec_id ORDER BY log_date DESC) AS rn
                FROM 
                    recommendation_audit_log
            ) l ON r.rec_id = l.rec_id AND l.rn = 1
        WHERE 
            r.by_user_id = %s
            AND r.customer_phone = %s
        ORDER BY 
            r.register_date DESC
        """
        
        # Fetch the data using your db_ops.fetch_data method
        result = db_ops.fetch_data(query, (userId, phone))

    else:
        query = """
        SELECT ui.district, ui.full_Name, r.full_name, r.customer_phone, r.customer_account, r.reason, r.document_path, r.filename, r.file_type, r.status, r.register_date
        FROM loan_recommendation r 
        join user_infos ui on ui.userId = r.by_user_id
        WHERE r.by_user_id = %s
            AND r.customer_phone = %s
        """
        
        # Fetch the data using your db_ops.fetch_data method
        result = db_ops.fetch_data(query, (userId, phone))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    # st.write(result)
    if result is None:
        return [], status  # Return empty list if there was an error
    
    return result, status

def allget_recommendations():
    """Fetch recommendations from database for the given user"""
    # userId  = get_id(username)
    query = """
    SELECT ui.district, ui.full_Name, r.full_name, r.customer_phone, r.customer_account, r.reason, r.document_path, r.filename, r.file_type, r.status, r.register_date
    FROM loan_recommendation r 
    join user_infos ui on ui.userId = r.by_user_id
    WHERE r.status = 'Pending'
        AND DATE(r.register_date) = CURRENT_DATE
    ORDER BY register_date DESC
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query)
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result


def total_recommendations():
    """Fetch recommendations from database for the given user"""
    # userId  = get_id(username)
    query = """
    SELECT
        COUNT(CASE WHEN status = 'Pending' THEN 1 END) AS pending_count,
        COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS approved_count,
        COUNT(CASE WHEN status = 'Rejected' THEN 1 END) AS rejected_count,
        COUNT(CASE WHEN status = 'Blocked' THEN 1 END) AS blocked_count
    FROM loan_recommendation;
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query)
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result


def total_recommendations_branch(username):
    """Fetch recommendations from database for the given user"""
    userId  = get_id(username)
    query = """
    SELECT
        COUNT(CASE WHEN status = 'Pending' THEN 1 END) AS pending_count,
        COUNT(CASE WHEN status = 'Approved' THEN 1 END) AS approved_count,
        COUNT(CASE WHEN status = 'Rejected' THEN 1 END) AS rejected_count,
        COUNT(CASE WHEN status = 'Blocked' THEN 1 END) AS blocked_count
    FROM loan_recommendation 
    WHERE by_user_id = %s;
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (userId,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result



def search_allget_recommendations(phone):
    """Fetch recommendations from database for the given user"""

    # Normalize phone number to +251 format
    if phone.startswith('09') and len(phone) == 10:
        phone = '+251' + phone[1:]
    elif phone.startswith('+2519') and len(phone) == 13:
        pass  # Already in correct format
    else:
        return []  # Invalid format, return empty list or handle with error
    
    # userId  = get_id(username)
    query = """
    SELECT ui.district, ui.full_Name, r.full_name, r.customer_phone, r.customer_account, r.reason, r.document_path, r.filename, r.file_type, r.status, r.register_date
    FROM loan_recommendation r 
    join user_infos ui on ui.userId = r.by_user_id
    WHERE r.customer_phone = %s
    """
    
    # Fetch the data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query, (phone,))
    
    # The fetch_data method already returns a list of dictionaries (due to dictionary=True cursor)
    # So we don't need to do the columns/row conversion
    if result is None:
        return []  # Return empty list if there was an error
    
    return result


# Function to fetch employee ID from the crm_user table
def get_rec_id(phone):
    """
    Fetches an employee ID from the crm_user table in the MySQL server database.

    Args:
        mydb: MySQL database connection object.
        employe_id: The employee ID to be fetched.

    Returns:
        The employee ID if found, None otherwise.
    """
    try:
        # Ensure phone is a clean string, no quotes or formatting issues
        phone = str(phone).strip()
        query1 = "SELECT rec_id FROM loan_recommendation WHERE customer_phone = %s"
        result = db_ops.fetch_one(query1, (phone,))
        # st.write(result)
        return result['rec_id']
        
    except Exception as e:
        st.error("Failed to fetch user id")
        st.exception(e)
        return None




def update_recommendation_status(phone, new_status, notes, username):
    """Update the status of a recommendation in the database"""

    
    try:
        rec_id  = get_rec_id(phone)
        # st.write(rec_id)

        if rec_id:
            update_query = """
            UPDATE loan_recommendation 
            SET status = %s
            WHERE customer_phone = %s
            """
            db_ops.update_data(update_query,(new_status, phone))
            
            # Add to audit log
            log_query = """
            INSERT INTO recommendation_audit_log 
            (rec_id, action, performed_by, notes)
            VALUES (%s, %s, %s, %s)
            """
            db_ops.insert_data(log_query, (rec_id, new_status, username, notes))

            return True
        else:
            st.error("Recommendation not found")
            return False
    except Exception as e:
        st.error("Failed to update recommendation status")
        traceback.print_exc()  # This prints the full error trace to the terminal
        return False


def check_rec_exist(phone_number,account_number):
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
        query1 = "SELECT customer_phone FROM loan_recommendation WHERE customer_phone = %s"
        result1 = db_ops.fetch_one(query1, (processed_phone_number,))
        query2 = "SELECT customer_account FROM loan_recommendation WHERE customer_account = %s"
        result2 = db_ops.fetch_one(query2, (account_number,))
        # # Retrieve phone number from customer_list table
        # query1 = "SELECT phone_number FROM customer_list WHERE phone_number = %s"
        # result1 = db_ops.fetch_one(query1, (processed_phone_number,))
        
        # # Retrieve phone number from customer_list_nonecode table
        # query2 = "SELECT phone_number FROM customer_list_nonecode WHERE phone_number = %s"
        # result2 = db_ops.fetch_one(query2, (processed_phone_number,))
        # # Retrieve phone number from branchcustomer table
        # query3 = "SELECT phoneNumber FROM branchcustomer WHERE phoneNumber = %s"
        # result3 = db_ops.fetch_one(query3, (processed_phone_number,))

        # # Retrieve phone number from kiyya_customer table
        # query4 = "SELECT phone_number FROM kiyya_customer WHERE phone_number = %s"
        # result4 = db_ops.fetch_one(query4, (processed_phone_number,))

        # # Retrieve phone number from women_product table
        # query5 = "SELECT phone_number FROM women_product_customer WHERE phone_number = %s"
        # result5 = db_ops.fetch_one(query5, (processed_phone_number,))
        
        # Check if phone number exists in any of the tables
        return result1 is not None or result2 is not None
    except Exception as e:
        st.error("Failed to search phone number")
        st.exception(e)
        return False
    

def check_rec_register(phone_number,account_number):
    """
    Fetches phone number from the MySQL server database to check if it exists.

    Args:
        cursor: MySQL cursor object
        phone_number: Phone number to check

    Returns:
        bool: True if the phone number exists, False otherwise
    """
    processed_phone_number = "+251" + phone_number[1:]

    queries = [
        ("SELECT phoneNumber FROM branchcustomer WHERE phoneNumber = %s LIMIT 1", (processed_phone_number,)),
        ("SELECT Saving_Account FROM branchcustomer WHERE Saving_Account = %s LIMIT 1", (account_number,)),
        ("SELECT phone_number FROM women_product_customer WHERE phone_number = %s LIMIT 1", (processed_phone_number,)),
        ("SELECT account_no FROM women_product_customer WHERE account_no = %s LIMIT 1", (account_number,)),
        ("SELECT phone_number FROM kiyya_customer WHERE phone_number = %s LIMIT 1", (processed_phone_number,)),
        ("SELECT phone_number FROM customer_list WHERE phone_number = %s LIMIT 1", (processed_phone_number,)),
        ("SELECT phone_number FROM customer_list_nonecode WHERE phone_number = %s LIMIT 1", (processed_phone_number,)),
        ("SELECT saving_account FROM customer_list WHERE saving_account = %s LIMIT 1", (account_number,)),
        ("SELECT saving_account FROM customer_list_nonecode WHERE saving_account = %s LIMIT 1", (account_number,)),
        ("SELECT saving_account FROM unique_intersection WHERE product_type NOT IN ('Wabbi', 'Women Formal') AND saving_account = %s LIMIT 1", (account_number,)),
        ("SELECT saving_account FROM conversiondata WHERE product_type NOT IN ('Wabbi', 'Women Formal') AND saving_account = %s LIMIT 1", (account_number,))
    ]

    try:
        for query, param in queries:
            result = db_ops.fetch_one(query, param)
            if result is not None:
                return True  # Stop checking once a match is found
        return False  # No match found in any table
    except Exception as e:
        st.error("Failed to search phone number or account number.")
        st.exception(e)
        return False

    



def check_rec_acc_exist(account_number):
    try:
        query1 = """
            SELECT saving_account 
            FROM unique_intersection 
            WHERE product_type IN ('Wabbi', 'Women Formal') 
              AND saving_account = %s
        """
        result1 = db_ops.fetch_one(query1, (account_number,))

        query2 = """
            SELECT saving_account 
            FROM conversiondata 
            WHERE product_type IN ('Wabbi', 'Women Formal') 
              AND saving_account = %s
        """
        result2 = db_ops.fetch_one(query2, (account_number,))

        # Return True if account number exists in either table
        return result1 is not None or result2 is not None

    except Exception as e:
        st.error("Failed to search account number.")
        st.exception(e)
        return False



def upload_marchent(df):
    try:
        data_to_insert = [tuple(x) for x in df[['phone', 'full_name', 'statuss']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO Marchent_data (phone, full_name, statuss) 
                            VALUES (%s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False



def upload_agents(df):
    try:
        data_to_insert = [tuple(x) for x in df[['customer_name', 'phone_number', 'bank']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO agents (customer_name, phone_number, bank) 
                            VALUES (%s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False

def upload_loanid(df):
    try:
        data_to_insert = [tuple(x) for x in df[['loan_id', 'phone', 'emergene_phone']].values.tolist()]
        # st.write(data_to_insert)
        # # Prepare data for insertion
        # data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'disbursed_date']].values.tolist()

        # Insert data into unique_intersection table
        try:
            insert_query = """
                            INSERT INTO due_loan_dataset (loan_id, phone_number, emergency_contact) 
                            VALUES (%s, %s, %s)
                        """


            # Replace NaN values with None in data_to_insert
            data_to_insert = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in data_to_insert
            ]
            
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
            st.error(f"Error can't upload data: ")
            print("Database fetch error:", e)
            traceback.print_exc()  
            

    except Exception as e:
        st.error(f"Error: {e}")
        traceback.print_exc()   # Rollback in case of error
        return False

def check_rejected(phone: str) -> tuple[str, str, str] | None:
    """
    Check if a rejected recommendation exists for the given phone number.
    
    Args:
        phone: Customer phone number (starting with '0')
    
    Returns:
        tuple: (rec_id, document_path) if recommendation found
        None: If no recommendation is found or error occurs
    """
    processed_phone_number = "+251" + phone[1:]
    try:
        query = """
            SELECT rec_id, document_path 
            FROM loan_recommendation 
            WHERE customer_phone = %s AND status = 'Rejected'
            LIMIT 1
        """
        
        result = db_ops.fetch_one(query, (processed_phone_number,))
        if result:
            return result['rec_id'], result['document_path']
        return None

    except Exception as e:
        st.error(f"Error checking recommendation: {str(e)}")
        return None


def get_overdue_pending() -> List[Tuple[str, str]]:
    """
    Fetches all pending recommendations older than 8 days.
    
    Returns:
        List of tuples: [(rec_id, document_path), ...]
        Empty list if none found or error occurs
    """
    try:
        query = """
            SELECT rec_id, document_path 
            FROM loan_recommendation 
            WHERE status = 'Pending'
            AND register_date < DATE_SUB(CURRENT_DATE(), INTERVAL 8 DAY)
        """
        result = db_ops.fetch_data(query)
        if not result:
            return []
        overdue_items = [(row['rec_id'], row['document_path']) for row in result] if isinstance(result[0], dict) else result
        # Store in total_removed table
        try:
            insert_query = """
                INSERT INTO total_removed (rec_id, document_path, removal_date, removal_reason)
                VALUES (%s, %s, CURRENT_DATE(), 'Overdue Pending Recommendation')
                ON DUPLICATE KEY UPDATE
                    removal_date = CURRENT_DATE(),
                    removal_reason = VALUES(removal_reason)
            """
            
            # Insert all records at once
            params = [(item[0], item[1]) for item in overdue_items]
            db_ops.insert_many(insert_query, params)
            
        except Exception as insert_error:
            st.error(f"Failed to log removed items: {str(insert_error)}")
            # Continue even if logging fails
        
        return overdue_items
    except Exception as e:
        st.error(f"Error fetching overdue recommendations: {str(e)}")
        return []



def delete_rejectedabove8(rec_id: str) -> bool:
    """
    Delete recommendation and its audit trail (keeps your original logic).
    Returns True if successful, False otherwise.
    """
    try:
        # Delete from audit log first
        audit_query = "DELETE FROM recommendation_audit_log WHERE rec_id = %s"
        audit_deleted = db_ops.delete_data(audit_query, (rec_id,))
        
        if audit_deleted is None:  # Error occurred
            st.error(f"Failed to delete audit log for {rec_id}")
            return False

        # Delete from main table
        main_query = "DELETE FROM loan_recommendation WHERE rec_id = %s"
        main_deleted = db_ops.delete_data(main_query, (rec_id,))
        
        if main_deleted is None:  # Error occurred
            st.error(f"Failed to delete recommendation {rec_id}")
            return False
            
        return True
        
    except Exception as e:
        st.error(f"Error deleting {rec_id}: {str(e)}")
        return False


def delete_rejected(rec_id: str, phone: str) -> bool:
    """
    Delete a rejected recommendation record and its associated audit log from the database.
    
    Args:
        rec_id: The recommendation record ID
        phone: The customer's phone number (starting with '0')

    Returns:
        bool: True if both deletions are successful, False otherwise
    """
    processed_phone_number = "+251" + phone[1:]
    
    try:
        # First, delete from the audit log (child table)
        delete_audit_query = "DELETE FROM recommendation_audit_log WHERE rec_id = %s"
        audit_deleted = db_ops.delete_data(delete_audit_query, (rec_id,))
        # st.write(audit_deleted)
        
        if audit_deleted is None:  # Error occurred during deletion
            return False
        
        # Then, delete from the main recommendation table (parent table)
        delete_recommendation_query = """
            DELETE FROM loan_recommendation 
            WHERE rec_id = %s AND customer_phone = %s AND status = 'Rejected'
        """
        recommendation_deleted = db_ops.delete_data(
            delete_recommendation_query, 
            (rec_id, processed_phone_number))
        
        if recommendation_deleted is None:  # Error occurred during deletion
            return False

        return True

    except Exception as e:
        st.error(f"Error during deletion process: {str(e)}")
        return False

@handle_websocket_errors
def get_by_user_id(phone):
    try:
         
        # Normalize phone number to +251 format
        processed_phone = (
            "+251" + phone[1:] if phone.startswith("0") 
            else phone if phone.startswith("+251") 
            else None
        )
        
        if not processed_phone:
            raise ValueError("Phone number must start with 0 or +251")
            
        # Execute query with parameterized input
        query = """
        SELECT r.performed_by 
        FROM recommendation_audit_log r
        JOIN loan_recommendation l ON l.rec_id = r.rec_id
        WHERE l.customer_phone = %s
        ORDER BY r.log_date DESC
        LIMIT 1
        """
        result = db_ops.fetch_one(query, (processed_phone,))
        
        # Return None if no result found
        if not result:
            return None
            
        # Handle both dictionary and tuple result formats
        return result.get('performed_by') if isinstance(result, dict) else result[0]
        
    except ValueError as ve:
        st.error(f"Validation error: {str(ve)}")
        return None
    except Exception as e:
        # logger.error(f"Database error fetching by_user_id: {str(e)}")
        raise RuntimeError(f"Error fetching recommendation data: {str(e)}")


@st.cache_data(show_spinner="Loading data, please wait...", persist="disk")
def get_customer_names():
    query = "SELECT fullName FROM kiyya_customer WHERE fullName IS NOT NULL LIMIT 1000"  # Filter at database level
    results = db_ops.fetch_data(query)
    return [row['fullName'] for row in results if row['fullName']] if results else []  # Additional Python-level filtering



def get_officerreject():
    """
    Fetches officer performance based on their assigned districts.
    Returns a list of dictionaries with 'Officer', 'Total Rejected', and 'Total Active' keys.
    """
    query = """
    WITH RECURSIVE seq AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM seq WHERE n < 10
    ),
    cleaned_user_infos AS (
        SELECT 
            userId,
            full_Name AS Officer,
            REPLACE(REPLACE(REPLACE(district, '[', ''), ']', ''), '"', '') AS clean_district
        FROM 
            user_infos
        WHERE 
            role = 3
    ),
    officer_districts AS (
        SELECT 
            u.userId,
            u.Officer,
            TRIM(
                SUBSTRING_INDEX(
                    SUBSTRING_INDEX(u.clean_district, ',', n),
                    ',', -1
                )
            ) AS District
        FROM 
            cleaned_user_infos u
        JOIN 
            seq ON n <= 1 + LENGTH(u.clean_district) - LENGTH(REPLACE(u.clean_district, ',', ''))
    )
    SELECT 
        o.Officer,
        COUNT(r.michu_id) AS `Total Rejected`,
        SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) AS `Total Active`,
        CONCAT(
            ROUND(
                IF(COUNT(r.michu_id) = 0, 0, 
                    (SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) / COUNT(r.michu_id)) * 100
                ),
                2
            ),
            '%'
        ) AS `Active %`
    FROM 
        rejected_customer r
    JOIN 
        branch_list b ON b.branch_code = r.branch_code
    JOIN 
        district_list d ON d.dis_Id = b.dis_Id
    JOIN 
        officer_districts o ON o.District = d.district_name
    GROUP BY 
        o.Officer;
    """
    
    # Fetch data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query)
    
    # Return empty list if result is None (in case of error), else return the fetched data
    return result if result is not None else []



def get_officerclosed():
    """
    Fetches officer performance based on their assigned districts.
    Returns a list of dictionaries with 'Officer', 'Total Rejected', and 'Total Active' keys.
    """
    query = """
    WITH RECURSIVE seq AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM seq WHERE n < 10
    ),
    cleaned_user_infos AS (
        SELECT 
            userId,
            full_Name AS Officer,
            REPLACE(REPLACE(REPLACE(district, '[', ''), ']', ''), '"', '') AS clean_district
        FROM 
            user_infos
        WHERE 
            role = 3
    ),
    officer_districts AS (
        SELECT 
            u.userId,
            u.Officer,
            TRIM(
                SUBSTRING_INDEX(
                    SUBSTRING_INDEX(u.clean_district, ',', n),
                    ',', -1
                )
            ) AS District
        FROM 
            cleaned_user_infos u
        JOIN 
            seq ON n <= 1 + LENGTH(u.clean_district) - LENGTH(REPLACE(u.clean_district, ',', ''))
    )
    SELECT 
        o.Officer,
        COUNT(r.loan_id) AS `Total Closed`,
        SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) AS `Total Active`,
        CONCAT(
            ROUND(
                IF(COUNT(r.loan_id) = 0, 0, 
                    (SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) / COUNT(r.loan_id)) * 100
                ),
                2
            ),
            '%'
        ) AS `Active %`
    FROM 
        closed r
    JOIN 
        branch_list b ON b.branch_code = r.branch_code
    JOIN 
        district_list d ON d.dis_Id = b.dis_Id
    JOIN 
        officer_districts o ON o.District = d.district_name
    GROUP BY 
        o.Officer;
    """
    
    # Fetch data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query)
    
    # Return empty list if result is None (in case of error), else return the fetched data
    return result if result is not None else []


def get_officerprospect():
    """
    Fetches officer performance based on their assigned districts.
    Returns a list of dictionaries with 'Officer', 'Total Rejected', and 'Total Active' keys.
    """
    query = """
    WITH RECURSIVE seq AS (
        SELECT 1 AS n
        UNION ALL
        SELECT n + 1 FROM seq WHERE n < 10
    ),
    cleaned_user_infos AS (
        SELECT 
            userId,
            full_Name AS Officer,
            REPLACE(REPLACE(REPLACE(district, '[', ''), ']', ''), '"', '') AS clean_district
        FROM 
            user_infos
        WHERE 
            role = 3
    ),
    officer_districts AS (
        SELECT 
            u.userId,
            u.Officer,
            TRIM(
                SUBSTRING_INDEX(
                    SUBSTRING_INDEX(u.clean_district, ',', n),
                    ',', -1
                )
            ) AS District
        FROM 
            cleaned_user_infos u
        JOIN 
            seq ON n <= 1 + LENGTH(u.clean_district) - LENGTH(REPLACE(u.clean_district, ',', ''))
    )
    SELECT 
        o.Officer,
        COUNT(r.customer_id_michu) AS `Total Prospect`,
        SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) AS `Total Active`,
        CONCAT(
            ROUND(
                IF(COUNT(r.customer_id_michu) = 0, 0, 
                    (SUM(CASE WHEN r.statuss = 'active' THEN 1 ELSE 0 END) / COUNT(r.customer_id_michu)) * 100
                ),
                2
            ),
            '%'
        ) AS `Active %`
    FROM 
        prospect_data r
    JOIN 
        branch_list b ON b.branch_code = r.branch_code
    JOIN 
        district_list d ON d.dis_Id = b.dis_Id
    JOIN 
        officer_districts o ON o.District = d.district_name
    GROUP BY 
        o.Officer;
    """
    
    # Fetch data using your db_ops.fetch_data method
    result = db_ops.fetch_data(query)
    
    # Return empty list if result is None (in case of error), else return the fetched data
    return result if result is not None else []







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
