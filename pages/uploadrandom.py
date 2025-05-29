import streamlit as st
import pandas as pd
from datetime import datetime
from navigation import make_sidebar
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()

def upload_random():
    # Custom CSS styling
    custom_css = """
    <style>
        div.block-container {
            padding-top: 2.5rem;
        }
        #MainMenu { visibility: hidden; }
        .stDeployButton { visibility: hidden; }
        .stButton button {
            background-color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 16px;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #00bfff;
            color: white;
        }
    </style>
    """
    st.set_page_config(page_title="Upload Random Data", page_icon=":bar_chart:", layout="wide")
    st.markdown(custom_css, unsafe_allow_html=True)
    update_activity()

    # Header section
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/coopbanck.gif')
    
    html_title = """
        <style>
        .title_dash{
            font-weight:bold;
            padding:1px;
            border-radius:6px
        }
        </style>
        <center><h2 class="title_dash">Upload Random Data</h2></center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    st.sidebar.markdown(f'<h4>Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    make_sidebar()

    # Main content
    with st.form(key='upload_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Select Start Date", 
                                    value=datetime(2024, 7, 1).date(),
                                    min_value=datetime(2024, 7, 1).date(),
                                    max_value=datetime.now().date())
        
        with col2:
            end_date = st.date_input("Select End Date",
                                    value=datetime.now().date(),
                                    min_value=start_date,
                                    max_value=datetime.now().date())

        if st.form_submit_button("Upload Data"):
            from dependence import random_upload_actual_data
            if start_date and end_date:
                if start_date <= end_date:
                    with st.spinner("Uploading data..."):
                        try:
                            random_upload_actual_data(start_date, end_date)
                            st.success("Data uploaded successfully!")
                        except Exception as e:
                            st.error(f"Error uploading data: {e}")
                else:
                    st.error("Start date must be before or equal to end date")
            else:
                st.error("Please select both start and end dates")

    # Footer
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
        <p>Copyright © 2025 Michu Platform</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__main__":
    upload_random()
