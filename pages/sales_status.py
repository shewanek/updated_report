import streamlit as st
# from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import home_sidebar
import plotly.graph_objects as go
import pandas as pd
from dependence import load_sales_detail, update_rejected_customers
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()
pd.set_option('future.no_silent_downcasting', True)


def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
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
        <center> <h3 class = "title_dash"> Michu Retention Detail Report </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    # st.balloons()

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
        
        # # tab_options = ["Wabbi & Kiyya-Formal", "Guyya & Kiyya-Informal"]
        # # active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
        # # if active_tab == "Wabbi & Kiyya-Formal":
        # # unique_customer, unique_by_self, registed_by_branch, df_unique_all = load_unquiecustomer(role, username)
        if role == 'Admin' or role == 'under_admin':
            df_combine_prospect, df_combine_rejected, df_merged_closed, df_merged_emegancce, df_merged_marchent = load_sales_detail(role, username)
        else:
            df_combine_prospect, df_combine_rejected, df_merged_closed = load_sales_detail(role, username)
        # st.write(df_combine_collection)
        # df_combine_arrears['Michu Loan Product'] = df_combine_arrears['Michu Loan Product'].replace({'Michu 1.0': 'Wabbi'})


        # # Combine unique values for filters
        # combined_districts = sorted(set(df_combine_collection["District"].dropna().unique()) | set(df_combine_conversion["District"].dropna().unique()) | set(df_combine_arrears["District"].dropna().unique()))
        # combined_branches = sorted(set(df_combine_collection["Branch"].dropna().unique()) | set(df_combine_conversion["Branch"].dropna().unique()) | set(df_combine_arrears["Branch"].dropna().unique()))

        # start_dates = []
        # end_dates = []



        # if df_combine_conversion is not None and not df_combine_conversion.empty:
        #     start_dates.append(df_combine_conversion["Conversion Date"].min())
        #     end_dates.append(df_combine_conversion["Conversion Date"].max())
        
        # # if df_combine_arrears is not None and not df_combine_arrears.empty:
        # #     start_dates.append(df_combine_arrears["Maturity Date"].min())
        # #     end_dates.append(df_combine_arrears["Maturity Date"].max())
        
        # if df_combine_collection is not None and not df_combine_collection.empty:
        #     start_dates.append(df_combine_collection["Collected Date"].min())
        #     end_dates.append(df_combine_collection["Collected Date"].max())

        # if start_dates and end_dates:
        #     combined_start_date = min(start_dates)
        #     combined_end_date = max(end_dates)
        # else:
        #     combined_start_date = None
        #     combined_end_date = None
    
    
    

        # # Sidebar filters
        # st.sidebar.image("pages/michu.png")
        # full_name = st.session_state.get("full_name", "")
        # # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        # st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
        # st.sidebar.header("Please filter")

        # district = st.sidebar.multiselect("Select District", options=combined_districts)
        
        # # Filter branches based on selected districts
        # if district:
        #     filtered_branches = sorted(set(df_combine_collection[df_combine_collection["District"].isin(district)]["Branch"].dropna().unique()) |
        #                             set(df_combine_conversion[df_combine_conversion["District"].isin(district)]["Branch"].dropna().unique()) |
        #                             set(df_combine_arrears[df_combine_arrears["District"].isin(district)]["Branch"].dropna().unique()))
        # else:
        #     filtered_branches = combined_branches

        # branch = st.sidebar.multiselect("Select Branch", options=filtered_branches)

        # col1, col2 = st.sidebar.columns(2)
        # with col1:
        #     date1 = st.date_input("Start Date", combined_start_date, min_value=combined_start_date, max_value=combined_end_date)
        # with col2:
        #     date2 = st.date_input("End Date", combined_end_date, min_value=combined_start_date, max_value=combined_end_date)


        # # Apply filters to each DataFrame
        # if district:
        #     df_combine_collection = df_combine_collection[df_combine_collection["District"].isin(district)]
        #     df_combine_conversion = df_combine_conversion[df_combine_conversion["District"].isin(district)]
        #     df_combine_arrears = df_combine_arrears[df_combine_arrears["District"].isin(district)]
        
        # if branch:
        #     df_combine_collection = df_combine_collection[df_combine_collection["Branch"].isin(branch)]
        #     df_combine_conversion = df_combine_conversion[df_combine_conversion["Branch"].isin(branch)]
        #     df_combine_arrears = df_combine_arrears[df_combine_arrears["Branch"].isin(branch)]


    
        # df_combine_collection = df_combine_collection[(df_combine_collection["Collected Date"] >= date1) & (df_combine_collection["Collected Date"] <= date2)]
        # df_combine_conversion = df_combine_conversion[(df_combine_conversion["Conversion Date"] >= date1) & (df_combine_conversion["Conversion Date"] <= date2)]
        # # df_combine_arrears = df_combine_arrears[(df_combine_arrears["Maturity Date"] >= date1) & (df_combine_arrears["Maturity Date"] <= date2)]
        # # st.write(df_combine_collection)


        # # Hide the sidebar by default with custom CSS
        # hide_sidebar_style = """
        #     <style>
        #         #MainMenu {visibility: hidden;}
        #     </style>
        # """
        # st.markdown(hide_sidebar_style, unsafe_allow_html=True)
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


        total_rejected = df_combine_rejected['michu_id'].nunique()
        total_rejected_contact = df_combine_rejected[df_combine_rejected['Customer_Feedback'].notna()]['michu_id'].nunique()
        Total_rejected_notactive = df_combine_rejected[df_combine_rejected['statuss'] != 'active']['michu_id'].nunique()
        total_rejected_active = df_combine_rejected[df_combine_rejected['statuss'] == 'active']['michu_id'].nunique()

        total_closed = df_merged_closed[df_merged_closed['statuss'] != 'active']['loan_id'].nunique()
        total_closed_active = df_merged_closed[df_merged_closed['statuss'] == 'active']['loan_id'].nunique()



        total_prospective = df_combine_prospect['customer_id_michu'].nunique()
        total_prospective_active = df_combine_prospect[df_combine_prospect['statuss'] == 'active']['customer_id_michu'].nunique()
        if role == 'Admin' or role == 'under_admin':
            total_emrgance = df_merged_emegancce['em_id'].nunique()
            total_emrgance_active = df_merged_emegancce[df_merged_emegancce['statuss'] == 'active']['em_id'].nunique()
            total_marchent = df_merged_marchent['me_id'].nunique()
            total_marchent_active = df_merged_marchent[df_merged_marchent['statuss'] == 'active']['me_id'].nunique()



        if role == 'Admin' or role == 'under_admin':
            Total = Total_rejected_notactive + total_closed + total_prospective + total_emrgance + total_marchent
            total_active = total_rejected_active + total_closed_active + total_prospective_active + total_emrgance_active + total_marchent_active
        else:
            Total = Total_rejected_notactive + total_closed + total_prospective
            total_active = total_rejected_active + total_closed_active + total_prospective_active



        # amount_actual = float(df_combine_rejected['Principal Collected'].sum())
        amount_target = 0
        # Function to create a gauge chart
        def create_conversion_gauge(value, target, title, thresholds=None, colors=None):
            """
            Create a target gauge with custom thresholds and colors.
            
            Parameters:
                value (float): The current value to display on the gauge.
                target (float): The target value to measure performance.
                title (str): Title of the gauge.
                thresholds (list, optional): Threshold values for different gauge sections. Default is [0.5, 0.8, 1.2].
                colors (list, optional): Colors for each threshold section. Default is ["red", "yellow", "green"].
                
            Returns:
                plotly.graph_objects.Figure: The gauge chart.
            """
            if thresholds is None:
                thresholds = [0.5, 0.7, 1.2]  # Default thresholds: 50%, 80%, and 120% of the target
            if colors is None:
                colors = ["red", "yellow", "green"]  # Default colors: red, yellow, green
            
            max_value = target * thresholds[-1]  # Maximum value for the gauge
            steps = [
                {"range": [0, target * thresholds[0]], "color": colors[0]},  # Below 50% - Red
                {"range": [target * thresholds[0], target * thresholds[1]], "color": colors[1]},  # 50%-80% - Yellow
                {"range": [target * thresholds[1], max_value], "color": colors[2]},  # Above 80% - Green
            ]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                delta={'reference': target, 'position': "top"},
                gauge={
                    "axis": {"range": [0, max_value]},
                    "bar": {"color": "#00adef"},  # Needle color
                    "steps": steps
                },
                title={"text": title}
            ))
            fig.update_layout(height=250, margin=dict(t=30, b=30, l=0, r=0))
            return fig

        def create_amount_gauge(value, target, title, thresholds=None, colors=None):
            """
            Create a target gauge with custom thresholds and colors.
            
            Parameters:
                value (float): The current value to display on the gauge.
                target (float): The target value to measure performance.
                title (str): Title of the gauge.
                thresholds (list, optional): Threshold values for different gauge sections. Default is [0.5, 0.8, 1.2].
                colors (list, optional): Colors for each threshold section. Default is ["red", "yellow", "green"].
                
            Returns:
                plotly.graph_objects.Figure: The gauge chart.
            """
            if thresholds is None:
                thresholds = [0.5, 0.7, 1.2]  # Default thresholds: 50%, 80%, and 120% of the target
            if colors is None:
                colors = ["red", "yellow", "green"]  # Default colors: red, yellow, green
            
            max_value = target * thresholds[-1]  # Maximum value for the gauge
            steps = [
                {"range": [0, target * thresholds[0]], "color": colors[0]},  # Below 50% - Red
                {"range": [target * thresholds[0], target * thresholds[1]], "color": colors[1]},  # 50%-80% - Yellow
                {"range": [target * thresholds[1], max_value], "color": colors[2]},  # Above 80% - Green
            ]
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                delta={'reference': target, 'position': "top"},
                gauge={
                    "axis": {"range": [0, max_value]},
                    "bar": {"color": "#00adef"},  # Needle color
                    "steps": steps
                },
                title={"text": title}
            ))
            fig.update_layout(height=250, margin=dict(t=30, b=30, l=0, r=0))
            return fig

    
        
        # col2, col3, col4, col5 = st.columns(4)
        # # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        # col2.metric(label="**Total Rejected**", value=total_collected)
        # col3.metric(label="**Total Closed**", value=total_collected)
        # col4.metric(label="**Total Prospective**", value=total_rejected)
        # col5.metric(label="**Total emrgance**", value=total_collectedd)
        # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
        # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
        # style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

            
        # Usage in Streamlit
        if role == "Admin" or role == 'under_admin' or role == 'Sales Admin':
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_conversion_gauge(value=total_rejected_contact, target=total_rejected, title="Total Contacted", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                    ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(create_amount_gauge(value=total_active, target=Total, title="Total Active", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                    ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                    use_container_width=True
                )

            coll1, coll2 = st.columns(2)  
        if role == "District User" or role == 'Branch User':
            st.plotly_chart(create_amount_gauge(value=total_active, target=Total, title="Total Active", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                use_container_width=True
            )
            # with coll1:
                # -- Per District --
                # Drop duplicates to ensure unique District entries for summarization
                # st.write(df_combine_rejected)
                
        
    
        # # Display combined data in a table
        # st.write(":orange[Michu Women Targeted Customer List 👇🏻]")
        # st.write(df_combine.drop(columns=['customerId', 'userName']).reset_index(drop=True).rename(lambda x: x + 1))
        # df = df_combine.drop(columns=['customerId', 'userName'])
        # csv = df.to_csv(index=False)
        # st.download_button(label=":blue[Download CSV]", data=csv, file_name='Women_Targeted_data.csv', mime='text/csv')
        col2, col3, col4, col5, col6 = st.columns(5)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col2.metric(label="**Active / Rejected**", value=f"{total_rejected_active}/{Total_rejected_notactive}")
        col3.metric(label="**Active / Closed**", value=f"{total_closed_active}/{total_closed}")
        col4.metric(label="**Active / Prospective**", value=f"{total_prospective_active}/{total_prospective}")
        if role == 'Admin' or role == 'under_admin':
            col5.metric(label="**Active / emrgance**", value=f"{total_emrgance_active}/{total_emrgance}")
            col6.metric(label="**Active / marchent**", value=f"{total_marchent_active}/{total_marchent}")
        # style_metric_cards(background_color="#000000", border_left_color="#e38524", border_color="#000000")
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
        tab2, tab3, tab4, tab5, tab6 = st.tabs(["Rejected Customer", "Closed Customer", "Prospect Customer", "Emrgance Customer", "Merchent Customer"])
        

        with tab2:
            tab21, tab22 = st.tabs(["Not Take Loan", "Take Loan"])
            with tab21:
                if role == 'Sales Admin':
                
    
                    # Define Editable Columns
                    editable_columns = ["Rejection_Reason_Remark", "Customer_Feedback"]

                    # Remove only non-display column(s) (keep 'michu_id' for backend)
                    display_df = df_combine_rejected[df_combine_rejected['statuss'] != 'active'].drop(columns=["branch_code"])

                    # Filter Widgets Title
                    st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)

                    # Filter Controls
                    col1, col2 = st.columns([2, 2])
                    with col1:
                        michu_loan_filter = st.selectbox("Filter: Michu Loan Product", ["All"] + list(display_df['michu_loan_product'].unique()))
                    with col2:
                        status_filter = st.selectbox("Filter: Status", ["All"] + list(display_df['statuss'].unique()))

                    # Apply Filters
                    if michu_loan_filter != "All":
                        display_df = display_df[display_df['michu_loan_product'] == michu_loan_filter]
                    if status_filter != "All":
                        display_df = display_df[display_df['statuss'] == status_filter]

                    # Create the version shown to users (hide michu_id)
                    display_ui = display_df.drop(columns=["michu_id"])

                    # Column Config
                    column_config = {
                        col: st.column_config.TextColumn(disabled=False) if col in editable_columns else st.column_config.TextColumn(disabled=True)
                        for col in display_ui.columns
                    }

                    # Show Editable Table
                    edited_df = st.data_editor(
                        display_ui,
                        key="my_key_rejecet",
                        column_config=column_config,
                        num_rows="fixed"
                    )

                    # Capture Edited Data
                    edited_data = st.session_state["my_key_rejecet"]["edited_rows"]

                    # Prepare Edits with michu_id
                    if edited_data:
                        result = {}
                        for row_index, edits in edited_data.items():
                            if not edits:
                                continue
                            michu_id = display_df.iloc[int(row_index)]["michu_id"]
                            result[row_index] = {"michu_id": michu_id, **edits}

                        # Update in DB
                        update_rejected_customers(result)


                else:
                    st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                    st.write(df_combine_rejected[df_combine_rejected['statuss'] != 'active'].drop(columns=['michu_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
        
            with tab22:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_rejected[df_combine_rejected['statuss'] == 'active'].drop(columns=['michu_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
        
        with tab3:
            tab31, tab32 = st.tabs(["Not Take Loan", "Take Loan"])
            with tab31:
                
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_merged_closed[df_merged_closed['statuss'] != 'active'].drop(columns=['loan_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
           
            with tab32:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_merged_closed[df_merged_closed['statuss'] == 'active'].drop(columns=['loan_id', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
           
        
        with tab4:
            tab41, tab42 = st.tabs(["Not Take Loan", "Take Loan"])
            with tab41:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_prospect[df_combine_prospect['statuss'] != 'active'].drop(columns=['customer_id_michu', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
            
            
            with tab42:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_prospect[df_combine_prospect['statuss'] == 'active'].drop(columns=['customer_id_michu', 'branch_code']).reset_index(drop=True).rename(lambda x: x + 1))
        if role == 'Admin' or role == 'under_admin':
            with tab5:
                tab51, tab52 = st.tabs(["Not Take Loan", "Take Loan"])
                with tab51:
                    st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Emergence </span>)</span> 👇🏻', unsafe_allow_html=True)
                    st.write(df_merged_emegancce[df_merged_emegancce['statuss'] != 'active'].drop(columns=['em_id']).reset_index(drop=True).rename(lambda x: x + 1))
                
                
                with tab52:
                    st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Emergence </span>)</span> 👇🏻', unsafe_allow_html=True)
                    st.write(df_merged_emegancce[df_merged_emegancce['statuss'] == 'active'].drop(columns=['em_id']).reset_index(drop=True).rename(lambda x: x + 1))
            
        

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



