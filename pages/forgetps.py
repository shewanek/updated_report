import streamlit as st
from dependence import connect_to_database, get_usernames, get_crmusernames
from PIL import Image
from time import sleep
from pages.forgetpassword import registertion
           
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
    
    # login_bar()  
    user_name = st.session_state.get('username', '') 
    with st.form(key = 'Create Account', clear_on_submit=True):
        # st.write('Send us the following information to reset you password')
        st.markdown('<h3 style="color: #e38524;">Please write your username to proceed 👇🏻</h3>', unsafe_allow_html=True)

        username = 'username_input'
        

        user_name = st.text_input('User Name ✍️', key=username, placeholder='Enter your username ')
        
        
        # Check if user is logged in
        # if "username" not in st.session_state:
        #     st.warning("No user found with the given username.")
        #     st.switch_page("main.py")
        
        col1,col3 = st.columns([0.8, 0.2])
        
        with col1:
            if st.form_submit_button(':orange[Proceed]'):
                mydb = connect_to_database()
                if mydb is not None:
                    cursor = mydb.cursor()
                    if  not user_name.strip():
                        st.warning('Please enter your user name to proceed')
                    elif user_name not in get_usernames(cursor) and user_name not in get_crmusernames(cursor):
                        st.warning('We do not have your user name in our database. If you\'re new or you can\'t remember your username, please try getting in touch with the administrator.') 
                    
                    
                    else:
                        st.session_state['username'] = user_name
                        registertion()
                        # st.switch_page("pages/forgetpassword.py")
                    cursor.close()
                    mydb.close()
        with col3:
            if st.form_submit_button(':orange[Log In]'):
                sleep(0.5)
                st.switch_page("main.py")
       
        # with col3:
        #     if st.form_submit_button("LogOut"):
        #         sleep(0.5)
        #         st.switch_page('main.py')
        

if __name__ == '__main__':
    
    register()