import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
from navigation import make_sidebar1
from dependence import connect_to_database, load_kiyya_branch_data, load_formal_branch_data
           
# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
    custom_cs = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
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
    
    
    back_image = Image.open('pages/kiyya.jpg')
    st.sidebar.image(back_image)
    # st.sidebar.image('pages/michu.png')
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
   
                        
    make_sidebar1()
    st.markdown(custom_cs, unsafe_allow_html=True)
    mydb = connect_to_database()
    if mydb is not None:
        
        b_combined_cust_by_crm, b_crm_cust_only = load_kiyya_branch_data(mydb)
        fb_combined_cust_by_crm, fb_crm_cust_only= load_formal_branch_data(mydb)
        # st.write(fb_crm_cust_only)


        start_dates = []
        end_dates = []


        

        if fb_combined_cust_by_crm is not None and not fb_combined_cust_by_crm.empty:
            start_dates.append(fb_combined_cust_by_crm["Disbursed Date"].min())
            end_dates.append(fb_combined_cust_by_crm["Disbursed Date"].max())

        if fb_crm_cust_only is not None and not fb_crm_cust_only.empty:
            start_dates.append(fb_crm_cust_only["registered_date"].min())
            end_dates.append(fb_crm_cust_only["registered_date"].max())

        if b_combined_cust_by_crm is not None and not b_combined_cust_by_crm.empty:
            start_dates.append(b_combined_cust_by_crm["Disbursed Date"].min())
            end_dates.append(b_combined_cust_by_crm["Disbursed Date"].max())

        if b_crm_cust_only is not None and not b_crm_cust_only.empty:
            # Convert "Register Date" to datetime and handle NaT values
            b_crm_cust_only["Register Date"] = pd.to_datetime(b_crm_cust_only["Register Date"], errors='coerce', unit='s')
            b_crm_cust_only["Register Date"] = b_crm_cust_only["Register Date"].dt.date

            # Filter out NaT values
            valid_dates = b_crm_cust_only["Register Date"].dropna()
            if not valid_dates.empty:
                min_date = valid_dates.min()
                max_date = valid_dates.max()
                start_dates.append(min_date)
                end_dates.append(max_date)

        if start_dates and end_dates:
            combined_start_date = min(start_dates)
            combined_end_date = max(end_dates)
        else:
            combined_start_date = None
            combined_end_date = None


        col1, col2 = st.sidebar.columns(2)
        with col1:
            date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        with col2:
            date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)

        
        date1 = pd.Timestamp(date1)
        date2 = pd.Timestamp(date2)

        

        fb_combined_cust_by_crm["Disbursed Date"] = pd.to_datetime(fb_combined_cust_by_crm["Disbursed Date"]).dt.date
        fb_combined_cust_by_crm = fb_combined_cust_by_crm[(fb_combined_cust_by_crm["Disbursed Date"] >= date1.date()) & (fb_combined_cust_by_crm["Disbursed Date"] <= date2.date())]

        fb_crm_cust_only["registered_date"] = pd.to_datetime(fb_crm_cust_only["registered_date"]).dt.date
        fb_crm_cust_only = fb_crm_cust_only[(fb_crm_cust_only["registered_date"] >= date1.date()) & (fb_crm_cust_only["registered_date"] <= date2.date())]

        b_combined_cust_by_crm["Disbursed Date"] = pd.to_datetime(b_combined_cust_by_crm["Disbursed Date"]).dt.date
        b_combined_cust_by_crm = b_combined_cust_by_crm[(b_combined_cust_by_crm["Disbursed Date"] >= date1.date()) & (b_combined_cust_by_crm["Disbursed Date"] <= date2.date())]

        b_crm_cust_only["Register Date"] = pd.to_datetime(b_crm_cust_only["Register Date"]).dt.date
        b_crm_cust_only = b_crm_cust_only[(b_crm_cust_only["Register Date"] >= date1.date()) & (b_crm_cust_only["Register Date"] <= date2.date())]
       
        # total_d_in = combined_cust_by_crm['kiyya_id'].nunique()
        # total_d_f = f_combined_cust_by_crm['wpc_id'].nunique()
        # unrtotal_d = crm_cust_only['kiyya_id'].nunique() + f_crm_cust_only['wpc_id'].nunique()

        untotal_b = b_crm_cust_only['kiyya_id'].nunique() + fb_crm_cust_only['wpc_id'].nunique()
        b_total_in = b_combined_cust_by_crm['kiyya_id'].nunique()
        b_total_f = fb_combined_cust_by_crm['wpc_id'].nunique()

        st.markdown("""
                <style>
                    .stTabs [data-baseweb="tab"] {
                        margin-top: -0.9rem;
                        margin-right: 13rem; /* Adjust the value to increase or decrease space between tabs */
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
        
        col1, col2, col3 = st.columns(3)
        col1.metric(label="**Total Infromal Customer**", value=b_total_in, delta=" Already Disbursed for")
        col2.metric(label="**Total Formal Customer**", value=b_total_f, delta=" Already Disbursed for")
        col3.metric(label="**Total Registered Customer (Informal + formal)**", value=untotal_b, delta=" Not Yet Disbursed for")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

        b_combined_cust_by_crm = b_combined_cust_by_crm.drop_duplicates(subset=['Saving Account'], keep='first')
        fb_combined_cust_by_crm = fb_combined_cust_by_crm.drop_duplicates(subset=['Saving Account'], keep='first')
        # st.write(fb_crm_cust_only)

        tab1, tab2 = st.tabs(["Kiyya Informal Customer List", "Kiyya Formal Customer List"])
        with tab1:
            if (b_combined_cust_by_crm is not None and not b_combined_cust_by_crm.empty) or  (b_crm_cust_only is not None and not b_crm_cust_only.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered by You** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if b_combined_cust_by_crm is not None and not b_combined_cust_by_crm.empty:
                    st.write(b_combined_cust_by_crm.drop(columns=['kiyya_id', 'userId']).reset_index(drop=True).rename(lambda x: x + 1))
                    
                else:
                    st.info("No branch or district has registered Kiyya Infprmal customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered by You but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if b_crm_cust_only is not None and not b_crm_cust_only.empty:
                    st.info("NB: This customer is not countable as Kiyya customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(b_crm_cust_only.drop(columns=['kiyya_id', 'userId']).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("No branch or district has registered Kiyya Informal Customer today.")
            else:
                st.info("No branch or district has registered Kiyya Informal customers yet.")

        with tab2:
            if (fb_combined_cust_by_crm is not None and not fb_combined_cust_by_crm.empty) or  (fb_crm_cust_only is not None and not fb_crm_cust_only.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered by You** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if fb_combined_cust_by_crm is not None and not fb_combined_cust_by_crm.empty:
                    st.write(fb_combined_cust_by_crm.drop(columns=['wpc_id', 'crm_id']).reset_index(drop=True).rename(lambda x: x + 1))
                    
                else:
                    st.info("No branch has registered Kiyya Formal customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered by You but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if fb_crm_cust_only is not None and not fb_crm_cust_only.empty:
                    st.info("NB: This customer is not countable as Kiyya customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(fb_crm_cust_only.drop(columns=['wpc_id', 'crm_id']).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("No branch or district has registered Kiyya Formal Customer today.")
            else:
                st.info("No branch or district has registered Kiyya Formal customers yet.")

    
    
if __name__ == '__main__':
    # make_sidebar()
    register()