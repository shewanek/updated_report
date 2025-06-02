import streamlit as st
import pandas as pd
from pathlib import Path
import traceback
import numpy as np
# from navigation import make_sidebar1
from dependence import update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()



# Streamlit app
def main():
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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
    update_activity()
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
        <center> <h3 class="title_dash"> Michu Arrears Data Upload Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    st.sidebar.image("pages/michu.png")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(":orange[Upload Arrears Excel file 👇🏻]", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False)
    # make_sidebar1()

    try:
        if uploaded_file is not None:
            from dependence import all_branch_code_exist, upload_dueloans, any_loan_id_exists
            filename = uploaded_file.name
            # Determine file extension
            file_extension = Path(filename).suffix.lower()
            try:
															

                expected_columns = [
                    "branch", "customer number", "loan id", "customer name", "phone number", 'saving account',
                    "michu loan product", "approved date", "maturity date", "approved amount",'outstanding balance', 
                    'due principal', 'due interest', "due penalty", 'total due amount', "arrears start date"
                ]

                column_mapping = {
                    "loan id": "loan_id",
                    "branch": "branch_code",
                    "customer number": "customer_number",
                    "customer name": "customer_name",
                    "phone number": "phone_number",
                    "saving account" : "saving_account",
                    "michu loan product": "product_type",
                    "approved date": "approved_date",
                    "maturity date": "maturity_date",
                    "approved amount": "approved_amount",
                    "outstanding balance" : "outstanding_balance",
                    'due principal' : "due_principal",
                    'due interest' : "due_interest",
                    "due penalty" : "due_penalty",
                    'total due amount' : "total_due_amount",
                    "arrears start date" : "arrears_start_date"
                }

                # Detect file type and read
                if file_extension in [".csv", ".txt"]:
                    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
                elif file_extension in [".xlsx", ".xls"]:
                    df = pd.read_excel(uploaded_file, engine="openpyxl")

                # Standardize column names
                df.columns = df.columns.str.strip().str.lower()

                # Check if all expected columns exist
                if not all(col in df.columns for col in expected_columns):
                    missing = [col for col in expected_columns if col not in df.columns]
                    st.error(f"Missing required columns: {missing}")
                else:
                    # Rename columns
                    df = df.rename(columns=column_mapping)

                    date_cols = ['approved_date', 'maturity_date', 'arrears_start_date']

                    for col in date_cols:
                        df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors='coerce')  # Parse
                        df[col] = df[col].dt.strftime('%Y-%m-%d')  # Format to YYYY-MM-DD


                    for col in ['approved_amount', 'due_principal', 'due_interest', 'due_penalty', 'total_due_amount']:
                        df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

                    # Convert all other columns to string (if not already)
                    for col in df.columns:
                        if col not in ['approved_date', 'maturity_date', 'arrears_start_date',
                                    'due_principal', 'due_interest', 'due_penalty', 'total_due_amount']:
                            df[col] = df[col].astype(str)

                    # st.write(df.head())
                    df = df.drop_duplicates(subset=['loan_id'], keep='first')
                    branches = df['branch_code']
                    missing_branch_code = all_branch_code_exist(branches)
                    df = df.replace(["", " ", "  "], None)  # Replace empty strings with None
                    df = df.where(pd.notnull(df), None)  # Convert NaN to None
                    df['approved_amount'] = pd.to_numeric(df['approved_amount'], errors='coerce')


                    conditions = [
                        (df['product_type'] == 'Michu Kiyya Formal'),
                        (df['product_type'] == 'Michu Kiyya Informal')
                    ]

                    choices = ['Michu Kiyya - Formal', 'Michu-Kiyya Informal']

                    df['product_type'] = np.select(conditions, choices, default=df['product_type'])

                    # st.write(df)
                    # st.write(df.columns)
                    if missing_branch_code:
                        # Convert all elements to strings to avoid type errors
                        missing_branch_code = [str(branch) for branch in missing_branch_code]
                        st.error(f"The following branches are not found in the database: {', '.join(missing_branch_code)}")
                    
                    else:
                        try:
                            # Check if any target_date exists
                            if any_loan_id_exists(df):
                                st.error("One or more loan Id in the uploaded file already exist in the database. this means You are trying to upload same data twice. Upload aborted.")
                            else:
                                if upload_dueloans(df):
                                    st.success("Data uploaded successfully!")

                                else:
                                    st.error("Data upload failed.")
                        except Exception as e:
                            st.error(f"Fail to  uload data: {e}")
                            print("Database fetch error:", e)
                            traceback.print_exc() 
                        
            except Exception as e:
                st.error(f"An error occurred while uloading: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
if __name__ == "__main__":
    main()

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
