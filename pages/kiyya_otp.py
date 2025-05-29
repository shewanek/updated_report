import streamlit as st
# from dependence import  validate_full_name
from navigation import login_bar
from navigation import make_sidebar1
from pages.kiyya_register import kiyya_register
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
        if st.form_submit_button("Proceed"):
            try:
                # validate form not empty
                if not otp_id:
                    st.error("Please enter a valid OTP.")
                    return
                
                headers = {"Content-Type": "application/json"}
                # Add payload if needed (adjust as per API requirements)
                payload = {
                    "otp": otp_id,
                    "transactionID": st.session_state.get("transactionID"),
                    "nationalId": st.session_state.get("national_id")   
                }
                # st.write(payload)

                response = requests.post("https://faydaintegration.dev.kifiya.et/getEkycData", headers=headers, json=payload)

                # Check if request was successful
                if response.status_code == 200:
                    data = response.json()
                    response_kyc_status = data.get("response", {}).get("kycStatus")

                    # Handle KYC status
                    if response_kyc_status and response_kyc_status.lower() == "true":
                        print(data.get("otp"))
                        print(data.get("transactionID"))
                        print(data.get("nationalId"))
                        
                        # Switch to OTP page
                        st.success("Redirecting to form page...")
                        kiyya_register()
                    else:
                        # # st.error("KYC failed or no response received. Please check your OTP.")
                        # # st.text(f"Response: {data}")
                        # st.error(data.get("errors"))
                        # if 'page_load_time' not in st.session_state:
                        #     st.session_state.page_load_time = datetime.now()

                        # # Check if 2 minutes have elapsed
                        # current_time = datetime.now()
                        # time_diff = current_time - st.session_state.page_load_time

                        # if time_diff.total_seconds() >= 120:  # 2 minutes in seconds
                        #     st.success("Session timeout - redirecting to registration page...")
                        #     time.sleep(2)
                        #     st.switch_page('pages/kiyya_registerId.py')
                        # Store the error message in session state
                        st.session_state.error_message = data.get("errors")
                        st.switch_page('pages/kiyya_registerId.py')
                else:
                    st.error(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
                    # st.text(f"Response Text: {response.text}")
                    # Add timestamp to session state if not exists
                    if 'page_load_time' not in st.session_state:
                        st.session_state.page_load_time = datetime.now()

                    # Check if 2 minutes have elapsed
                    current_time = datetime.now()
                    time_diff = current_time - st.session_state.page_load_time

                    if time_diff.total_seconds() >= 120:  # 2 minutes in seconds
                        st.success("Session timeout - redirecting to registration page...")
                        st.switch_page('pages/kiyya_registerId.py')
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching data: {str(e)}")

    
        

if __name__ == '__main__':
    # make_sidebar()
    register()