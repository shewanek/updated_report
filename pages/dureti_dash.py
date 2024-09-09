import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from PIL import Image
from dependence import connect_to_database, load_all_women_data, load_kiyya_data
from navigation import home_sidebar
from datetime import date


def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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
    st.markdown(custom_cs, unsafe_allow_html=True)
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
    refresh_interval = 600  # 5 minutes
    st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")

    image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1, 0.9])
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
        <center> <h4 class = "title_dash"> Michu Kiyya Customers Detail Report (<span style="color: #00adef; font-size: 20px;">Year-To-Date</span>)</h4> </center>
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

    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    mydb = connect_to_database()
    if mydb is not None:
        cursor = mydb.cursor()


        combined_cust_by_crm, crm_cust_only = load_all_women_data(mydb)
        merged_df_1, merged_df_2 = load_kiyya_data(mydb)

        crm_cust_only['wpc_id'].nunique()

        start_dates = []
        end_dates = []


        if combined_cust_by_crm is not None and not combined_cust_by_crm.empty:
            start_dates.append(combined_cust_by_crm["Disbursed Date"].min())
            end_dates.append(combined_cust_by_crm["Disbursed Date"].max())

        if crm_cust_only is not None and not crm_cust_only.empty:
            start_dates.append(crm_cust_only["registered_date"].min())
            end_dates.append(crm_cust_only["registered_date"].max())

        if start_dates and end_dates:
            combined_start_date = min(start_dates)
            combined_end_date = max(end_dates)
        else:
            combined_start_date = None
            combined_end_date = None
       
       
       

        back_image = Image.open('pages/kiyya.jpg')
        st.sidebar.image(back_image)
        username = st.session_state.get("username", "")
        full_name = st.session_state.get("full_name", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
        

        col1, col2 = st.sidebar.columns(2)
        with col1:
            date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        with col2:
            date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)




        combined_cust_by_crm = combined_cust_by_crm[(combined_cust_by_crm["Disbursed Date"] >= date1) & (combined_cust_by_crm["Disbursed Date"] <= date2)]
        crm_cust_only = crm_cust_only[(crm_cust_only["registered_date"] >= date1) & (crm_cust_only["registered_date"] <= date2)]
        


        # Hide the sidebar by default with custom CSS
        hide_sidebar_style = """
            <style>
                #MainMenu {visibility: hidden;}
            </style>
        """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)
        home_sidebar()

        # st.markdown(
        #     """
        #     <style>
        #     .metric-card-container {
        #         padding-top: 0.2rem;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True
        # )
         # df_combine
         

        # Get today's date
        today = date.today()
        crm_cust_today = crm_cust_only[crm_cust_only['registered_date'] == today]

        # Get the count of unique 'wpc_id' for today
        total_registered_today = crm_cust_today['wpc_id'].nunique()

        # Calculate the total number of registered customers
        total_registered = combined_cust_by_crm['wpc_id'].nunique()
        total_by_branch = merged_df_1['kiyya_id'].nunique()
        total_correct = total_registered + total_by_branch

        total_notcounted = crm_cust_only['wpc_id'].nunique()
        total_not_counted_bybr = merged_df_2['kiyya_id'].nunique()
        total_not_counted = total_notcounted + total_not_counted_bybr

        
        
        col1, col2, col3 = st.columns(3)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Registered Customer**", value=total_correct, delta="Already Disburesed for")
        # Use st.markdown to add custom styling for the delta text
        col2.metric(label="**Total Registered Customer**", value=total_not_counted, delta="Not yet Disburesed")
        col3.metric(label="**Total Registered Customer Today**", value=total_registered_today, delta="Not yet Disburesed")
        # col4.metric(label="**Total Active**", value=df_combine_active.cust_id.nunique(), delta="Customer")
        # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
        # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
        style_metric_cards(background_color="#e38524", border_left_color="#00adef", border_color="#1f66bd", box_shadow="#f71938")

        # # Display combined data in a table
        # st.write(":orange[Michu Women Targeted Customer List 👇🏻]")
        # st.write(df_combine.drop(columns=['customerId', 'userName']).reset_index(drop=True).rename(lambda x: x + 1))
        # df = df_combine.drop(columns=['customerId', 'userName'])
        # csv = df.to_csv(index=False)
        # st.download_button(label=":blue[Download CSV]", data=csv, file_name='Women_Targeted_data.csv', mime='text/csv')
        st.markdown("""
            <style>
                .stTabs [data-baseweb="tab"] {
                    margin-top: -0.9rem;
                    margin-right: 10rem; /* Adjust the value to increase or decrease space between tabs */
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
        tab1, tab2 = st.tabs(["Customer List by District and Head Office", "Customer List by Branch"])
        with tab1:
            if (combined_cust_by_crm is not None and not combined_cust_by_crm.empty) or  (crm_cust_only is not None and not crm_cust_only.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered Customer** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if combined_cust_by_crm is not None and not combined_cust_by_crm.empty:
                    st.write(combined_cust_by_crm.drop(columns=['wpc_id', 'crm_id']).reset_index(drop=True).rename(lambda x: x + 1))
                    # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                    # csv = df.to_csv(index=False)
                    # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
                else:
                    st.info("There are no registered Kiyya customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered Customer but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if crm_cust_only is not None and not crm_cust_only.empty:
                    st.info("NB: This customer is not countable as Kiyya customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(crm_cust_only.drop(columns=['wpc_id', 'crm_id']).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("You have no registered   today.")
            else:
                st.info("There is no registered customers yet.")
        with tab2:
            st.write(merged_df_2.drop(columns=['userId', 'userName', 'kiyya_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))



if __name__ == "__main__":
    main()
