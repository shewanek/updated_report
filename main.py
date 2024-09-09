import streamlit as st
from dependence import connect_to_database, get_usernames, get_password_by_username, verify_password, get_role_by_username, get_fullname_by_username, get_crmusernames, get_crmpassword_by_username, get_role_by_crmusername, get_fullname_by_crmusername
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
import sys
sys.path.append('DASHBOARD')  # Assuming 'DASHBOARD' is the parent directory containing the 'pages' package

import sys
sys.path.append('DASHBOARD')  # Assuming 'DASHBOARD' is the parent directory containing the 'pages' package
# from pages import forgetp
from sign_in import sign_up


# Main function to handle user login
def main():
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    # hide_streamlit_style = """
    # <style>
    # #MainMenu{visibility: hidden;}
    # .stDeployButton {visibility: hidden;}
    # </style>
    # """
    # st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # login_bar()
    with open('custom.css') as f:
        st.write(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        # st.image(image)
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h3 class = "title_dash"> Michu Reporting Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # login_bar()
    # role = st.session_state.get('selected_role', 'Select Role')
    with st.form(key='login', clear_on_submit= True):
        st.subheader('Login Here')
        # Custom CSS to change the border color when the input field is focused
        custom_ss = """
            <style>
            /* Change border color of text input when focused */
            .stTextInput > div > div > input:focus {
                border-color: #00BFFF !important; /* Cyan blue color */
                box-shadow: 0 0 0 0.2rem rgba(0, 191, 255, 0.25) !important;
            }
            </style>
            """

        # Inject custom CSS into the Streamlit app
        st.markdown(custom_ss, unsafe_allow_html=True)
        username = st.text_input('Username', key='login_username_input', placeholder='Enter Your Username').strip()
        password = st.text_input('Password', key='login_password_input', placeholder='Enter Your Password', type='password')
        back_image = Image.open('pages/MichuHome.jpg')
        st.sidebar.image(back_image)

        # Display the rotating message
        st.sidebar.markdown('Welcome to <span style="color: #e38524;">MICHU</span> Reporting Portal<span style="color: #00adef; font-size: 20px;">!</span>', unsafe_allow_html=True)

        col1,col2 = st.columns([0.4,0.6])

       
        with col1:
            if st.form_submit_button('Log In'):
                mydb = connect_to_database()
                if mydb is not None:
                    cursor = mydb.cursor()
                    if not username.strip():
                        st.error('Please enter your username')
                    elif username in get_usernames(cursor):
                        stored_password = get_password_by_username(cursor, username)
                        if not password.strip():
                            st.error('Please enter your Password')
                        elif stored_password and verify_password(password, stored_password):
                            role = get_role_by_username(cursor, username)
                            full_name = get_fullname_by_username(cursor, username)
                            st.session_state.logged_in = True
                            st.session_state['username'] = username 
                            st.session_state['password'] = password
                            st.session_state['role'] = role

                            st.session_state['full_name'] = full_name
                            # st.success(f'Welcome back, {full_name}!')
                            st.sidebar.subheader(f'Welcome, {full_name}')
                            # return username  # Return authenticated username
                            if role == 'Admin':
                                sleep(0.5)
                                st.switch_page("pages/dashboard.py")
                            elif role == 'Branch User':
                                sleep(0.5)
                                st.switch_page("pages/register.py")
                            elif role == 'District User':
                                sleep(0.5)
                                st.switch_page("pages/district_dash.py")
                            elif role == 'Sales Admin':
                                sleep(0.5)
                                st.switch_page("pages/sales_dash.py")
                            elif role == 'Data Uploader':
                                sleep(0.5)
                                st.switch_page("pages/UploadData.py")
                            elif role == 'collection_admin':
                                sleep(0.5)
                                st.switch_page('pages/collection_dash.py')
                            elif role == 'collection_user':
                                sleep(0.5)
                                st.switch_page('pages/collection_userdash.py')
                            elif role == 'under_admin':
                                sleep(0.5)
                                st.switch_page('pages/report.py')
                                
                            else:
                                st.warning("No Role given for this User")
                            st.balloons()

                        else:
                            st.error('Incorrect Password. Please try again.')
                    elif username in get_crmusernames(cursor):
                        stored_password = get_crmpassword_by_username(cursor, username)
                        if not password.strip():
                            st.error('Please enter your Password')
                        elif stored_password and verify_password(password, stored_password):
                            role = get_role_by_crmusername(cursor, username)
                            full_name = get_fullname_by_crmusername(cursor, username)
                            st.session_state.logged_in = True
                            st.session_state['username'] = username 
                            st.session_state['password'] = password
                            st.session_state['role'] = role

                            st.session_state['full_name'] = full_name
                            # st.success(f'Welcome back, {full_name}!')
                            st.sidebar.subheader(f'Welcome, {full_name}')
                            # return username  # Return authenticated username
                            if role == 'CRM':
                                sleep(0.5)
                                st.switch_page("pages/dashB.py")
                                
                            else:
                                st.warning("No Role given for this User")
                            st.balloons()

                        else:
                            st.error('Incorrect Password. Please try again.')
                    else:
                        st.warning('Username not found. Please contact Admin if you are a new user.')
            
        # with  col2:
        col3, col4, col5 = st.columns([0.4,0.3, 0.3])
        with col3:
            st.write("")
            st.write("Don't have an account?")
        with col4:
            if st.form_submit_button('Sign Up'):
                sign_up()
        with col5:
            if st.form_submit_button('Forgot Password?'):
                sleep(0.5)
                st.switch_page("pages/forgetps.py")
   

if __name__ == '__main__':
    # login_bar()
    main()
    
