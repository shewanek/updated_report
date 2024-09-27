import streamlit as st
import pandas as pd
from dependence import connect_to_database
from pathlib import Path
import re
from navigation import make_sidebar1

# Check if all branches exist in the branch_list table
def all_branch_code_exist(branch_code, mydb):
    cursor = mydb.cursor()
    cursor.execute("SELECT branch_code FROM branch_list")
    br_existing_data = cursor.fetchall()
    cursor.close()
    
    existing_branches = [row[0] for row in br_existing_data]
    
    missing_branch_code = [branch for branch in branch_code if branch not in existing_branches]
    
    return missing_branch_code

# Format target_date to yy/mm/dd
def format_target_date(date):
    return date.strftime('%y/%m/%d')

# Check if any target_date from the uploaded file already exists in the target table
def any_target_date_exists(df, mydb):
    cursor = mydb.cursor()
    formatted_dates = tuple(df['convdisbursed_date'].apply(format_target_date).tolist())
    
    if len(formatted_dates) == 1:
        query = "SELECT disbursed_date FROM conversiondata WHERE disbursed_date = %s"
        cursor.execute(query, (formatted_dates[0],))
    else:
        query = "SELECT disbursed_date FROM conversiondata WHERE disbursed_date IN %s"
        cursor.execute(query % str(formatted_dates))
    
    result = cursor.fetchall()
    cursor.close()

    return len(result) > 0

def upload_to_unique(df, mydb):
    try:
        # Display the Saving_Account as list where product_type is 'Women Informal'
        informal_accounts = df[df['product_type'] == 'Women Informal']['saving_account'].tolist()

        # Display the Saving_Account as list where product_type is 'Women Formal'
        formal_accounts = df[df['product_type'] == 'Women Formal']['saving_account'].tolist()

        with mydb.cursor() as cursor:
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
                            AND userId IN (SELECT userId FROM user_info)
                    """
                    
                    cursor.execute(query)
                    kiyya_customer_data = cursor.fetchall()
                    kiyya_customer_df = pd.DataFrame(kiyya_customer_data, columns=['Saving_Account', 'userId'])
                    # st.write(kiyya_customer_df)

            # Fetch women_product_customer data for formal_accounts in a similar way
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
                            AND crm_id IN (SELECT userId FROM user_info)
                    """
                    
                    cursor.execute(query)
                    women_customer_data = cursor.fetchall()
                    women_customer_df = pd.DataFrame(women_customer_data, columns=['Saving_Account', 'userId'])
                    # st.write(women_customer_df)

            # Fetch branchcustomer data
            cursor.execute("SELECT Saving_Account, userId FROM branchcustomer")
            branchcustomer_data = cursor.fetchall()
            branchcustomer_df = pd.DataFrame(branchcustomer_data, columns=['Saving_Account', 'userId'])
            # st.write(branchcustomer_df)
            # Fetch all user_info data
            cursor.execute("SELECT userId, branch FROM user_info")
            user_info_data = cursor.fetchall()
            user_info_df = pd.DataFrame(user_info_data, columns=['userId', 'branch_code'])
            # st.write(user_info_df)

        # # Filter df rows by product type and corresponding customer lists
        # kiyya_customers = df[df['product_type'] == 'Women Informal']
        # formal_customers = df[df['product_type'] == 'Women Formal']

        # Concatenate customer data in reverse order to prioritize kiyya_customer and women_customer
        combined_customer_df = pd.concat([branchcustomer_df, women_customer_df, kiyya_customer_df], ignore_index=True)
        combined_customer_df = combined_customer_df.drop_duplicates(subset=['Saving_Account'], keep='last')
        # st.write(combined_customer_df)

        # # Close cursor after data fetching
        # cursor.close()

        # Merge combined customer data with user_info
        merged_df = combined_customer_df.merge(user_info_df, on='userId', how='left')

        # Merge the original df with merged_df on 'Saving_Account'
        final_merged_df = df.merge(merged_df, left_on='saving_account', right_on='Saving_Account', how='left')

        # Replace the branch_code in df with the correct merged branch_code if saving_account matches
        final_merged_df['branch_code'] = final_merged_df.apply(
            lambda row: row['branch_code_y'] if pd.notna(row['branch_code_y']) else row['branch_code_x'], axis=1
        )

        # Prepare data for insertion
        data_to_insert = final_merged_df[['branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'convdisbursed_date']].values.tolist()

        # Insert data into the 'conversiondata' table
        with mydb.cursor() as cursor:
            insert_query = """
                INSERT INTO conversiondata (branch_code, customer_number, customer_name, saving_account, product_type, disbursed_amount, disbursed_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(insert_query, data_to_insert)

        # Commit the transaction
        mydb.commit()

        return True

    except Exception as e:
        # Log the error for debugging
        print(f"Error: {e}")

        # Rollback in case of error
        mydb.rollback()
        
        return False






# Streamlit app
def main():
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
        #MainMenu { visibility: hidden; }
        .stDeployButton { visibility: hidden; }
        .stButton button {
            background-color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 16px;
            cursor: pointer.
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash {
            font-weight: bold;
            padding: 1px;
            border-radius: 6px;
        }
        </style>
        <center> <h3 class="title_dash"> Michu Actual Data Upload Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    st.sidebar.image("pages/michu.png")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(":orange[Upload Actual Conversion Excel file 👇🏻]", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False)
    make_sidebar1()

    mydb = connect_to_database()

    if mydb is not None:
        if uploaded_file is not None:
            filename = uploaded_file.name
            # Determine file extension
            file_extension = Path(filename).suffix.lower()
            try:
                column_types = {
                    'branch_code': str,
                    'customer_number': str, 
                    'customer_name': str, 
                    'saving_account': str,
                    'product_type': str 
                }
                if file_extension in [".csv", ".txt"]:
                    # Read CSV or text file
                    df = pd.read_csv(uploaded_file, dtype=column_types, encoding="ISO-8859-1")
                elif file_extension in [".xlsx", ".xls"]:
                    # Read Excel file
                    df = pd.read_excel(uploaded_file, dtype=column_types, engine="openpyxl")
                
                # Convert column names to lowercase and take only the first word
                df.columns = [str(col).lower().split()[0] for col in df.columns]
                
                required_columns = {'branch_code', 'customer_number', 'customer_name', 'saving_account', 'product_type', 'disbursed_amount', 'convdisbursed_date'}
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
                else:
                    # Check for null or empty values in required columns only
                    required_df = df[list(required_columns)]
                    if required_df.isnull().any().any():
                        null_columns = required_df.columns[required_df.isnull().any()].tolist()
                        st.error(f"The following columns contain null or empty values: {', '.join(null_columns)}")
                    else:
                        df['branch_code'] = df['branch_code'].str.strip()

                        # Check for invalid dates in target_date column
                        try:
                            df['convdisbursed_date'] = pd.to_datetime(df['convdisbursed_date'], errors='coerce')
                            invalid_dates = df['convdisbursed_date'].isna()
                            if invalid_dates.any():
                                st.error("The convdisbursed_date column contains invalid dates.")
                                return
                        except Exception as e:
                            st.error(f"An error occurred while parsing dates: {e}")
                            return
                        
                        branches = df['branch_code']
                        missing_branch_code = all_branch_code_exist(branches, mydb)
                        
                        if missing_branch_code:
                            # Convert all elements to strings to avoid type errors
                            missing_branch_code = [str(branch) for branch in missing_branch_code]
                            st.error(f"The following branches are not found in the database: {', '.join(missing_branch_code)}")
                        else:
                            # Check if any target_date exists
                            if any_target_date_exists(df, mydb):
                                st.error("One or more Actual dates in the uploaded file already exist in the database. this means You are trying to upload same data twice. Upload aborted.")
                            else:
                                if upload_to_unique(df, mydb):
                                    st.success("Data uploaded successfully!")

                                else:
                                    st.error("Data upload failed.")
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")
        mydb.close()
    else:
        st.error("Failed to connect to the database.")

if __name__ == "__main__":
    main()
