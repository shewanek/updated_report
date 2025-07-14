import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import home_sidebar
import pandas as pd
from dependence import load_all_women_data, load_all_kiyya_data
from dependence import update_activity, check_session_timeout

# Check timeout on every interaction
check_session_timeout()


def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
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

    st.balloons()

    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    username = st.session_state.get("username", "")
    try:
        
        combined_cust_by_crm, crm_cust_only = load_all_women_data(username)
        
        merged_df_1, merged_df_2 = load_all_kiyya_data(username)

        # Combine unique values for filters
        combined_subprocess = sorted(set(combined_cust_by_crm["Sub Process"].dropna().unique()) | set(crm_cust_only["Sub Process"].dropna().unique()) | set(merged_df_1["Sub Process"].dropna().unique()) | set(merged_df_2["Sub Process"].dropna().unique()))
        combined_recruiter = sorted(set(combined_cust_by_crm["Recruited by"].dropna().unique()) | set(crm_cust_only["Recruited by"].dropna().unique()) | set(merged_df_1["Recruited by"].dropna().unique()) | set(merged_df_2["Recruited by"].dropna().unique()))


        # crm_cust_only['wpc_id'].nunique()

        start_dates = []
        end_dates = []


        if combined_cust_by_crm is not None and not combined_cust_by_crm.empty:
            start_dates.append(combined_cust_by_crm["Disbursed Date"].min())
            end_dates.append(combined_cust_by_crm["Disbursed Date"].max())

        if crm_cust_only is not None and not crm_cust_only.empty:
            start_dates.append(crm_cust_only["registered_date"].min())
            end_dates.append(crm_cust_only["registered_date"].max())

        if merged_df_1 is not None and not merged_df_1.empty:
            start_dates.append(merged_df_1["Disbursed Date"].min())
            end_dates.append(merged_df_1["Disbursed Date"].max())

        if merged_df_2 is not None and not merged_df_2.empty:
            # Convert "Register Date" to datetime and handle NaT values
            merged_df_2["Register Date"] = pd.to_datetime(merged_df_2["Register Date"], errors='coerce', unit='s')
            merged_df_2["Register Date"] = merged_df_2["Register Date"].dt.date

            # Filter out NaT values
            valid_dates = merged_df_2["Register Date"].dropna()
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
       
       
       

        # back_image = Image.open('pages/kiyya.jpg')
        st.sidebar.image('pages/kiyya.jpg')
        
        full_name = st.session_state.get("full_name", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

        sub_process = st.sidebar.multiselect("Select Sub Process", options=combined_subprocess)
        
        # Filter branches based on selected districts
        if sub_process:
            # st.session_state.district=district
            filtered_by = sorted(set(combined_cust_by_crm[combined_cust_by_crm["Sub Process"].isin(sub_process)]["Recruited by"].dropna().unique()) |
                                       set(crm_cust_only[crm_cust_only["Sub Process"].isin(sub_process)]["Recruited by"].dropna().unique()) |
                                       set(merged_df_1[merged_df_1["Sub Process"].isin(sub_process)]["Recruited by"].dropna().unique()) |
                                       set(merged_df_2[merged_df_2["Sub Process"].isin(sub_process)]["Recruited by"].dropna().unique()))
                                       
        else: 
        
            filtered_by = combined_recruiter

        Recruiter = st.sidebar.multiselect("Select Recruiter", options=filtered_by)
        

        col1, col2 = st.sidebar.columns(2)
        with col1:
            date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        with col2:
            date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)

        # Apply filters to each DataFrame
        if sub_process:
            combined_cust_by_crm = combined_cust_by_crm[combined_cust_by_crm["Sub Process"].isin(sub_process)]
            crm_cust_only = crm_cust_only[crm_cust_only["Sub Process"].isin(sub_process)]
            merged_df_1 = merged_df_1[merged_df_1["Sub Process"].isin(sub_process)]
            merged_df_2 = merged_df_2[merged_df_2["Sub Process"].isin(sub_process)]
            
        
        if Recruiter:
            combined_cust_by_crm = combined_cust_by_crm[combined_cust_by_crm["Recruited by"].isin(Recruiter)]
            crm_cust_only = crm_cust_only[crm_cust_only["Recruited by"].isin(Recruiter)]
            merged_df_1 = merged_df_1[merged_df_1["Recruited by"].isin(Recruiter)]
            merged_df_2 = merged_df_2[merged_df_2["Recruited by"].isin(Recruiter)]
            



        date1 = pd.Timestamp(date1)
        date2 = pd.Timestamp(date2)

        # Ensure both sides of the comparison are dates
        combined_cust_by_crm["Disbursed Date"] = pd.to_datetime(combined_cust_by_crm["Disbursed Date"]).dt.date
        combined_cust_by_crm = combined_cust_by_crm[(combined_cust_by_crm["Disbursed Date"] >= date1.date()) & (combined_cust_by_crm["Disbursed Date"] <= date2.date())]

        crm_cust_only["registered_date"] = pd.to_datetime(crm_cust_only["registered_date"]).dt.date
        crm_cust_only = crm_cust_only[(crm_cust_only["registered_date"] >= date1.date()) & (crm_cust_only["registered_date"] <= date2.date())]

        merged_df_1["Disbursed Date"] = pd.to_datetime(merged_df_1["Disbursed Date"]).dt.date
        merged_df_1 = merged_df_1[(merged_df_1["Disbursed Date"] >= date1.date()) & (merged_df_1["Disbursed Date"] <= date2.date())]

        # Filter merged_df_2 based on date range
        # merged_df_2 = merged_df_2[(merged_df_2["Register Date"] >= date1_datetime64) & (merged_df_2["Register Date"] <= date2_datetime64)]
        merged_df_2["Register Date"] = pd.to_datetime(merged_df_2["Register Date"]).dt.date
        merged_df_2 = merged_df_2[(merged_df_2["Register Date"] >= date1.date()) & (merged_df_2["Register Date"] <= date2.date())]
        


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
         

        

        # Calculate the total number of registered customers
        total_registered = combined_cust_by_crm['wpc_id'].nunique()
        total_by_branch = merged_df_1['kiyya_id'].nunique()
        total_correct = total_registered + total_by_branch

        total_notcounted = crm_cust_only['wpc_id'].nunique()
        total_not_counted_bybr = merged_df_2['kiyya_id'].nunique()
        total_not_counted = total_notcounted + total_not_counted_bybr

        
        # tab11, tab12 = st.tabs(["Aggregate Report", "Report per Recruiter"])
        # with tab12:
        col1, col2, col3 = st.columns(3)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Formal Customer**", value=total_registered, delta="Already Disburesed for")
        # Use st.markdown to add custom styling for the delta text
        col2.metric(label="**Total Infromal Customer**", value=total_by_branch, delta="Already Disburesed for")
        col3.metric(label="**Total  Infromal + Formal Customer**", value=total_not_counted, delta="Not yet Disburesed")
        # col4.metric(label="**Total Active**", value=df_combine_active.cust_id.nunique(), delta="Customer")
        # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
        # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
        style_metric_cards(background_color="#e38524", border_left_color="#00adef", border_color="#1f66bd", box_shadow="#f71938")

        combined_cust_by_crm = combined_cust_by_crm.drop_duplicates(subset=['Saving Account'], keep='first')
        merged_df_1 = merged_df_1.drop_duplicates(subset=['Saving Account'], keep='first')
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
        tab1, tab2 = st.tabs(["Kiyya Formal Customer List", "Kiyya Informal Customer List"])
        with tab1:
            if (combined_cust_by_crm is not None and not combined_cust_by_crm.empty) or  (crm_cust_only is not None and not crm_cust_only.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered Customer** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if combined_cust_by_crm is not None and not combined_cust_by_crm.empty:
                    st.write(combined_cust_by_crm.drop(columns=['wpc_id', 'crm_id']).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1))
                    # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                    # csv = df.to_csv(index=False)
                    # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
                else:
                    st.info("There are no registered Kiyya Formal customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered Customer but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if crm_cust_only is not None and not crm_cust_only.empty:
                    st.info("NB: This customer is not countable as Kiyya Formal customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(crm_cust_only.drop(columns=['wpc_id', 'crm_id']).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("You have no registered   today.")
            else:
                st.info("There is no registered customers yet.")
        with tab2:
            # st.write(merged_df_2.drop(columns=['userId', 'userName', 'kiyya_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
            if (merged_df_1 is not None and not merged_df_1.empty) or  (merged_df_2 is not None and not merged_df_2.empty):
                st.markdown(f'<span style="color: #e38524;">**Registered Customer** (<span style="color: #00adef;">whose loan has already been disbursed </span>)</span> 👇🏻', unsafe_allow_html=True)
                if merged_df_1 is not None and not merged_df_1.empty:
                    st.write(merged_df_1.drop(columns=['userId', 'kiyya_id',]).drop_duplicates().reset_index(drop=True).rename(lambda x: x + 1))
                    # df = unique_customer.drop(columns=['uniqueId', 'userName'])
                    # csv = df.to_csv(index=False)
                    # st.download_button(label=":blue[Download CSV]", data=csv, file_name='unique_data.csv', mime='text/csv')
                else:
                    st.info("There are no registered Kiyya Informal customers whose loan have already been disbursed.")

                st.markdown('<span style="color: #e38524;">**Registered Customer but not yet disbursed.(<span style="color: #00adef;">Live</span>)**</span> 👇🏻', unsafe_allow_html=True)
                if merged_df_2 is not None and not merged_df_2.empty:
                    st.info("NB: This customer is not countable as Kiyya Informal customer until the disbursement is confirmed. Again, it is important to note that if the registered customer account number is incorrect, it is not countable for the registered user.")
                    st.write(merged_df_2.drop(columns=['userId', 'kiyya_id', ]).reset_index(drop=True).rename(lambda x: x + 1))
                else:
                    st.info("You have no registered   today.")
            else:
                st.info("There is no registered customers yet.")
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
