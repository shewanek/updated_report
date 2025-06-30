import streamlit as st
from navigation import login_bar
from navigation import home_sidebar
from dependence import get_roles_from_db
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()


# Main function to handle user sign-up
def select():
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
    update_activity()
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

    col1, col2 = st.columns([0.1, 0.9])
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
        <center> <h2 class = "title_dash">Michu User Role </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    hide_sidebar_style = """
            <style>
                #MainMenu {visibility: hidden;}
            </style>
        """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    home_sidebar()
    with st.form(key='Create Account'):
        st.subheader('Select Role ')
        roles = ['Select Role']
        try:
            
            roles = ['Select Role']
            
            roles_from_db = get_roles_from_db()
            if roles_from_db:
                roles.extend(roles_from_db)
                 
            
            role_key = 'role_input'
            role = st.selectbox('Role', roles, key=role_key)
        except Exception as e:
            st.error(f"An error occurred while loading role: {e}")
        # role_key = 'role_input'
        # role = st.selectbox('Role', ['Select Role', 'Branch User', 'District User', 'Sales Admin', 'Admin'], key=role_key)
        
        
        if st.form_submit_button(':orange[Proceed]'):
            if role == 'Select Role':
                st.warning('Please select a role.')
            elif role == 'Admin' or role == 'Data Uploader' or role == 'collection_admin' or role == 'under_admin' or role == 'recomandation':
                st.session_state['selected_role'] = role
                st.switch_page('pages/Signup.py')
            else:
                st.session_state['selected_role'] = role
                st.switch_page('pages/districtt.py')
    
    # Footer implementation
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
    <p>Copyright Â© 2025 Michu Platform</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
        

if __name__ == '__main__':
    select()
