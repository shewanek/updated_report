import streamlit as st
from dependence import connect_to_database, insert_resetpuser, validate_full_name, validate_email, has_user_sent_request_today
from PIL import Image
from time import sleep



# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
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
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    # login_bar()
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
        <center> <h3 class = "title_dash">Michu Password Reset </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    username = st.session_state.get('username', '')
    # st.write(username)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    # login_bar()   
    with st.form(key = 'Create Account', clear_on_submit=True):
        # st.write('Send us the following information to reset you password')
        st.markdown('<h3 style="color: #e38524;">Send us the following information to reset you password 👇🏻</h3>', unsafe_allow_html=True)
        name_key = 'name_input'
        email = 'email_input'
        branch = 'region_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name')
        outlook_email = st.text_input('Outlook Email', key=email, placeholder='Enter your outlook email')
        branch_name = st.text_input('District/Branch', key = branch, placeholder='Enter your district or branch')
        

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':orange[Send]'):
                mydb = connect_to_database()
                if mydb is not None:
                    cursor = mydb.cursor()
                    if not validate_full_name(name):
                        st.warning('Please enter valid name (First name and father name)') 
                    elif not validate_email(outlook_email):
                        st.warning('Please enter a valid email address (Your Outlook email)')
                    elif not branch_name.strip():
                        st.warning('Please provide your district name if you are from CBO district, or your branch name if you are from CBO branch.')
                    else:
                        # Check if user has already sent a request today
                        if has_user_sent_request_today(cursor, username):
                            st.warning('You have already submitted a reset request. Please check your Outlook email; we will send it to you; please wait patiently.')
                    
                        else:  
                            if insert_resetpuser(mydb, cursor, username, name, outlook_email, branch_name):
                                st.success(f"Your password reset request (for {username} user name) was received successfully!. We sent you the reset password via Outlook email; check your inbox after an hour.")
                                sleep(5)
                                st.switch_page("main.py")
                    cursor.close()
                    mydb.close()
        with col3:
            if st.form_submit_button(':Gold[Log In]'):
                sleep(0.5)
                st.switch_page("main.py")
       
        

if __name__ == '__main__':
    
    register()