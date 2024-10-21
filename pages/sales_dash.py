import streamlit as st
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
from navigation import make_sidebar
           
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
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    customm = """
        <style>
            .app-header {
                display: none;
            }
        </style>
        """

    # Apply the custom CSS
    st.markdown(customm, unsafe_allow_html=True)

    
    
    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
    with col1:
        # st.image(image)
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h3 class = "title_dash"> Michu Reporting Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    
    st.balloons()

    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar()
    st.markdown(custom_cs, unsafe_allow_html=True)
    with st.form(key = 'Create Account', clear_on_submit=True):
        col1, col2 = st.columns([0.7, 0.5])
        # with col1:
        #     # if st.form_submit_button("Michu Women Targeted, Registered Report"):
        #     #     sleep(0.5)
        #     #     st.switch_page('pages/sales_duretidash.py')
        #     # st.write("")
        #     # st.write("")
        #     if st.form_submit_button("Michu New Customer  Dashboard"):
        #         sleep(0.5)
        #         st.switch_page('pages/sales_uniquedash.py')
        #     st.write("")
        #     st.write("")
        #     if st.form_submit_button("Michu Kiyya Product Dashboard"):
        #         sleep(0.5)
        #         st.switch_page('pages/kiyya_sales.py')
            
        with col2:
            # if st.form_submit_button("Michu Customers Detail Report"):
            #     sleep(0.5)
            #     st.switch_page('pages/sales_data.py')

            # st.write("")
            # st.write("")
            if st.form_submit_button("Target Performance Report"):
                sleep(0.5)
                st.switch_page('pages/Actual_vs_Target.py')

   
        # with col4: 
        # with col3:
        #     if st.form_submit_button("LogOut"):
        #         sleep(0.5)
        #         st.switch_page('main.py')
        

if __name__ == '__main__':
    # make_sidebar()
    register()