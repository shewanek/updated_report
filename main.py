import streamlit as st
import traceback
from dependence import initialize_session
from dependence import check_active_session
# from navigation import logout




# if 'last_activity' in st.session_state:
#     # Check if the session is active
#     if not check_active_session(st.session_state['username']):
#         # If the session is not active, reset the session state
#         st.session_state.clear()
#         st.warning("Your session has expired. Please log in again.")
#         logout()
    
def set_session_state(username, password, role, full_name):
    initialize_session(username)
    st.session_state.logged_in = True
    st.session_state['username'] = username
    st.session_state['password'] = password
    st.session_state['role'] = role
    st.session_state['full_name'] = full_name
    
    # st.rerun()

def display_sidebar_welcome(full_name):
    st.sidebar.subheader(f'Welcome, {full_name}')

def role_redirect(role):
    st.cache_data.clear()
    page_map = {
        'Admin': "pages/dashboard.py",
        'Branch User': "pages/register.py",
        'District User': "pages/district_dash.py",
        'Sales Admin': "pages/sales_dash.py",
        'Data Uploader': "pages/UploadData.py",
        'under_admin': "pages/report.py",
        'collection_admin':'pages/collection_dash.py',
        'collection_user':'pages/collection_userdash.py',
        'recomandation': "pages/upload_letter.py",
    }
    page = page_map.get(role)
    if page:
        st.switch_page(page)
    else:
        st.warning("No Role assigned for this User")

def crm_role_redirect(role):
    st.cache_data.clear()
    crm_page_map = {
        # 'CRM': "pages/dashB.py",
        'CRM': "pages/upload_letter.py",
        'report': "pages/kiyyaa_Report.py"
    }
    crm_page = crm_page_map.get(role)
    if crm_page:
        st.switch_page(crm_page)
    else:
        st.warning("No Role assigned for this CRM User")

def main():
    st.set_page_config(page_title="Michu Portal", page_icon=":bar_chart:", layout="centered")
    
    # CSS for custom styling
    custom_css = """
    <style>
        #MainMenu, .stDeployButton { visibility: hidden; }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80vh;
        }
        .login-box {
            width: 100%;
            max-width: 200px;  /* Adjusted width to make it narrower */
            padding: 1rem;     /* Reduced padding for a more compact look */
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .login-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #fff;
            margin-bottom: 0.5rem;  /* Reduced margin for compactness */
        }
        .login-input {
            width: 100%;
            padding: 0.4rem;
            font-size: 0.9rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 0.5rem;  /* Reduced margin for compactness */
        }
        
        .stButton button {
            background-color: #000;
            color: #fff;
            padding: 0.4rem 0.8rem;
            font-size: 0.9rem;
            cursor: pointer;
            border-radius: 4px;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #00bfff;
            color: #fff;
        }
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
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Container for the login box
    with st.container():
        with st.container():
            st.sidebar.image('pages/MichuHome.jpg')

            # Display the rotating message
            st.sidebar.markdown('Welcome to <span style="color: #e38524;">MICHU</span> Reporting Portal<span style="color: #00adef; font-size: 20px;">!</span>', unsafe_allow_html=True)

            col1, col2 = st.columns([0.2,0.9])
            with col1:
                st.image('pages/coopbanck.gif')
            with col2:
                st.markdown("<h2 class='login-title'>Michu Reporting Portal</h2>", unsafe_allow_html=True)

            # Login Form
            with st.form(key='login_form', clear_on_submit=True):
                username = st.text_input('Username', placeholder='Enter Username').strip()
                password = st.text_input('Password', placeholder='Enter Password', type='password')
                
                if st.form_submit_button('Log In'):
                    if not username or not password:
                        st.error("⚠️ Username and Password are required.")
                    else:
                        from dependence import (
                                get_usernames, get_password_by_username, verify_password, get_role_by_username,
                                get_fullname_by_username, get_crmusernames, get_crmpassword_by_username, 
                                get_role_by_crmusername, get_fullname_by_crmusername
                            )
                        try:
                            if check_active_session(username):
                                st.warning(
                                    f"⚠️ The username '{username}' is currently active in another session.\n\n"
                                    "🔒 Note: This system allows only **one active session per user** at a time (single-session-per-user policy).\n\n"
                                    "👉 If you're not sure who is logged in, please make sure to **keep your password secure** and consider changing it to ensure account safety."
                                )

                            elif username in get_usernames():
                                stored_password = get_password_by_username(username)
                                if verify_password(password, stored_password):
                                    
                                    role = get_role_by_username(username)
                                    full_name = get_fullname_by_username(username)
                                    set_session_state(username, password, role, full_name)
                                    display_sidebar_welcome(full_name)
                                    role_redirect(role)
                                else:
                                    st.error("⚠️ Incorrect password. Please try again.")
                            elif username in get_crmusernames():
                                stored_password = get_crmpassword_by_username(username)
                                if verify_password(password, stored_password):
                                    role = get_role_by_crmusername(username)
                                    full_name = get_fullname_by_crmusername(username)
                                    set_session_state(username, password, role, full_name)
                                    display_sidebar_welcome(full_name)
                                    crm_role_redirect(role)
                                else:
                                    st.error("⚠️ Incorrect password. Please try again.")
                            else:
                                st.warning("⚠️ Username not found. Please contact the admin if you are a new user.")
                        except Exception as e:
                            st.error("Failed to login")
                            # Print a full stack trace for debugging
                            print("Database fetch error:", e)
                            traceback.print_exc()  # This prints the full error trace to the terminal

            # Sign Up and Forgot Password Links
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Sign Up'):
                    from sign_in import sign_up
                    sign_up()
            with col2:
                if st.button('Forgot Password?'):
                    from pages.forgetps import register
                    register()

            st.write("")
            st.write("")
            st.write("")
            st.subheader("📊 Collection Report")
            st.write("Access the full collection report by clicking the button below:")
            st.link_button("Go to Collection Report", "http://10.101.200.140:4050/michu/login")


    # Footer
    footer = """
    <div class='footer'>
        <p>Copyright Â© 2025 Michu Platform. All Rights Reserved. </p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
   
if __name__ == '__main__':
    main()
    
