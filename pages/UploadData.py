import streamlit as st
# from PIL import Image
from time import sleep  
from navigation import make_sidebar
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()



# Main function to handle user sign-up
def upload():
    # Custom CSS to change button hover color to cyan blue
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
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
    # login_bar()
    st.markdown(custom_cs, unsafe_allow_html=True)
    update_activity()
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
        <center> <h2 class = "title_dash">Michu Upload Data Portal </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar()
    with st.form(key = 'Create Account', clear_on_submit=True):
        # df_combine
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
        tab1, tab2, tab3, tab4 = st.tabs(["Upload Actual Data", "Upload Target Data", "Upload Colection Data", "Upload Sales Data"])
        with tab1:
            col1, col2 = st.columns([0.4, 0.6])
            with col2:
                st.markdown('<div class="centered-form">', unsafe_allow_html=True)
                # if st.form_submit_button("Michu Women Targeted Registration Form"):
                #     sleep(0.5)
                #     st.switch_page('pages/duretiregister.py')
                # st.write("")
                # st.write("")
                if st.form_submit_button(f"Upload Actual :orange[Unique] Data"):
                    sleep(0.5)
                    st.switch_page('pages/uploadunique.py')
                st.write("")
                st.write("")
                if st.form_submit_button("Upload Actual :blue[Conversion] Data"):
                    sleep(0.5)
                    st.switch_page('pages/uploadconversion.py')
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        with tab2:
            col1, col2 = st.columns([0.4, 0.6])
            with col2:
                st.markdown('<div class="centered-form">', unsafe_allow_html=True)
                # # if st.form_submit_button("Michu Women Targeted Registration Form"):
                # #     sleep(0.5)
                # #     st.switch_page('pages/duretiregister.py')
                # # st.write("")
                # # st.write("")
                # if st.form_submit_button(f"Upload :orange[Unique] Data"):
                #     sleep(0.5)
                #     st.switch_page('pages/ActualData.py')
                # st.write("")
                # st.write("")
                if st.form_submit_button("Upload :blue[Target] Data"):
                    sleep(0.5)
                    st.switch_page('pages/TargetData.py')
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        with tab3:
            col1, col2 = st.columns([0.4, 0.6])
            st.markdown('<div class="centered-form">', unsafe_allow_html=True)
            with col2:
                if st.form_submit_button("Upload Colleaction Data"):
                    st.switch_page('pages/upload_coll.py')
                
                st.write("")
                st.write("")
                if st.form_submit_button("Upload conversion Data"):
                    st.switch_page('pages/upload_arrersconv.py')

                st.write("")
                st.write("")
                if st.form_submit_button("Upload due loan Data"):
                    st.switch_page('pages/upload_dueloan.py')
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        with tab4:
            col1, col2 = st.columns([0.4, 0.6])
            st.markdown('<div class="centered-form">', unsafe_allow_html=True)
            with col2:
                if st.form_submit_button("Upload Rejected Data"):
                    st.switch_page('pages/upload_reject.py')

                st.write("")
                st.write("")

                if st.form_submit_button("Upload Closed Data"):
                    st.switch_page('pages/upload_closed.py')

                st.write("")
                st.write("")

                if st.form_submit_button("Upload Prospect Data"):
                    st.switch_page('pages/upload_prospect.py')

                st.write("")
                st.write("")

                if st.form_submit_button("Upload CBS Data"):
                    st.switch_page('pages/upload_cbs.py')
                
                st.write("")
                st.write("")

                if st.form_submit_button("Upload emergance Data"):
                    st.switch_page('pages/upload_emergance.py')
                
                st.write("")
                st.write("")

                if st.form_submit_button("Upload Disbursment Data"):
                    st.switch_page('pages/upload_disb.py')
                    

                st.write("")
                st.write("")

                if st.form_submit_button("Upload Marchent Data"):
                    st.switch_page('pages/upload_merchat.py')

                st.write("")
                st.write("")

                if st.form_submit_button("Upload Loan Id Data"):
                    st.switch_page('pages/upload_loan_id.py')


                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

    # st.write("Last Uploaded Actual Data")
    try:
        from dependence import load_targetdata, load_uniqactualdata, load_convactualdata
        df_target = load_targetdata()
        # df_actual = load_actualdata()
        df_unique = load_uniqactualdata()
        df_conv = load_convactualdata()
        
        with tab1:
            st.markdown('<h5>Last Uploaded <span style="color: #e38524;"> Actual Unique </span> Data 👇🏻</h5>', unsafe_allow_html=True)
            st.write(df_unique.reset_index(drop=True).rename(lambda x: x + 1))
            st.write(" ")
            st.write(" ")
            # st.write("Last Uploaded Target Data")
            st.markdown('<h5>Last Uploaded <span style="color: #00adef;">Actual Conversion </span> Data 👇🏻</h5>', unsafe_allow_html=True)
            st.write(df_conv.reset_index(drop=True).rename(lambda x: x + 1))
        with tab2:
            # st.write("Last Uploaded Target Data")
            st.markdown('<h5>Last Uploaded <span style="color: #00adef;">Target </span> Data 👇🏻</h5>', unsafe_allow_html=True)
            st.write(df_target.reset_index(drop=True).rename(lambda x: x + 1))

    except Exception as e:
            st.error(f"An error occurred while loading data: {e}")
    
        

if __name__ == '__main__':
    # make_sidebar()
    upload()

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