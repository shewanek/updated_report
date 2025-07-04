import streamlit as st
# from dependence import  validate_full_name
from navigation import login_bar
from navigation import make_sidebar1
from pages.kiyya_register_withid import kiyya_register_withid
import requests
from datetime import datetime, timedelta
import time

def set_session_state(transactionID):
    st.session_state.logged_in = True
    st.session_state['transactionID'] = transactionID

# Main function to handle user sign-up
def register():
    """
    Handles user sign-up process and form interactions.
    Resets input fields upon successful registration.
    """
    st.set_page_config(page_title="Michu form", page_icon=":bar_chart:", layout="wide")
    custom_cs = """
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
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_cs, unsafe_allow_html=True)
    login_bar()
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
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
        <center> <h3 class = "title_dash">Kiyya Informal Customer Registeration Form</h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar1()
    username = st.session_state.get('username', 'username')

    with st.form(key="otp_form"):
        otp_key = 'otp_input'
        otp_id = st.text_input('OTP', key=otp_key, placeholder='Enter  OTP that sent to your phone number').strip()
        transactionID = st.session_state.get("transaction_id")
        national_id = st.session_state.get("national_id")
        phone_number = st.session_state.get("phone_number")
        Saving_Account = st.session_state.get("Saving_Account")
        col21, col22 = st.columns([0.7, 0.3])
        with col21:
            if st.form_submit_button("Proceed"):
                try:
                    # validate form not empty
                    if not otp_id:
                        st.error("Please enter a valid OTP.")
                        if st.form_submit_button("Back to Form"):
                            st.switch_page("pages/kiyya_registerId.py")
                        return
                    
                    # Validate session state dependencies
                    required_fields = ["transaction_id", "national_id", "phone_number", "Saving_Account"]
                    missing = [f for f in required_fields if not st.session_state.get(f)]
                    if missing:
                        st.error(f"Missing required data: {', '.join(missing)}")
                        st.stop()
                    
                    # Build the URL with query parameters
                    url = f"https://kid-api.dev.kifiya.et/api/v1/request/kyc?FAN={national_id}&OTP={otp_id}&TRANSACTIONID={transactionID}"

                    # Headers
                    payload = {}
                    files={}
                    headers = {
                        'Authenticate': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJNaWNodSBDb29wIiwiaWF0IjoxNzUxMzc0Mzc1LCJleHAiOjE3NjcxMzkyMDB9.KtIT28uzZMlsmW1HbWp4pC8ngl1EkaZEAxw9VQOSqreF2MTqJ7qv_uDtjl5bGh3XehZ_l6C2hBGY_77dF4OPHA',
                        'Content-Type': 'application/json'
                    }

                    with st.spinner("Verifying OTP and retrieving KYC data..."):
                        try:
                            response = requests.get(url, headers=headers, timeout=10)

                            if response.status_code == 200:
                                data = response.json()
                                resp = data.get("data", {})
                                kyc_status = resp.get("response", {}).get("kycStatus")
                                errors = resp.get("errors")

                                if not errors and kyc_status == "true":
                                    identity = resp["response"]["identity"]
                                    responseTime = resp.get("responseTime")
                                    name = next(i["value"] for i in identity["name"] if i["language"] == "eng")
                                    dob = identity["dob"]
                                    gender = next(i["value"] for i in identity["gender"] if i["language"] == "eng")
                                    national_phone = identity["phoneNumber"]
                                    email = identity["emailId"]
                                    address = next(item["value"] for item in identity["fullAddress"] if item["language"] == "eng")

                                    if gender.strip().lower() != "female":
                                        st.error("Only females are allowed for this product.")
                                        if st.form_submit_button("Back to Form"):
                                            st.switch_page("pages/kiyya_registerId.py")
                                        st.stop()

                                    st.success("Redirecting to form...")
                                    kiyya_register_withid(name, phone_number, Saving_Account, national_id,  gender, dob, transactionID, national_phone, email, address, responseTime)
                                else:
                                    st.session_state["error_datamessage"] = data.get("message")
                                    st.switch_page("pages/kiyya_registerId.py")
                            else:
                                st.error(f"Failed to fetch KYC data: {response.status_code}, pls enter correct OTP")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Request failed: {e}")
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred while fetching data: {str(e)}")
        with col22:
            if st.form_submit_button("Back to Form"):
                st.switch_page("pages/kiyya_registerId.py")

    
        

if __name__ == '__main__':
    # make_sidebar()
    register()