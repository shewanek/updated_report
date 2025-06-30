import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import home_sidebar
from dependence import load_unquiecustomer, load_unquiekiyya

from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()


def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
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
    st.markdown(custom_cs, unsafe_allow_html=True)
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    update_activity()
    customm = """
        <style>
            .app-header {
                display: none;
            }
        </style>
        """

    # Apply the custom CSS
    st.markdown(customm, unsafe_allow_html=True)

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
        <center> <h3 class = "title_dash"> Michu Unique Customers Detail Report (<span style="color: #00adef; font-size: 20px;">Year-To-Date</span>)</h3> </center>
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
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    try:
        
        unique_customer, unique_by_self, registed_by_branch, df_unique_all = load_unquiecustomer(role, username)
        k_unique_customer, k_unique_by_self, k_registed_by_branch, k_df_unique_all = load_unquiekiyya(role, username)
        # st.write(unique_customer)
        # Combine unique values for filters
        combined_districts = sorted(set(df_unique_all["District"].dropna().unique()) | set(unique_customer["District"].dropna().unique()) | set(unique_by_self["District"].dropna().unique()) | set(registed_by_branch["District"].dropna().unique()) | set(k_df_unique_all["District"].dropna().unique()) | set(k_unique_customer["District"].dropna().unique()) | set(k_unique_by_self["District"].dropna().unique()) | set(k_registed_by_branch["District"].dropna().unique()))
        combined_branches = sorted(set(df_unique_all["Branch"].dropna().unique()) | set(unique_customer["Branch"].dropna().unique()) | set(unique_by_self["Branch"].dropna().unique()) | set(registed_by_branch["Branch"].dropna().unique()) | set(k_df_unique_all["Branch"].dropna().unique()) | set(k_unique_customer["Branch"].dropna().unique()) | set(k_unique_by_self["Branch"].dropna().unique()) | set(k_registed_by_branch["Branch"].dropna().unique()))

        start_dates = []
        end_dates = []


        if df_unique_all is not None and not df_unique_all.empty:
            start_dates.append(df_unique_all["Disbursed Date"].min())
            end_dates.append(df_unique_all["Disbursed Date"].max())

        if unique_customer is not None and not unique_customer.empty:
            start_dates.append(unique_customer["Disbursed_Date"].min())
            end_dates.append(unique_customer["Disbursed_Date"].max())

        if unique_by_self is not None and not unique_by_self.empty:
            start_dates.append(unique_by_self["Disbursed Date"].min())
            end_dates.append(unique_by_self["Disbursed Date"].max())
        
        if registed_by_branch is not None and not registed_by_branch.empty:
            start_dates.append(registed_by_branch["Disbursed_Date"].min())
            end_dates.append(registed_by_branch["Disbursed_Date"].max())



        if k_df_unique_all is not None and not k_df_unique_all.empty:
            start_dates.append(k_df_unique_all["Disbursed Date"].min())
            end_dates.append(k_df_unique_all["Disbursed Date"].max())

        if k_unique_customer is not None and not k_unique_customer.empty:
            start_dates.append(k_unique_customer["Disbursed_Date"].min())
            end_dates.append(k_unique_customer["Disbursed_Date"].max())

        if k_unique_by_self is not None and not k_unique_by_self.empty:
            start_dates.append(k_unique_by_self["Disbursed Date"].min())
            end_dates.append(k_unique_by_self["Disbursed Date"].max())
        
        if k_registed_by_branch is not None and not k_registed_by_branch.empty:
            start_dates.append(k_registed_by_branch["Disbursed_Date"].min())
            end_dates.append(k_registed_by_branch["Disbursed_Date"].max())

        if start_dates and end_dates:
            combined_start_date = min(start_dates)
            combined_end_date = max(end_dates)
        else:
            combined_start_date = None
            combined_end_date = None
       
       
       

        # Sidebar filters
        st.sidebar.image("pages/michu.png")
        full_name = st.session_state.get("full_name", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
        st.sidebar.header("Please filter")

        district = st.sidebar.multiselect("Select District", options=combined_districts)
        
        # Filter branches based on selected districts
        if district:
            filtered_branches = sorted(set(df_unique_all[df_unique_all["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(unique_customer[unique_customer["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(unique_by_self[unique_by_self["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(registed_by_branch[registed_by_branch["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(k_df_unique_all[k_df_unique_all["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(k_unique_customer[k_unique_customer["District"].isin(district)]["Branch"].dropna().unique()) |
                                       set(k_unique_by_self[k_unique_by_self["District"].isin(district)]["Branch"].dropna().unique())|
                                       set(k_registed_by_branch[k_registed_by_branch["District"].isin(district)]["Branch"].dropna().unique()))
        else:
            filtered_branches = combined_branches

        branch = st.sidebar.multiselect("Select Branch", options=filtered_branches)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        with col2:
            date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)


        # Apply filters to each DataFrame
        if district:
            df_unique_all = df_unique_all[df_unique_all["District"].isin(district)]
            unique_customer = unique_customer[unique_customer["District"].isin(district)]
            unique_by_self = unique_by_self[unique_by_self["District"].isin(district)]
            registed_by_branch = registed_by_branch[registed_by_branch["District"].isin(district)]
            k_df_unique_all = k_df_unique_all[k_df_unique_all["District"].isin(district)]
            k_unique_customer = k_unique_customer[k_unique_customer["District"].isin(district)]
            k_unique_by_self = k_unique_by_self[k_unique_by_self["District"].isin(district)]
            k_registed_by_branch = k_registed_by_branch[k_registed_by_branch["District"].isin(district)]
        
        if branch:
            df_unique_all = df_unique_all[df_unique_all["Branch"].isin(branch)]
            unique_customer = unique_customer[unique_customer["Branch"].isin(branch)]
            unique_by_self = unique_by_self[unique_by_self["Branch"].isin(branch)]
            registed_by_branch = registed_by_branch[registed_by_branch["Branch"].isin(branch)]
            k_df_unique_all = k_df_unique_all[k_df_unique_all["Branch"].isin(branch)]
            k_unique_customer = k_unique_customer[k_unique_customer["Branch"].isin(branch)]
            k_unique_by_self = k_unique_by_self[k_unique_by_self["Branch"].isin(branch)]
            k_registed_by_branch = k_registed_by_branch[k_registed_by_branch["Branch"].isin(branch)]


        df_unique_all = df_unique_all[(df_unique_all["Disbursed Date"] >= date1) & (df_unique_all["Disbursed Date"] <= date2)]
        unique_customer = unique_customer[(unique_customer["Disbursed_Date"] >= date1) & (unique_customer["Disbursed_Date"] <= date2)]
        unique_by_self = unique_by_self[(unique_by_self["Disbursed Date"] >= date1) & (unique_by_self["Disbursed Date"] <= date2)]
        registed_by_branch = registed_by_branch[(registed_by_branch["Disbursed_Date"] >= date1) & (registed_by_branch["Disbursed_Date"] <= date2)]

        k_df_unique_all = k_df_unique_all[(k_df_unique_all["Disbursed Date"] >= date1) & (k_df_unique_all["Disbursed Date"] <= date2)]
        k_unique_customer = k_unique_customer[(k_unique_customer["Disbursed_Date"] >= date1) & (k_unique_customer["Disbursed_Date"] <= date2)]
        k_unique_by_self = k_unique_by_self[(k_unique_by_self["Disbursed Date"] >= date1) & (k_unique_by_self["Disbursed Date"] <= date2)]
        k_registed_by_branch = k_registed_by_branch[(k_registed_by_branch["Disbursed_Date"] >= date1) & (k_registed_by_branch["Disbursed_Date"] <= date2)]


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
        total = df_unique_all['uniqueId'].nunique() + k_df_unique_all['uniqueId'].nunique()
        col1, col2, col3 = st.columns(3)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Unique Customer**", value=total, delta="Customer")
        col2.metric(label="**Total Michu Unique Customer(Wabi & Guya)**", value=df_unique_all['uniqueId'].nunique(), delta="Customer")
        col3.metric(label="**Total Kiyya Unique Customer(Formal & Informal)**", value=k_df_unique_all['uniqueId'].nunique(), delta="Customer")
        # col3.metric(label="**Total Closed**", value=df_combine_closed.cust_id.nunique(), delta="Customer")
        # col4.metric(label="**Total Active**", value=df_combine_active.cust_id.nunique(), delta="Customer")
        # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
        # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
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
        tab1, tab2= st.tabs(["Michu(Wabi & Guya)", "Michu Kiyya(Informal & Formal)"])
        with tab1:
            # Display unique data in a table  
            st.markdown('<span style="color: #e38524;">**Registered by Branch** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            # st.write(df_unique.drop(columns=['uniqueId', 'userName', 'Upload Date']).reset_index(drop=True).rename(lambda x: x + 1))
            st.write(unique_customer.reset_index(drop=True).rename(lambda x: x + 1))
            # df = df_unique.drop(columns=['uniqueId', 'userName'])
            # csv = df.to_csv(index=False)
            # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')

            st.markdown('<span style="color: #e38524;">**Self Registered** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            st.write(unique_by_self.reset_index(drop=True).rename(lambda x: x + 1))

            # st.markdown('<span style="color: #e38524;">**Today Registered By Branch (Live)**</span> 👇🏻', unsafe_allow_html=True)

            st.markdown('<span style="color: #e38524;">**Registered by the branch, but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
            st.info("NB: This customer is not countable as unique until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered branch, but rather for where the account is open.")
            st.write(registed_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
        
    

        with tab2:
            # Display unique data in a table  
            st.markdown('<span style="color: #e38524;">**Registered by Branch** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            # st.write(df_unique.drop(columns=['uniqueId', 'userName', 'Upload Date']).reset_index(drop=True).rename(lambda x: x + 1))
            st.write(k_unique_customer.reset_index(drop=True).rename(lambda x: x + 1))
            # df = df_unique.drop(columns=['uniqueId', 'userName'])
            # csv = df.to_csv(index=False)
            # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')

            st.markdown('<span style="color: #e38524;">**Self Registered** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            st.write(k_unique_by_self.reset_index(drop=True).rename(lambda x: x + 1))

            # st.markdown('<span style="color: #e38524;">**Today Registered By Branch (Live)**</span> 👇🏻', unsafe_allow_html=True)

            st.markdown('<span style="color: #e38524;">**Registered by the branch, but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
            st.info("NB: This customer is not countable as unique until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered branch, but rather for where the account is open.")
            st.write(k_registed_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
        # df_conversion
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
    
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
    
if __name__ == "__main__":
    main()
