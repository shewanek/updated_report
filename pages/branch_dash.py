import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import make_sidebar1
from dependence import load_branchdata, load_branch_kiyya_data

from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()



def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Portal", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    # CSS to hide the header
    hide_header_style = """
        <style>
        .app-header {display: none;}
        </style>
        """
    st.markdown(hide_header_style, unsafe_allow_html=True)
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
        }
        .stAppHeader { visibility: hidden; }
        /* Hide the entire header bar */
        header.stAppHeader {
            display: none;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    customm = """
        <style>
            .app-header {
                display: none;
            }
        </style>
        """

    # Apply the custom CSS
    st.markdown(customm, unsafe_allow_html=True)
    update_activity()

    # Auto-refresh interval (in seconds)
    refresh_interval = 6600  # Adjust as needed (e.g., 10 minutes for real-time)
    st_autorefresh(interval=refresh_interval * 1000, key="Michu Bot dash")

    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/michu.png')
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

    # st.balloons()

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
        
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    try:
        
        unique_cust_by_branch, unique_cust_by_self, registed_by_branch, unique_customer = load_branchdata(username)
        k_unique_cust_by_branch, k_unique_cust_by_self, k_registed_by_branch, k_unique_customer = load_branch_kiyya_data(username)

        # df_combine_closed, df_combine_active, df_combine_arrears = load_customer_detail(role, username)
        # st.write(k_unique_cust_by_branch)
        # conversion_customer
        # Sidebar
        st.sidebar.image("pages/michu.png")
        # username = st.session_state.get("username", "")
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

            

        if k_unique_customer is not None and not k_unique_customer.empty:
            start_dates.append(k_unique_customer["Disbursed Date"].min())
            end_dates.append(k_unique_customer["Disbursed Date"].max())

        if k_unique_cust_by_branch is not None and not k_unique_cust_by_branch.empty:
            start_dates.append(k_unique_cust_by_branch["Disbursed_Date"].min())
            end_dates.append(k_unique_cust_by_branch["Disbursed_Date"].max())

        if k_unique_cust_by_self is not None and not k_unique_cust_by_self.empty:
            start_dates.append(k_unique_cust_by_self["Disbursed Date"].min())
            end_dates.append(k_unique_cust_by_self["Disbursed Date"].max())
        
        if k_registed_by_branch is not None and not k_registed_by_branch.empty:
            start_dates.append(k_registed_by_branch["Disbursed_Date"].min())
            end_dates.append(k_registed_by_branch["Disbursed_Date"].max())

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


        k_unique_customer = k_unique_customer[(k_unique_customer["Disbursed Date"] >= date1) & (k_unique_customer["Disbursed Date"] <= date2)]
        k_unique_cust_by_branch = k_unique_cust_by_branch[(k_unique_cust_by_branch["Disbursed_Date"] >= date1) & (k_unique_cust_by_branch["Disbursed_Date"] <= date2)]
        k_unique_cust_by_self = k_unique_cust_by_self[(k_unique_cust_by_self["Disbursed Date"] >= date1) & (k_unique_cust_by_self["Disbursed Date"] <= date2)]
        k_registed_by_branch = k_registed_by_branch[(k_registed_by_branch["Disbursed_Date"] >= date1) & (k_registed_by_branch["Disbursed_Date"] <= date2)]

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
        total = unique_customer.uniqueId.nunique() + k_unique_customer.uniqueId.nunique()

        col1, col2, col3 = st.columns(3)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Unique Customer**", value=total, delta="Customer")
        col2.metric(label="**Total Michu Unique Customer(Wabi & Guya)**", value=unique_customer.uniqueId.nunique(), delta="Customer")
        col3.metric(label="**Total Kiyya Unique Customer(Formal & Informal)**", value=k_unique_customer.uniqueId.nunique(), delta="Customer")
        # col3.metric(label="**Total Closed**", value=df_combine_closed.cust_id.nunique(), delta="Customer")
        # col4.metric(label="**Total Active**", value=df_combine_active.cust_id.nunique(), delta="Customer")
        # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
        # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

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
        tab1, tab2= st.tabs(["Michu(Wabi & Guya)", "Michu Kiyya(Informal & Formal)"])
        with tab1:
            # Display unique data in a table  
            st.markdown('<span style="color: #e38524;">**Registered by Branch** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            # st.write(df_unique.drop(columns=['uniqueId', 'userName', 'Upload Date']).reset_index(drop=True).rename(lambda x: x + 1))
            if unique_cust_by_branch is not None and not unique_cust_by_branch.empty:
                st.write(unique_cust_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
                # df = df_unique.drop(columns=['uniqueId', 'userName'])
                # csv = df.to_csv(index=False)
                # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
            else:
                st.info("There are no customers registered by your distirct.")

            st.markdown('<span style="color: #e38524;">**Self Registered** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            if unique_cust_by_self is not None and not unique_cust_by_self.empty:
                st.write(unique_cust_by_self.reset_index(drop=True).rename(lambda x: x + 1))

                # st.markdown('<span style="color: #e38524;">**Today Registered By Branch (Live)**</span> 👇🏻', unsafe_allow_html=True)
            else:
                st.info("There are no self-registered customers at your district.")

            st.markdown('<span style="color: #e38524;">**Registered by the branch, but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
            if registed_by_branch is not None and not registed_by_branch.empty:
                st.info("NB: This customer is not countable as unique until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered branch, but rather for where the account is open.")
                st.write(registed_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
            else:
                st.info("There are no registered customers at your district today.")

        with tab2:
            # Display unique data in a table  
            st.markdown('<span style="color: #e38524;">**Registered by Branch** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            # st.write(df_unique.drop(columns=['uniqueId', 'userName', 'Upload Date']).reset_index(drop=True).rename(lambda x: x + 1))
            if k_unique_cust_by_branch is not None and not k_unique_cust_by_branch.empty:
                st.write(k_unique_cust_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
                # df = df_unique.drop(columns=['uniqueId', 'userName'])
                # csv = df.to_csv(index=False)
                # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
            else:
                st.info("There are no customers registered by your distirct.")

            st.markdown('<span style="color: #e38524;">**Self Registered** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
            if k_unique_cust_by_self is not None and not k_unique_cust_by_self.empty:
                st.write(k_unique_cust_by_self.reset_index(drop=True).rename(lambda x: x + 1))

                # st.markdown('<span style="color: #e38524;">**Today Registered By Branch (Live)**</span> 👇🏻', unsafe_allow_html=True)
            else:
                st.info("There are no self-registered customers at your district.")

            st.markdown('<span style="color: #e38524;">**Registered by the branch, but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
            if k_registed_by_branch is not None and not k_registed_by_branch.empty:
                st.info("NB: This customer is not countable as unique until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered branch, but rather for where the account is open.")
                st.write(k_registed_by_branch.reset_index(drop=True).rename(lambda x: x + 1))
            else:
                st.info("There are no registered customers at your district today.")
        
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

