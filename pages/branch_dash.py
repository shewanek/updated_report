import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import mysql.connector
import plotly.express as px
import time
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from PIL import Image
import streamlit_authenticator as stauth
import hashlib
import os
from dependence import connect_to_database, load_branchdata, load_customer_detail
from navigation import make_sidebar1

from TheStream.CollectedData import collectionData, role_fetch

from TheStream.AddingCollection import arrears_acess, role_fetch #InArrearsData, 



def initialize_session():
    if "selectedRow" in st.session_state:
        st.session_state.selectedRow=None
    if "collectionDatas" in st.session_state:
        st.session_state.collectionDatas=[]

    if "collectionSelection" in st.session_state:
        st.session_state.collectionSelection=None

def colmain():

    initialize_session()
    branch_code, role = role_fetch()

    def reset_selected_row():
        st.session_state.selectedRow = None
        st.session_state.collectionSelection = None
    
    
    tab1, tab2 = st.tabs(["In Arrears Loan", "Collection Status"])

    with tab1:
        arrears_acess(branch_code, role)
    with tab2:
        collectionData(branch_code, role)



def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    with open('custom.css') as f:
        st.write(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Auto-refresh interval (in seconds)
    refresh_interval = 6600  # Adjust as needed (e.g., 10 minutes for real-time)
    st_autorefresh(interval=refresh_interval * 1000, key="Michu Bot dash")

    image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image)
    html_title = """
        <style>
        .title_dash {
            font-weight:bold;
            padding:1px;
            border-radius:6px
        }
        </style>
        <center> <h3 class="title_dash"> Michu Customers Detail Report (<span style="color: #00adef; font-size: 20px;">Year-To-Date</span>) </h3> </center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    st.balloons()

    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Fetch data from different tables
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
        
    mydb = connect_to_database()
    if mydb is not None:
        dureti_customer, unique_customer, conversion_customer, unique_cust_by_branch, unique_cust_by_self, registed_by_branch = load_branchdata(mydb)
        df_combine_closed, df_combine_active, df_combine_arrears = load_customer_detail(mydb)
        # unique_customer
        # conversion_customer
        # Sidebar
        st.sidebar.image("pages/michu.png")
        username = st.session_state.get("username", "")
        full_name = st.session_state.get("full_name", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

        # # Set combined min and max dates
        # combined_start_date = min(dureti_customer["Register Date"].min(), unique_customer["Disbursed Date"].min(), conversion_customer["Collection Date"].min())
        # combined_end_date = max(dureti_customer["Register Date"].max(), unique_customer["Disbursed Date"].max(), conversion_customer["Collection Date"].max())

        start_dates = []
        end_dates = []


        if unique_customer is not None and not unique_customer.empty:
            start_dates.append(unique_customer["Disbursed Date"].min())
            end_dates.append(unique_customer["Disbursed Date"].max())

        if unique_cust_by_branch is not None and not unique_cust_by_branch.empty:
            start_dates.append(unique_cust_by_branch["Disbursed_Date"].min())
            end_dates.append(unique_cust_by_branch["Disbursed_Date"].max())

        if unique_cust_by_self is not None and not unique_cust_by_self.empty:
            start_dates.append(unique_cust_by_self["Disbursed Date"].min())
            end_dates.append(unique_cust_by_self["Disbursed Date"].max())
        
        if registed_by_branch is not None and not registed_by_branch.empty:
            start_dates.append(registed_by_branch["Disbursed_Date"].min())
            end_dates.append(registed_by_branch["Disbursed_Date"].max())

        # if df_combine_active is not None and not df_combine_active.empty:
        #     start_dates.append(df_combine_active["Approved Date"].min())
        #     end_dates.append(df_combine_active["Approved Date"].max())
        
        # if df_combine_arrears is not None and not df_combine_arrears.empty:
        #     start_dates.append(df_combine_arrears["Approved Date"].min())
        #     end_dates.append(df_combine_arrears["Approved Date"].max())

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

        unique_customer = unique_customer[(unique_customer["Disbursed Date"] >= date1) & (unique_customer["Disbursed Date"] <= date2)]
        unique_cust_by_branch = unique_cust_by_branch[(unique_cust_by_branch["Disbursed_Date"] >= date1) & (unique_cust_by_branch["Disbursed_Date"] <= date2)]
        unique_cust_by_self = unique_cust_by_self[(unique_cust_by_self["Disbursed Date"] >= date1) & (unique_cust_by_self["Disbursed Date"] <= date2)]

        registed_by_branch = registed_by_branch[(registed_by_branch["Disbursed_Date"] >= date1) & (registed_by_branch["Disbursed_Date"] <= date2)]
        # df_combine_closed = df_combine_closed[(df_combine_closed["Approved Date"] >= date1) & (df_combine_closed["Approved Date"] <= date2)]
        # df_combine_active = df_combine_active[(df_combine_active["Approved Date"] >= date1) & (df_combine_active["Approved Date"] <= date2)]
        # df_combine_arrears = df_combine_arrears[(df_combine_arrears["Approved Date"] >= date1) & (df_combine_arrears["Approved Date"] <= date2)]

        # Hide the sidebar by default with custom CSS
        hide_sidebar_style = """
            <style>
                #MainMenu {visibility: hidden;}
            </style>
        """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)
        make_sidebar1()

        st.markdown(
            """
            <style>
            .metric-card-container {
                padding-top: 0.2rem;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        col1, col2, col3, col4= st.columns(4)
        # col3.metric(label="**Total Targeted Women**", value=dureti_customer['customerId'].nunique(), delta="Registered Customer")
        col1.metric(label="**Total New/Unique**", value=unique_customer['uniqId'].nunique(), delta=" Customer")
        # col2.metric(label="**Total Conversion Customer**", value=conversion_customer['conId'].nunique(), delta="Registered Customer")
        col2.metric(label="**Total In Arrears**", value=df_combine_arrears['cust_id'].nunique(), delta="Customer")
        col3.metric(label="**Total Closed**", value=df_combine_closed['cust_id'].nunique(), delta="Customer")
        col4.metric(label="**Total Active**", value=df_combine_active['cust_id'].nunique(), delta="Customer")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
        # col2.info("Note: This report contains unique customers, As of August 1st ")

        # # # Display data in a table
        # # st.markdown('<h4 style="color: #e38524;">Registered Customer List 👇🏻</h4>', unsafe_allow_html=True)
        # st.markdown("""
        # <style>
        #     [data-testid="stElementToolbar"] {
        #     display: none;
        #     }
        # </style>
        # """, unsafe_allow_html=True)

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
        tab1, tab2, tab3, tab4 = st.tabs(["Unique", "In Arrears", "Closed", "Active"])
        with tab1:
            st.markdown('<span style="color: #e38524;">**Registered by Branch** (<span style="color: #00adef;">which has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            if unique_cust_by_branch is not None and not unique_cust_by_branch.empty:
                st.write(unique_cust_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
                # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                # csv = df.to_csv(index=False)
                # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
            else:
                st.info("There are no customers registered by your branch.")

            st.markdown('<span style="color: #e38524;">**Self Registered** (<span style="color: #00adef;">which has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            if unique_cust_by_self is not None and not unique_cust_by_self.empty:
                st.write(unique_cust_by_self.reset_index(drop=True).rename(lambda x: x + 1))
                # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                # csv = df.to_csv(index=False)
                # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
            else:
                st.info("There are no self-registered customers at your branch.")
            

            # st.markdown('<span style="color: #e38524;">**Today Registered By Branch (Live)**</span> 👇🏻', unsafe_allow_html=True)

            st.markdown('<span style="color: #e38524;">**Registered by the branch, but  has not yet been disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
            if registed_by_branch is not None and not registed_by_branch.empty:
                st.info("NB: This customer is not countable as unique until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered branch, but rather for where the account is open.")
                st.write(registed_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
                # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                # csv = df.to_csv(index=False)
                # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
            else:
                st.info("There are no registered customers at your branch today.")
            

        with tab2:
            # st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">In Arrears Status </span>)</span> 👇🏻', unsafe_allow_html=True)
            # st.write(df_combine_arrears.drop(columns=['cust_id']).reset_index(drop=True).rename(lambda x: x + 1))
            colmain()
        with tab3:
            st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed Status </span>)</span> 👇🏻', unsafe_allow_html=True)
            if df_combine_closed is not None and not df_combine_closed.empty:
                st.write(df_combine_closed.drop(columns=['cust_id', 'Approved Amount','Approved Date','Expiry Date','Oustanding Total','Arrears Start Date']).reset_index(drop=True).rename(lambda x: x + 1))

            else:
                st.info("There is no closed loan status at your branch")
            
        with tab4:
            st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Active Status </span>)</span> 👇🏻', unsafe_allow_html=True)
            if df_combine_active is not None and not df_combine_active.empty:
                st.write(df_combine_active.drop(columns=['cust_id']).reset_index(drop=True).rename(lambda x: x + 1)) 
            else:
                st.info("There is no active loan status at your branch")
        

        

if __name__ == "__main__":
    main()

