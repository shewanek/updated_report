import streamlit as st
from streamlit_autorefresh import st_autorefresh
# from PIL import Image
from streamlit_extras.metric_cards import style_metric_cards
from dependence import load_kiyya_report_data
from dependence import update_activity, check_session_timeout


# Check timeout on every interaction
check_session_timeout()


def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_cs, unsafe_allow_html=True)
    update_activity()


    # Auto-refresh interval (in seconds)
    refresh_interval = 600  # 5 minutes
    st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")

    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/michu.png')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h4 class = "title_dash"> Michu Kiyya Customers Detail Report </h4> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)


    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    try:
        kiyya_customer, kiyya_customer_today, formal_customer, formal_customer_today = load_kiyya_report_data()



        # back_image = Image.open('pages/kiyya.jpg')
        st.sidebar.image('pages/kiyya.jpg')
        # username = st.session_state.get("username", "")
        # full_name = st.session_state.get("full_name", "")
        # # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        # st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
        

        # col1, col2 = st.sidebar.columns(2)
        # with col1:
        #     date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        # with col2:
        #     date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)


        # combined_cust_by_crm = combined_cust_by_crm[(combined_cust_by_crm["Disbursed Date"] >= date1) & (combined_cust_by_crm["Disbursed Date"] <= date2)]
        # crm_cust_only = crm_cust_only[(crm_cust_only["registered_date"] >= date1) & (crm_cust_only["registered_date"] <= date2)]
        
        # home_sidebar()

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
         
        st.markdown('<h5><span style="color: #e38524;">Infromal Registered Customer </span> 👇🏻</h5>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Informal Rigistered Customer**", value=kiyya_customer, delta="Customer")
        col2.metric(label="**Total Informal Rigister Customer of Today**", value=kiyya_customer_today, delta="Today Customer")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

        st.markdown('<h5><span style="color: #e38524;">Formal Registered Customer  </span> 👇🏻</h5>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col3.metric(label="**Total Formal Rigister Customer**", value=formal_customer, delta="Customer")
        col4.metric(label="**Total Formal Rigister Customer of Today**", value=formal_customer_today, delta="Today Customer")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
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
        # st.write("Wait till ")
        
        # if merged_df is not None and not merged_df.empty:
        #     st.markdown(f'<span style="color: #e38524;">**Registered Customer**👇🏻', unsafe_allow_html=True)
        #     st.write(merged_df.drop(columns=['kiyya_id', 'userId']).reset_index(drop=True).rename(lambda x: x + 1))
        #     # df = unique_customer.drop(columns=['uniqueId', 'userName'])
        #     # csv = df.to_csv(index=False)
        #     # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
        # else:
        #     st.info("There is no registered customers yet.")
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")



if __name__ == "__main__":
    
    main()

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
