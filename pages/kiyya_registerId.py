import streamlit as st
# from dependence import validate_full_name
from navigation import login_bar
from navigation import make_sidebar1
import requests
from dependence import validate_phone, get_unquiedureatphone, get_unquiedkiyyaphone, get_natinal_id, validate_saving_account, check_durationunique_account


def set_session_state(transactionID, national_id, phone_nmuber):
    st.session_state.logged_in = True
    st.session_state['transactionID'] = transactionID
    st.session_state['national_id'] = national_id
    st.session_state['phone_nmuber'] = phone_nmuber


# Main function to handle user sign-up
def register():
    """
    Handles user sign-up process and form interactions.
    Switches page based on the API response.
    """
    st.set_page_config(page_title="Michu form", page_icon=":bar_chart:", layout="wide")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
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
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    login_bar()

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
        <center><h3 class="title_dash">Kiyya Informal Customer Registeration Form</h3></center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    make_sidebar1()

    # Main form for national ID input
    # Main container
    with st.container():
        

        # Form header
        st.markdown(
            """
            <div style="background-color:#f5f5f5; padding:10px; border-radius:10px; text-align:center; margin-bottom:20px;">
                <h2 style="color:#333;">National ID Verification</h2>
                <p style="color:#666;">Please provide your National ID and Phone Number to proceed.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:   
            # Create form
            with st.form(key="national_form", clear_on_submit=True):
                # Input fields
                national_key = "national_input"
                phone_key = "phone_input"
                account_key = "account"

                national_id = st.text_input(
                    "National ID*",
                    key=national_key,
                    placeholder="Enter national ID (FAN)",
                    help="Provide your 12-digit National ID number."
                )

                phone_number = st.text_input(
                    "Customer Phone* (09XXXXXXXX)", 
                    placeholder = "enter phone",
                    max_chars=10,
                    help="Must start with 09 and be 10 digits"
                ).strip()
                Saving_Account = st.text_input(
                            "Customer Account*",
                            placeholder= "Enter Account Number",
                            max_chars=13,
                            help="Must be 12 or 13 digits"
                        ).strip()

                # Submit button
                submit_button = st.form_submit_button("Proceed")

                # Handle form submission
                if submit_button:
                    try:
                        # Validate form input
                        if not national_id:
                            st.error("Please enter a valid National ID.")
                            st.stop()
                        elif not validate_phone(phone_number):
                            st.error('Please enter a valid phone number (use this format 09... or 07...)')
                            st.stop()
                        elif not validate_saving_account(Saving_Account):
                            st.error('The saving account is not correct please try again')
                        elif get_natinal_id(national_id):
                            st.error('The national id already exist, please enter correct national id (yours)')
                            st.stop()
                        elif phone_number in get_unquiedureatphone():
                            st.error('The phone number already exist, please enter correct phone number(new)')
                            st.stop()
                        elif phone_number in get_unquiedkiyyaphone():
                            st.error('The phone number already exist, please enter correct phone number(new)')
                            st.stop()
                        elif check_durationunique_account(Saving_Account):
                            st.error('The saving account is already exist, indicating that the customer has already used the product (it is not new or unique).')
                            st.stop()

                        else:
                            url = f"https://kid-api.dev.kifiya.et/api/v1/request/otp?FAN={national_id}"

                            payload = {}
                            files={}
                            headers = {
                            'Authenticate': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJDb3Bwb3JhdGl2ZSBiYWsiLCJpYXQiOjE3NTI0Nzk2MDEsImV4cCI6MTgxMjkzMTIwMH0.DK5Y2HdepGc8JyRPyOxhBLYEBCAY4jK8wdLc6LR1zYs8dr_OQDSBxmsPpWXqOA2BFG9rXh8No3hvGxFxKNEFyw',
                            'Content-Type': 'application/json'
                            }

                            response = requests.request("GET", url, headers=headers, data=payload, files=files)

                            # print(response.text)

                            # Handle API response
                            if response.status_code == 200:
                                data = response.json()
                                api_data = data.get("data")
                                errors=  api_data.get("errors")

                                if errors is None:
                                    # Extract nested fields safely
                                    transaction_id = api_data.get("transactionID")
                                    # response_info = api_data.get("response") or {}

                                    # Set session state
                                    st.session_state['transaction_id'] = transaction_id
                                    st.session_state['national_id'] = national_id
                                    st.session_state['phone_number'] = phone_number
                                    st.session_state['Saving_Account'] = Saving_Account

                                    # Switch to OTP page
                                    st.success("Redirecting to OTP page...")
                                    st.switch_page("pages/kiyya_otp.py")

                                else:
                                    # Fallback: Show any errors or a generic message
                                    if errors:
                                        st.error(f"API error: {errors}")
                                    else:
                                        st.error("Failed to verify the National ID.")
                            else:
                                st.error(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"An error occurred while fetching data: {str(e)}")

                # Display error message if available
                if 'error_message' in st.session_state:
                    st.error(st.session_state.error_message)
                    del st.session_state.error_message
if __name__ == "__main__":
    register()
