import streamlit as st
from time import sleep  # Assuming dash.py contains your dashboard layout
from navigation import login_bar
from navigation import make_sidebar
from pages.kiyya_register import kiyya_register
from pages.dureati_reg import registerr
from pages.unique_register import unique_register
# from pages.dureati_reg import registerr
from dependence import update_activity, check_session_timeout, get_branchcode


# Check timeout on every interaction
check_session_timeout()



# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
    custom_cs = """
    <style>
        div.block-container {
            padding-top: 0rem; /* Adjust this value to reduce padding-top */
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
    login_bar()
    st.markdown(custom_cs, unsafe_allow_html=True)
    update_activity()
  
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
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    # Fiscal year options with corresponding date ranges
    fiscal_year_mapping = {
        "2024/2025": ("2024-07-01", "2025-06-30"),
        "2025/2026": ("2025-07-01", "2026-06-30")
    }

    # Dropdown for display
    selected_label = st.sidebar.selectbox(
        "Select Fiscal Year",
        list(fiscal_year_mapping.keys()),
        index=1  # Default to 2025/2026 (adjust if needed)
    )

    # Retrieve corresponding date range
    start_date, end_date = fiscal_year_mapping[selected_label]

    # Store in session state for later use
    st.session_state["fiscal_year_label"] = selected_label
    st.session_state["fiscal_year_start"] = start_date
    st.session_state["fiscal_year_end"] = end_date

    # Read the selection
    fy_label = st.session_state.get("fiscal_year_label")
    fy_start = st.session_state.get("fiscal_year_start")
    fy_end = st.session_state.get("fiscal_year_end")

    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar()
    st.balloons()
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        
        st.markdown('<h5><span style="color: #00adef;">Form </span> 👇🏻</h5>', unsafe_allow_html=True)
        with st.form(key = 'forms', clear_on_submit=True):
        
            if st.form_submit_button("Michu New/Unique Customer Registration Form"):
                unique_register()
            st.write("")
          
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
           
            if st.form_submit_button("Kiyya :blue[FORMAL] Customer Registeration Form"):
                registerr()
            st.write("")

            if st.form_submit_button("Kiyya :orange[INFORMAL] Customer Registeration Form"):
                if get_branchcode(username):
                    st.switch_page('pages/kiyya_registerId.py')
                else:
                    kiyya_register()
            
            
    with col2:
        
      
        # st.info("NB: For the Michu Kiyya Campaign, we hide the other dashboard and focus on the Kiyya product beginning October 1.")
        st.markdown('<h5><span style="color: #e38524;">Report </span> 👇🏻</h5>', unsafe_allow_html=True)
        with st.form(key = 'reports', clear_on_submit=True):
            # # st.markdown('<div class="centered-form">', unsafe_allow_html=True)
            # if st.form_submit_button("Michu Unique Customers Detail Report"):
            #     sleep(0.5)
            #     st.switch_page('pages/branch_dash.py')
            
            # if st.form_submit_button("Michu Collection Report"):
            #     sleep(0.5)
            #     st.switch_page('pages/status.py')
            
            if st.form_submit_button("Target Performance Report"):
                sleep(0.5)
                st.switch_page('pages/Actual_vs_Target.py')

            st.write("")
            if st.form_submit_button("Retention Data Report"):
                sleep(0.5)
                # st.write("under development")
                st.switch_page('pages/sales_status.py')
            # if st.form_submit_button("Target Performance Report Kiyya(Informal & Formal)"):
            #     sleep(0.5)
            #     st.switch_page('pages/kiyya_actual_vs_target.py')
            # # # st.write("")
            st.write("")
            if st.form_submit_button("Upload Recommendation Letter"):
                sleep(0.5)
                # st.write("under development")
                st.switch_page('pages/upload_letter.py')
            
            # st.markdown('</div>', unsafe_allow_html=True)
    # with st.form(key = 'Create_head_sales', clear_on_submit=True):
    #     coll1, coll2 = st.columns([0.5, 0.5])
    #     with coll1:
    #         if st.form_submit_button("Retention Data Report"):
    #                 sleep(0.5)
    #                 # st.write("under development")
    #                 st.switch_page('pages/sales_status.py')

    #         with coll2:
    #             if st.form_submit_button("Upload Recomadation Letter"):
    #                 sleep(0.5)
    #                 # st.write("under development")
    #                 st.switch_page('pages/upload_letter.py')
    #             # if st.form_submit_button("Collection & Conversion Data Report"):
    #             #     sleep(0.5)
    #             #     # st.write("under development")
    #             #     st.switch_page('pages/conversion_dash.py')
    

    # with st.form(key = 'upload_recomadation', clear_on_submit=True):
        
    #     if st.form_submit_button("Upload Recomadation Letter"):
    #             sleep(0.5)
    #             # st.write("under development")
    #             st.switch_page('pages/upload_letter.py')
            
    
        

if __name__ == '__main__':
    # make_sidebar()
    register()

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