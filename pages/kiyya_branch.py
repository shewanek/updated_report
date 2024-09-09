import streamlit as st
from PIL import Image
from time import sleep  # Assuming dash.py contains your dashboard layout
from streamlit_extras.metric_cards import style_metric_cards
from navigation import make_sidebar1
from pages.kiyya_register import kiyya_register
from pages.dureati_reg import registerr
from dependence import connect_to_database, load_women_data, load_kiyya_data
           
# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
    custom_cs = """
    <style>
        div.block-container {
            padding-top: 1.8rem; /* Adjust this value to reduce padding-top */
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
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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
        <center> <h3 class = "title_dash"> Kiyya Reporting Portal </h3> </center>
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
    back_image = Image.open('pages/kiyya.jpg')
    st.sidebar.image(back_image)
    # st.sidebar.image('pages/michu.png')
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
   
    # back_image = Image.open('pages/kiyya.jpg')
    # st.sidebar.image(back_image)
                        
    make_sidebar1()
    st.markdown(custom_cs, unsafe_allow_html=True)
    mydb = connect_to_database()
    if mydb is not None:
        # combined_cust_by_crm, crm_cust_only = load_women_data(mydb)
        combined_cust_by_crm, crm_cust_only = load_kiyya_data(mydb)
        col4, col5 = st.columns([0.6, 0.4])
        with col4:
            with st.form(key = 'Create_crmdash', clear_on_submit=True):
                # col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                # with col2:
                # st.markdown('<div class="centered-form">', unsafe_allow_html=True)
                # if st.form_submit_button("Michu Women Targeted, Registered Report"):
                #     sleep(0.5)
                #     st.switch_page('pages/dash.py')
            
                if st.form_submit_button("Kiyya :orange[INFORMAL] Customer Registeration Form"):
                    kiyya_register()
                if st.form_submit_button("Kiyya :blue[FORMAL] Customer Registeration Form"):
                    registerr()
            
            col5.metric(label="**Total Registered Customer**", value=combined_cust_by_crm['kiyya_id'].nunique(), delta=" Already Disbursed for")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
            # st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
            <style>
                .stTabs [data-baseweb="tab"] {
                    margin-top: -0.9rem;
                    margin-right: 5rem; /* Adjust the value to increase or decrease space between tabs */
                    background-color: black;
                    color: white; /* Optional: Change text color */
                    padding: 0.5rem 1rem; /* Add some padding for better appearance */
                    border-bottom: 2px solid #00adef;
                }
                .stTabs [data-baseweb="tab"].active {
                border-bottom-color: cyan !important;
                }
            </style>
            """, unsafe_allow_html=True)
        # st.write(merge)
        tab1,= st.tabs(["Kiyya Registered Customer list"])
        with tab1:
            if (combined_cust_by_crm is not None and not combined_cust_by_crm.empty) or  (crm_cust_only is not None and not crm_cust_only.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered by You** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if combined_cust_by_crm is not None and not combined_cust_by_crm.empty:
                    st.write(combined_cust_by_crm.drop(columns=['kiyya_id', 'userId', 'userName', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
                    # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                    # csv = df.to_csv(index=False)
                    # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
                else:
                    st.info("You have no registered Kiyya customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered by You but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if crm_cust_only is not None and not crm_cust_only.empty:
                    st.info("NB: This customer is not countable as Kiyya customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(crm_cust_only.drop(columns=['kiyya_id', 'userId', 'userName', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("You have no registered   today.")
            else:
                st.info("You have no registered customers yet.")
        

    
    
if __name__ == '__main__':
    # make_sidebar()
    register()