import streamlit as st
from dependence import connect_to_database, validate_username, get_usernames, insert_crmuser, get_employe_usename, get_employe_id, get_employe_user
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
import json

# Establish database connection
# mydb = connect_to_database()

@st.dialog("Sign Up Here")
def sign_up():
    mydb = connect_to_database()
    with st.form(key='Create_sign_up_crm', clear_on_submit=True):
        # Input fields for employee ID, username, and password
        employe_id = st.text_input('Employee ID', key='id_input', placeholder='Enter your ID number')
        username = st.text_input('Username', key='username_input', placeholder='Enter Username')
        password1 = st.text_input('Password', key='password_input', placeholder='Enter Your Password', type='password')
        password2 = st.text_input('Confirm Password', key='confirm_password_input', placeholder='Confirm Your Password', type='password')

        # Submit button
        col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
        with col1:
            if st.form_submit_button(':orange[Register]'):
                if mydb is not None:
                    try:
                        cursor = mydb.cursor()
                        if not employe_id:
                            st.warning('Please enter your ID number.')
                        elif len(password1) < 6:
                            st.warning('Password must be at least 6 characters long.')
                        elif password1 != password2:
                            st.warning('Passwords do not match. Please re-enter your password.')
                        elif not get_employe_id(mydb, employe_id):
                            st.warning("You can't registered b/c of your employee ID is not found in our database. Please contact the admin.")
                        elif get_employe_user(mydb, employe_id):
                            st.warning("You've already registered; please use your username to log in on the login page.")
                        elif not validate_username(username):
                            st.warning('Please enter a valid username (use alphanumeric characters, at least 2 characters long).')
                        elif get_employe_usename(mydb, username):
                            st.warning('Username already exists. Please choose a different username.')
                        elif username in get_usernames(cursor):
                            st.warning('Username already exists. Please choose a different username.')
                        else:
                            if insert_crmuser(mydb, cursor, employe_id, username, password1):
                                st.success("You've successfully registered! Now you can log in using your username and password.")
                            else:
                                st.error("Registration failed. Please try again later.")
                    except Exception as e:
                        st.error(f"Failed to register user: {e}")
                    finally:
                        cursor.close()
                        mydb.close()
