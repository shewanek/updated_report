import streamlit as st
from time import sleep  # Assuming dash.py contains your dashboard layout
import json 
from navigation import login_bar
from navigation import home_sidebar
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()

# Main function to handle user sign-up
def sign_up():
    """
    Handles user sign-up process and form interactions.
    Resets input fields upon successful registration.
    """
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
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
    update_activity()
    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        st.image('pages/michu.png')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h2 class = "title_dash">Michu User Form </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    home_sidebar()

    # Access the selected role and district from session state
    role = st.session_state.get('selected_role', 'Select Role')
    district = st.session_state.get('selected_district', 'Select District')
    # st.write(district)
    if role == 'Sales Admin' or role == 'collection_user':
        district_json = json.dumps(district)
    elif role == 'Admin' or role == 'Data Uploader' or role == 'collection_admin' or role == 'under_admin':
        district_json = 'Head office'
    else:
        district_json = district
    # st.write(district)
    with st.form(key='Create Account', clear_on_submit=True):
        st.subheader('Add User')
        name_key = 'name_input'
        username_key = 'username_input'
        branch_key = 'branch_input'
        password_key = 'password_input'
        confirm_password_key = 'confirm_password_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter Full Name')
        username = st.text_input('Username', key=username_key, placeholder='Enter Username')

        
        
        # district_key = 'district_input'
        
        
        # Branch options depend on the selected district
        if role != 'Admin' and role != 'District User' and role != 'Sales Admin' and role != 'Data Uploader' and role != 'collection_admin' and role != 'collection_user' and role != 'under_admin' and role != 'recomandation':
            branch_options = ['Select Branch']
            try:
                from dependence import get_branch_from_db
                br_from_db = get_branch_from_db(district)
                if br_from_db:
                    branch_options.extend(br_from_db)
            except Exception:
                st.warning("Failed to retrieve branch from the database. Please try again later.")
            
            branch = st.selectbox('Branch', branch_options, key=branch_key)
        else:
            branch = None

        password1 = st.text_input('Password', key=password_key, placeholder='Enter Your Password', type='password')
        password2 = st.text_input('Confirm Password', key=confirm_password_key, placeholder='Confirm Your Password', type='password')

        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        with col1:
            if st.form_submit_button(':orange[Register]'):
                from dependence import validate_username, get_usernames, insert_user, is_branch_registered
                try:
                    if branch == 'Select Branch':
                        st.warning('Please select a branch.')
                    elif not validate_username(username):
                        st.warning('Please enter a valid username (use alphanumeric characters, at least 2 characters long).')
                    elif branch in is_branch_registered(branch):
                        st.warning(f"The branch {branch} is already registered. Please select a different branch.")
                    elif username in get_usernames():
                        st.warning('Username already exists. Please choose a different username.')
                    elif len(password1) < 6:
                        st.warning('Password must be at least 6 characters long.')
                    elif password1 != password2:
                        st.warning('Passwords do not match. Please re-enter your password.')
                    else:
                        if insert_user(name, username, district_json, branch, role, password1):
                            st.success(f"User, {name} has been successfully registered!")
                except Exception as e:
                    st.error(f"Failed to register user: {e}")


        if role == 'Admin' or role == 'Data Uploader' or role == 'collection_admin' or role == 'under_admin':
            with col2:
                st.write('change role')
            with col3:
                if st.form_submit_button("change"):
                    with st.spinner('Logging in...'):
                        sleep(0.5)
                    st.switch_page('pages/district.py')
        else:
            with col2:
                st.write('change District')
            with col3:
                if st.form_submit_button("change"):
                    with st.spinner('Logging in...'):
                        sleep(0.5)
                    st.switch_page('pages/districtt.py')
        
        # with col4:
        #     if st.form_submit_button("LogOut"):
        #         with st.spinner('Logging out...'):
        #             sleep(0.5)
        #         st.switch_page('main.py')

if __name__ == '__main__':
    sign_up()
