import streamlit as st
import pandas as pd
from dependence import connect_to_database
from pathlib import Path
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

# Check if branch_code in the uploaded file is unique
def is_branch_code_unique(df):
    return df['branch_code'].is_unique

# Format target_date to yy/mm/dd
def format_target_date(date):
    return date.strftime('%y/%m/%d')

# Check if any target_date from the uploaded file already exists in the target table
def any_target_date_exists(df, mydb):
    cursor = mydb.cursor()
    formatted_dates = tuple(df['actual_date'].apply(format_target_date).tolist())
    
    if len(formatted_dates) == 1:
        query = "SELECT actual_date FROM actual WHERE actual_date = %s"
        cursor.execute(query, (formatted_dates[0],))
    else:
        query = "SELECT actual_date FROM actual WHERE actual_date IN %s"
        cursor.execute(query % str(formatted_dates))
    
    result = cursor.fetchall()
    cursor.close()

    return len(result) > 0

# Upload data to the target table
def upload_to_db(df, mydb):
    cursor = mydb.cursor()
    for index, row in df.iterrows():
        formatted_date = format_target_date(row['actual_date'])
        cursor.execute("""
            INSERT INTO actual (branch_code, unique_actual, account_actual, disbursment_actual, actual_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (row['branch_code'], 
             row['unique_actual'], 
             row['account_actual'], 
             row['disbursment_actual'], 
             formatted_date)
        )
    mydb.commit()
    cursor.close()
    return True

# Streamlit app
def main():
    st.set_page_config(page_title="Michu Portal", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
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

    uploaded_file = st.file_uploader(":orange[Upload Actual Excel file 👇🏻]", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False)
    make_sidebar1()

    mydb = connect_to_database()

    if mydb is not None:
        if uploaded_file is not None:
            filename = uploaded_file.name
            # Determine file extension
            file_extension = Path(filename).suffix.lower()
            try:
                if file_extension in [".csv", ".txt"]:
                    # Read CSV or text file
                    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
                elif file_extension in [".xlsx", ".xls"]:
                    # Read Excel file
                    df = pd.read_excel(uploaded_file, engine="openpyxl")
                
                # Convert column names to lowercase and take only the first word
                df.columns = [str(col).lower().split()[0] for col in df.columns]
                
                required_columns = {'branch_code', 'unique_actual', 'account_actual', 'disbursment_actual', 'actual_date'}
                missing_columns = required_columns - set(df.columns)
                if missing_columns:
                    st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
                else:
                    df['branch_code'] = df['branch_code'].str.strip()

                    # Check if branch_code is unique
                    if not is_branch_code_unique(df):
                        st.error("The branch_code column contains duplicate values.")
                        return

                    # Check for non-numeric strings in target columns
                    target_columns = ['unique_actual', 'account_actual', 'disbursment_actual']
                    
                    for col in target_columns:
                        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                    # Check for invalid dates in target_date column
                    try:
                        df['actual_date'] = pd.to_datetime(df['actual_date'], errors='coerce')
                        invalid_dates = df['actual_date'].isna()
                        if invalid_dates.any():
                            st.error("The actual_date column contains invalid dates.")
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
                            if upload_to_db(df, mydb):
                                st.success("Data uploaded successfully!")
                            else:
                                st.error("Data upload failed.")
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")
        mydb.close()
    else:
        st.error("Failed to connect to the database.")
    
    # Footer implementation
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #000;
        color: #00adef;
        text-align: center;
        padding: 0.5rem 0;
    }
    </style>
    <div class='footer'>
    <p>Copyright Â© 2025 Michu Platform</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
