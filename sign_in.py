import streamlit as st

# Establish database connection
# mydb = connect_to_database()

@st.dialog("Sign Up Here")
@st.fragment
def sign_up():
    # Display the sign-up form
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
                from dependence import insert_crmuser

                try:
                    # Validate form inputs
                    if not validate_form(employe_id, username, password1, password2):
                        return

                    # If validation passes, insert the new user
                    if insert_crmuser(employe_id, username, password1):
                        st.success("You've successfully registered! Now you can log in using your username and password.")
                    else:
                        st.error("Registration failed. Please try again later.")
                except Exception as e:
                    st.error(f"Failed to register user: {e}")

# Validation function for form inputs
def validate_form(employe_id, username, password1, password2):
    from dependence import validate_username, get_usernames, get_employe_usename, get_employe_id, get_employe_user

    if not employe_id:
        st.warning('Please enter your ID number.')
        return False
    elif len(password1) < 6:
        st.warning('Password must be at least 6 characters long.')
        return False
    elif password1 != password2:
        st.warning('Passwords do not match. Please re-enter your password.')
        return False
    elif not get_employe_id(employe_id):
        st.warning("Your employee ID is not found in our database. Please contact the admin.")
        return False
    elif get_employe_user(employe_id):
        st.warning("You've already registered; please use your username to log in.")
        return False
    elif not validate_username(username):
        st.warning('Please enter a valid username (alphanumeric, at least 2 characters long).')
        return False
    elif get_employe_usename(username) or username in get_usernames():
        st.warning('Username already exists. Please choose a different username.')
        return False
    return True

