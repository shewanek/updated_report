import streamlit as st
from dependence import connect_to_database, update_password
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
from navigation import login_bar


# Main function to handle user sign-up
def forget_password():
    """
    Handles user sign-up process and form interactions.
    Resets input fields upon successful registration.
    """
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
    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    image = Image.open('pages/michu.png')

    login_bar()

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        st.image(image)
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h2 class = "title_dash"> Michu  User Password </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    with st.form(key='change_password'):
        st.subheader('Change Password')
        current_password = st.text_input('Current Password', type='password')
        new_password = st.text_input('New Password', type='password')
        confirm_password = st.text_input('Confirm New Password', type='password')

        col1,col2,col3 = st.columns(3)
        username = st.session_state.get("username", "")
        # st.write(username)
        password = st.session_state.get("password", "")
    

        with col1:
            if st.form_submit_button('Change Password'):
                conn = connect_to_database()
                if conn:
                    cursor = conn.cursor()
                    if not current_password.strip():
                        st.error('Please enter your current password')
                    elif current_password == password:
                        if not new_password.strip():
                            st.error('Please enter new password')
                        elif len(new_password) < 6:
                            st.error('Password must be at least 6 characters long.')
                        elif new_password == confirm_password:
                            update_password(conn, cursor, username, new_password)
                            st.success('Password was successfully changed! Click the Login button to login again.')
                        else:
                            st.error('New password and confirmation do not match.')
                    else:
                        st.error('Incorrect current password.')
        with col2:
            st.write(' ')
        with col3:
            if st.form_submit_button("Login"):
                sleep(0.5)
                st.switch_page('main.py')
        

if __name__ == '__main__':
    # make_sidebar()
    forget_password()