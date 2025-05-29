import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from pages.changepassword import forget_password
from pages.reset_dash import resetpassword
from dependence import end_user_session

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

def make_sidebar():
    with st.sidebar:
        st.write(" ")
        # st.write(" ") 
        # st.write(" ")

        role = st.session_state.get("role", "")
        
        if role == 'Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.4, 0.6])
                

                with coll1:
                    if st.button("Home"):
                        home()

                with coll2:
                    if st.button("Add User"):
                        signup()
                col3, col4 = st.columns([0.6, 0.4])
                with col3:
                    if st.button('Change Password'):
                        password()
                with col4:
                    if st.button('LogOut'):
                        logout()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == 'Sales Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        sales_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                if st.button('Change Password'):
                    password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        elif role == "CRM" or role == "recomandation":
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.4, 0.7])
                with col3:
                    if st.button('LogOut'):
                        logout()
                with col4:
                    if st.button('Change Password'):
                        password()
            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
                
                

        elif role == "District User":
             # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        district_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                if st.button('Change Password'):
                    password()
        elif role == "Data Uploader":
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                st.write("") 
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.65, 0.35])
                with col4:
                    if st.button('LogOut'):
                        logout()
                with col3:
                    if st.button('Change Password'):
                        password()
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        
        elif role == 'collection_admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                

                col3, col4 = st.columns([0.65, 0.35])
                # with col3:
                #     if st.button("Home"):
                #         sales_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                with col3:
                    if st.button('Change Password'):
                        password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == 'collection_user':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                

                col3, col4 = st.columns([0.65, 0.35])
                # with col3:
                #     if st.button("Home"):
                #         sales_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                with col3:
                    if st.button('Change Password'):
                        password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()


        else:
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                st.write("") 
                st.write("") 
                
                # st.write(f"Welcome {username}")
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    if st.button('Reports'):
                        report()
                with col2:
                    if st.button("LogOut"):
                        logout()
               
                if st.button('Change Password'):
                    password()

                # if st.button('Reports'):
                #     report()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        # else:
        #     # Check both logged_in and sign_in session states
        #     if st.session_state.get("logged_in", False):
        #         st.write("") 
        #         # st.switch_page("pages/forgetpassword.py")

        #     elif get_current_page_name() != "main":
        #         # Redirect to the main page if the user is not logged in
        #         logout()

def make_sidebar1():
    with st.sidebar:
        # st.title("💎 Diamond Corp")
        st.write(" ")
        # st.write(" ") 
        # st.write(" ")

        role = st.session_state.get("role", "")
        if role == 'Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.4, 0.6])
                

                with coll1:
                    if st.button("Home"):
                        home()

                with coll2:
                    if st.button("Add User"):
                        signup()
                col3, col4 = st.columns([0.6, 0.4])
                with col3:
                    if st.button('Change Password'):
                        password()
                with col4:
                    if st.button('LogOut'):
                        logout()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        
        elif role == 'Sales Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        sales_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                # if st.button('Change Password'):
                #     password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == "District User":
             # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        district_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                # if st.button('Change Password'):
                #     password()
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()


        elif role == "Data Uploader":
             # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        data_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                # if st.button('Change Password'):
                #     password()
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        else:
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                st.write("") 
                st.write("") 
                
                # st.write(f"Welcome {username}")
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    if st.button('Home'):
                        branch_home()
                with col2:
                    if st.button("LogOut"):
                        logout()
               
                # if st.button('Change Password'):
                #     password()

                # if st.button('Reports'):
                #     report()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

def make_sidebar2():
    with st.sidebar:
        # st.title("💎 Diamond Corp")
        st.write(" ")
        st.write(" ") 
        st.write(" ")

        role = st.session_state.get("role", "")
        if role == 'Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.5, 0.5])
                

                with coll1:
                    if st.button("Add User"):
                        signup()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                col3, col4 = st.columns([0.6, 0.4])
                
                if st.button('Change Password'):
                    password()
                 
                if st.button('Reset User Password'):
                    reset()

                if st.button('Upload All Data'):
                    upload()
            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        elif role == "under_admin":
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                col1, col2 = st.columns([0.4, 0.6])

                with col1:
                    if st.button("LogOut"):
                        logout()
                with col2:
                    if st.button('Change Password'):
                        password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == "District User":
             # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # # Create two columns layout
                # coll1, coll2 = st.columns([0.4, 0.6])
                

                # with coll1:
                #     if st.button("Home"):
                #         home()

                col3, col4 = st.columns([0.5, 0.5])
                with col3:
                    if st.button("Home"):
                        district_home()
                with col4:
                    if st.button('LogOut'):
                        logout()
                
                if st.button('Change Password'):
                    password()
            
            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        else:
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                st.write("") 
                st.write("") 
                
                # st.write(f"Welcome {username}")
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    if st.button('Home'):
                        branch_home()
                with col2:
                    if st.button("LogOut"):
                        logout()
               
                if st.button('Change Password'):
                    password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

def home_sidebar():
    with st.sidebar:
        # st.title("💎 Diamond Corp")
        st.write(" ")
        st.write(" ") 
        st.write(" ")

        role = st.session_state.get("role", "")
        if role == 'Admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.6, 0.5])

                with coll1:
                    if st.button("Home"):
                        home()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                        # role = st.session_state.get("role", "") 
                        # st.session_state.role = ""
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == 'under_admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.6, 0.5])

                with coll1:
                    if st.button("Home"):
                        home_report()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                        # role = st.session_state.get("role", "") 
                        # st.session_state.role = ""
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
        elif role == 'CRM':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.6, 0.5])

                with coll1:
                    if st.button("Home"):
                        crm_home()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                        # role = st.session_state.get("role", "") 
                        # st.session_state.role = ""
                

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()

        elif role == 'collection_admin':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.6, 0.5])

                with coll1:
                    if st.button("Home"):
                        coladmin_home()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                        # role = st.session_state.get("role", "") 
                        # st.session_state.role = ""
        elif role == 'collection_user':
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                
                # Create two columns layout
                coll1, coll2 = st.columns([0.6, 0.5])

                with coll1:
                    if st.button("Home"):
                        coluser_home()

                with coll2:
                    if st.button("LogOut"):
                        logout()
                        # role = st.session_state.get("role", "") 
                        # st.session_state.role = ""

        else:
            # Check both logged_in and sign_in session states
            if st.session_state.get("logged_in", False):
                st.write("") 
                st.write("") 
                st.write("") 
                
                # st.write(f"Welcome {username}")

                col1, col2 = st.columns([0.35,0.65])
                with col1:
                    if st.button("LogOut"):
                        logout()
                with col2:
                    if st.button('Change Password'):
                        password()

            elif get_current_page_name() != "main":
                # Redirect to the main page if the user is not logged in
                logout()
def login_bar():
    if st.session_state.get("logged_in", False):
            st.write("") 
            # st.switch_page("pages/forgetpassword.py")

    elif get_current_page_name() != "main":
        # Redirect to the main page if the user is not logged in
        logout()
def logout():

    username = st.session_state.get("username", "")
    st.session_state["logged_in"] = False
    # st.session_state["username"] = ""
    # Clear caches
    # Clear all sensitive session data
    end_user_session(username)
    st.session_state.logged_in = False
    for key in ['username', 'password', 'role', 'full_name']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.clear()
    # st.rerun()
    st.info("Logged out successfully!")
    
    # sleep(0.5)
    st.switch_page("main.py")

    

def signup():
    # Update session state upon signing up
    st.session_state["sign_up"] = True
    st.info("Sign up successful!")
    sleep(0.5)
    st.switch_page("pages/district.py")
def password():
    # Update session state upon signing up
    st.session_state["logged_in"] = True
    # st.info("Sign up successful!")
    sleep(0.5)
    forget_password()
    # st.switch_page("pages/changepassword.py")
def home():
    # change to home
    st.session_state["logged_in"] = True
    st.info('go to successful!')
    sleep(0.5)
    st.switch_page("pages/dashboard.py")
def branch_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/register.py")

def district_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/district_dash.py")

def report():
    st.session_state["logged_in"] = True
    st.info('go to reports successful!')
    sleep(0.5)
    # st.switch_page("pages/branch_dash.py")

def reset():
    st.session_state["logged_in"] = True
    resetpassword()
    # st.info('go to reset successful!')
    # sleep(0.5)
    # st.switch_page("pages/reset_dash.py")

def sales_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/sales_dash.py")

def data_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/UploadData.py")

def coladmin_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/collection_dash.py")

def coluser_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/collection_userdash.py")

def home_report():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    sleep(0.5)
    st.switch_page("pages/report.py")

def crm_home():
    st.session_state["logged_in"] = True
    st.info('go to home successful!')
    st.switch_page("pages/dashB.py")

def upload():
    st.session_state["logged_in"] = True
    # st.info('go to home successful!')
    st.switch_page("pages/upload_all.py")