import streamlit as st
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
from navigation import login_bar
from navigation import make_sidebar
from pages.kiyya_register import kiyya_register
from pages.dureati_reg import registerr
from pages.unique_register import unique_register
# from pages.dureati_reg import registerr



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
    login_bar()
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
        <center> <h2 class = "title_dash">Michu Reporting Portal </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    # username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar()
    col1, col2 = st.columns([0.7, 0.5])
    
    with col1:
        # st.subheader(":blue[Form]")
        st.write(" ")
        st.write(" ")
        st.markdown('<h5><span style="color: #00adef;">Form </span> 👇🏻</h5>', unsafe_allow_html=True)
        with st.form(key = 'forms', clear_on_submit=True):
        
            if st.form_submit_button("Michu New/Unique Customer Registration Form"):
                unique_register()
            # # st.write("")
            # # st.write("")
            # # # if st.form_submit_button("Michu Collection & Conversion Report Form "):
            # # #     sleep(0.5)
            # # #     st.switch_page('pages/conversionregister.py')
            # # # st.markdown('</div>', unsafe_allow_html=True)
            # if st.form_submit_button("Michu Kiyya Product Report"):
            #     # registerr()
            #     sleep(0.5)
            #     st.switch_page('pages/kiyya_branch.py')
            st.write("")
            if st.form_submit_button("Kiyya :orange[INFORMAL] Customer Registeration Form"):
                kiyya_register()
            st.write("")
            if st.form_submit_button("Kiyya :blue[FORMAL] Customer Registeration Form"):
                registerr()
            
    with col2:
        
        # st.subheader(":orange[Report]") 
        st.write(" ")
        st.write(" ")
        # st.info("NB: For the Michu Kiyya Campaign, we hide the other dashboard and focus on the Kiyya product beginning October 1.")
        st.markdown('<h5><span style="color: #e38524;">Report </span> 👇🏻</h5>', unsafe_allow_html=True)
        with st.form(key = 'reports', clear_on_submit=True):
            # st.markdown('<div class="centered-form">', unsafe_allow_html=True)
            if st.form_submit_button("Michu Customers Detail Report"):
                sleep(0.5)
                st.switch_page('pages/branch_dash.py')
            st.write("")
            if st.form_submit_button("Target Performance Report"):
                sleep(0.5)
                st.switch_page('pages/Actual_vs_Target.py')

            st.write("")
            if st.form_submit_button("Target Performance Kiyya Report"):
                sleep(0.5)
                st.switch_page('pages/kiyya_actual_vs_target.py')
            # # st.write("")
            # # st.write("")
            
            # st.markdown('</div>', unsafe_allow_html=True)
            
    
   
        

if __name__ == '__main__':
    # make_sidebar()
    register()