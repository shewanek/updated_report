import streamlit as st
from navigation import make_sidebar
from pages.dureati_reg import registerr
from pages.kiyya_register import kiyya_register

from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()
           
# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
    custom_cs = """
    <style>
        div.block-container {
            padding-top: 2.5rem; /* Adjust this value to reduce padding-top */
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
        .css-1vbd788.e1tzin5v1 {
            display: none;
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    
    
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)
    update_activity()


    col1, col2, col3 = st.columns([0.1,0.7,0.1])
   
    with col1:
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h3 class = "title_dash"> Michu Kiyya Reporting Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    
    
    
    # st.balloons()

    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # back_image = Image.open('pages/kiyya.jpg')
    st.sidebar.image('pages/kiyya.jpg')
    # st.sidebar.image('pages/michu.png')
    # username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    make_sidebar()
   
    st.markdown(custom_cs, unsafe_allow_html=True)
    try:
        
        col4, col5 = st.columns([0.6, 0.4])
        with col4:
            with st.form(key = 'Create_crmdash', clear_on_submit=True):
                
            
                if st.form_submit_button("Kiyya :orange[INFORMAL] Customer Registeration Form"):
                    kiyya_register()
                if st.form_submit_button("Kiyya :blue[FORMAL] Customer Registeration Form"):
                    registerr()
        with col5:
            st.write("")
            st.write("")
            with st.form(key = 'reporter', clear_on_submit=True):
                if st.form_submit_button("Detail Report"):

                    st.switch_page('pages/crm_report.py')
        
    except Exception as e:
            st.error(f"An error occurred while loading data: {e}")
        

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
    # make_sidebar()
    register()