import streamlit as st
import pandas as pd
from pathlib import Path
# from navigation import make_sidebar1
from dependence import initialize_session, update_activity, check_session_timeout




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
            # padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
        #MainMenu { visibility: hidden; }
        .stDeployButton { visibility: hidden; }
        .stAppHeader { visibility: hidden; }
        /* Hide the entire header bar */
        header.stAppHeader {
            display: none;
        }
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
        <center> <h3 class="title_dash"> Michu Actual Data Upload Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    st.sidebar.image("pages/michu.png")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(":orange[Upload Actual Unique Excel file 👇🏻]", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False)
    # make_sidebar1()

    try:
        if uploaded_file is not None:
            from dependence import all_branch_code_exist, upload_all_Data
            filename = uploaded_file.name
            # Determine file extension
            file_extension = Path(filename).suffix.lower()
            try:
                column_types = {
                    'branch_code': str,
                    'customer_number': str,
                    'customer_name': str, 
                    'gender': str, 
                    'phone_number': str, 
                    'saving_account': str, 
                    'business_tin': str,
                    'application_status': str,
                    'michu_loan_product': str, 
                    'approved_amount': float,
                    'oustanding_total': float,
                    'loan_status': str
                }
                if file_extension in [".csv", ".txt"]:
                    # Read CSV or text file
                    df = pd.read_csv(uploaded_file, dtype=column_types, encoding="ISO-8859-1")
                elif file_extension in [".xlsx", ".xls"]:
                    # Read Excel file
                    df = pd.read_excel(uploaded_file, dtype=column_types, engine="openpyxl")
                
                # Convert column names to lowercase and take only the first word
                df.columns = [str(col).lower().split()[0] for col in df.columns]
                
                required_columns = {'branch_code', 'customer_number', 'customer_name', 'gender', 'phone_number', 'saving_account', 'business_tin', 'application_status', 'michu_loan_product', 'approved_amount', 'approved_date', 'expiry_date', 'oustanding_total', 'arrears_start_date', 'loan_status'}
                missing_columns = required_columns - set(df.columns)
                req_col = {'branch_code', 'approved_date', 'loan_status'}
                if missing_columns:
                    st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
                else:
                    # Check for null or empty values in required columns only
                    required_df = df[list(req_col)]
                    if required_df.isnull().any().any():
                        null_columns = required_df.columns[required_df.isnull().any()].tolist()
                        st.error(f"The following columns contain null or empty values: {', '.join(null_columns)}")
                    
                    else:
                        df = df.where(pd.notnull(df), None)
                        df['branch_code'] = df['branch_code'].str.strip()

                        # Check for invalid dates in target_date column
                        try:
                            df['approved_date'] = pd.to_datetime(df['approved_date'], errors='coerce')
                            invalid_dates = df['approved_date'].isna()
                            if invalid_dates.any():
                                st.error("The approved_date column contains invalid dates.")
                                return
                        except Exception as e:
                            st.error(f"An error occurred while parsing dates: {e}")
                            return
                        
                        branches = df['branch_code']
                        missing_branch_code = all_branch_code_exist(branches)
                        
                        if missing_branch_code:
                            # Convert all elements to strings to avoid type errors
                            missing_branch_code = [str(branch) for branch in missing_branch_code]
                            st.error(f"The following branches are not found in the database: {', '.join(missing_branch_code)}")
                        else:
                            try:
                                if upload_all_Data(df):
                                    st.success("Data uploaded successfully!")

                                else:
                                    st.error("Data upload failed.")
                            except Exception as e:
                                st.error(f"Fail to  uload data: {e}")
                        
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
