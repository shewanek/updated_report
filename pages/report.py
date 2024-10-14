import streamlit as st
from time import sleep  # Assuming dash.py contains your dashboard layout
from navigation import make_sidebar2
           
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
        .css-1vbd788.e1tzin5v1 {
            display: none;
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
    with open('custom.css') as f:
        st.write(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    
    # image2 = Image.open('pages/coopbanck.gif')
    # image = Image.open('pages/michu.png')
    

    

    col1, col2, col3 = st.columns([0.1,0.7,0.1])
    
    # with col3:
    #     st.image(image)
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
        <center> <h3 class = "title_dash"> Michu Reporting Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # CSS to hide the first column on small screens
    hide_col1_css = """
        <style>
        @media (max-width: 600px) {
            .col3 {
                display: none;
            }
        }
        </style>
        """

    # Insert the custom CSS
    st.markdown(hide_col1_css, unsafe_allow_html=True)
    
    
    st.balloons()

    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.sidebar.image('pages/michu.png')
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar2()
    st.markdown(custom_cs, unsafe_allow_html=True)
    with st.form(key = 'Create_head_admin', clear_on_submit=True):
        # col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
        # with col2:
        # st.markdown('<div class="centered-form">', unsafe_allow_html=True)
        # if st.form_submit_button("Michu Women Targeted, Registered Report"):
        #     sleep(0.5)
        #     st.switch_page('pages/dash.py')
        # st.write("")
        # st.write("")
        col4, col5 = st.columns([0.7, 0.4])
        with col4:
            # if st.form_submit_button("Michu new customer  Dashboard"):
            #     sleep(0.5)
            #     st.switch_page('pages/unique_dash.py')
            # st.write("")
            # st.write("")
            # # if st.form_submit_button("Michu Conversion Dashboard"):
            # #     sleep(0.5)
            # #     st.switch_page('pages/conversion_dash.py')
            # # st.write("")
            # # st.write("")
            # if st.form_submit_button("Michu Kiyya Product Dashboard"):
            #     sleep(0.5)
            #     st.switch_page('pages/dureti_dash.py')
            if st.form_submit_button("Target Performance Report"):
                sleep(0.5)
                st.switch_page('pages/Actual_vs_Target.py')
        with col5:
            
            # if st.form_submit_button("Michu Customers Detail Report"):
            #     sleep(0.5)
            #     st.switch_page('pages/getdata.py')
            
            # if st.form_submit_button("Target Performance Report"):
            #     sleep(0.5)
            #     st.switch_page('pages/Actual_vs_Target.py')
           
            # st.info("NB: For the Michu Kiyya Campaign, we hide the other dashboard and focus on the Kiyya product beginning October 1.")
            if st.form_submit_button("Target Performance Kiyya Report"):
                sleep(0.5)
                st.switch_page('pages/kiyya_actual_vs_target.py')
        st.markdown('</div>', unsafe_allow_html=True)
    

    
        

if __name__ == '__main__':
    # make_sidebar()
    register()