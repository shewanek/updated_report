import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import home_sidebar
import plotly.graph_objects as go
import pandas as pd
from dependence import load_customer_detail, load_customer_detail_informal
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
    update_activity()
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
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
        <center> <h3 class = "title_dash"> Michu Collection Detail Report </h3> </center>
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
        tab_options = ["Wabbi & Kiyya-Formal", "Guyya & Kiyya-Informal"]
        active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
        if active_tab == "Wabbi & Kiyya-Formal":
            # unique_customer, unique_by_self, registed_by_branch, df_unique_all = load_unquiecustomer(role, username)
            df_combine_collection, df_combine_conversion, df_combine_arrears = load_customer_detail(role, username)
            df_combine_arrears['Michu Loan Product'] = df_combine_arrears['Michu Loan Product'].replace({'Michu 1.0': 'Wabbi'})


            # Combine unique values for filters
            combined_districts = sorted(set(df_combine_collection["District"].dropna().unique()) | set(df_combine_conversion["District"].dropna().unique()) | set(df_combine_arrears["District"].dropna().unique()))
            combined_branches = sorted(set(df_combine_collection["Branch"].dropna().unique()) | set(df_combine_conversion["Branch"].dropna().unique()) | set(df_combine_arrears["Branch"].dropna().unique()))

            start_dates = []
            end_dates = []

            

            if df_combine_conversion is not None and not df_combine_conversion.empty:
                start_dates.append(df_combine_conversion["Conversion Date"].min())
                end_dates.append(df_combine_conversion["Conversion Date"].max())
            
            # if df_combine_arrears is not None and not df_combine_arrears.empty:
            #     start_dates.append(df_combine_arrears["Maturity Date"].min())
            #     end_dates.append(df_combine_arrears["Maturity Date"].max())
            
            if df_combine_collection is not None and not df_combine_collection.empty:
                start_dates.append(df_combine_collection["Collected Date"].min())
                end_dates.append(df_combine_collection["Collected Date"].max())

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
                filtered_branches = sorted(set(df_combine_collection[df_combine_collection["District"].isin(district)]["Branch"].dropna().unique()) |
                                        set(df_combine_conversion[df_combine_conversion["District"].isin(district)]["Branch"].dropna().unique()) |
                                        set(df_combine_arrears[df_combine_arrears["District"].isin(district)]["Branch"].dropna().unique()))
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
                df_combine_collection = df_combine_collection[df_combine_collection["District"].isin(district)]
                df_combine_conversion = df_combine_conversion[df_combine_conversion["District"].isin(district)]
                df_combine_arrears = df_combine_arrears[df_combine_arrears["District"].isin(district)]
            
            if branch:
                df_combine_collection = df_combine_collection[df_combine_collection["Branch"].isin(branch)]
                df_combine_conversion = df_combine_conversion[df_combine_conversion["Branch"].isin(branch)]
                df_combine_arrears = df_combine_arrears[df_combine_arrears["Branch"].isin(branch)]


        
            df_combine_collection = df_combine_collection[(df_combine_collection["Collected Date"] >= date1) & (df_combine_collection["Collected Date"] <= date2)]
            df_combine_conversion = df_combine_conversion[(df_combine_conversion["Conversion Date"] >= date1) & (df_combine_conversion["Conversion Date"] <= date2)]
            # df_combine_arrears = df_combine_arrears[(df_combine_arrears["Maturity Date"] >= date1) & (df_combine_arrears["Maturity Date"] <= date2)]
            # st.write(df_combine_collection)


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

            total_in_arrears = df_combine_arrears['arr_Id'].nunique()
            total_collected =  df_combine_collection['Loan_Id'].nunique()
            total_conversion = df_combine_conversion['arr_Id'].nunique()
            collected_target =  total_in_arrears + total_conversion
            total_collectedd = total_collectedd = df_combine_collection[df_combine_collection['Paid Status'] == 'CLOSED']['Loan_Id'].nunique()

            principal_sum = df_combine_collection['Principal Collected'].sum()
            interest_sum = df_combine_collection['Interest Collected'].sum()
            penalty_sum = df_combine_collection['Penality Collected'].sum()

            amount_actual = float(principal_sum + interest_sum + penalty_sum)



            # amount_actual = float(df_combine_collection['Principal Collected'].sum())
            amount_target = float(df_combine_arrears['Approved Amount'].sum())
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
                fig.update_layout(height=300, margin=dict(t=30, b=30, l=0, r=0))
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
                fig.update_layout(height=300, margin=dict(t=30, b=30, l=0, r=0))
                return fig

        
            
            col2, col3, col4 = st.columns(3)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col2.metric(label="**Total In Arrears**", value=total_in_arrears, delta="Customer")
            col3.metric(label="**Total Collected**", value=total_collected, delta="Customer")
            col4.metric(label="**Total Conversion**", value=total_conversion, delta="Customer")
            # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
            # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

                
            # Usage in Streamlit
            if role == "Admin" or role == 'under_admin' or role == 'collection_admin':
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )
                with col2:
                    st.plotly_chart(create_amount_gauge(value=amount_actual, target=amount_target, title="Amount Performance", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )

                coll1, coll2 = st.columns(2)  
                with coll1:
                    # -- Per District --
                    # Drop duplicates to ensure unique District entries for summarization
                    district_summary = df_combine_arrears[['District']].drop_duplicates()

                    # Calculate Total In Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # Group by 'District' and sum the collected amounts
                    total_collected = (
                        df_combine_collection.groupby(['District'])
                        .agg({
                            'Principal Collected': 'sum',
                            'Interest Collected': 'sum',
                            'Penality Collected': 'sum'
                        })
                        .reset_index()
                    )
                    # Rename the total sum to 'Total Collected'
                    total_collected['Total Collected'] = (
                        total_collected['Principal Collected'] + 
                        total_collected['Interest Collected'] + 
                        total_collected['Penality Collected']
                    )
                    # Keep only relevant columns
                    total_collected = total_collected[['District', 'Total Collected']]

                    # # Calculate Total Collected
                    # total_collected = (df_combine_collection.groupby(['District']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge all summaries with the District summary
                    grouped_df = district_summary.merge(total_customers_in_arrears, on=['District'], how='left')
                    grouped_df = grouped_df.merge(total_conversion, on=['District'], how='left')
                    grouped_df = grouped_df.merge(total_collected, on=['District'], how='left')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].infer_objects(copy=False).astype(float)



                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions,
                        'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")

                    # Reset the index to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Define a styling function for the Total row
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    # Apply styling
                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per District ] 👇🏻")
                    st.write(styled_df)


                with coll2:
                    # -- Per District and Branch --
                    # Drop duplicates to ensure unique branches for summarization
                    district_branch_summary = df_combine_arrears[['District', 'Branch']].drop_duplicates()

                    # Calculate Total Customers in Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # Group by 'District' and sum the collected amounts
                    total_collected = (
                        df_combine_collection.groupby(['District', 'Branch'])
                        .agg({
                            'Principal Collected': 'sum',
                            'Interest Collected': 'sum',
                            'Penality Collected': 'sum'
                        })
                        .reset_index()
                    )
                    # Rename the total sum to 'Total Collected'
                    total_collected['Total Collected'] = (
                        total_collected['Principal Collected'] + 
                        total_collected['Interest Collected'] + 
                        total_collected['Penality Collected']
                    )
                    # Keep only relevant columns
                    total_collected = total_collected[['District', 'Branch', 'Total Collected']]

                    # # Calculate Total Collected
                    # total_collected = ( df_combine_collection.groupby(['District', 'Branch']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge the summaries with the district and branch data
                    grouped_df = district_branch_summary.merge(total_customers_in_arrears, on=['District', 'Branch'], how='outer')
                    grouped_df = grouped_df.merge(total_conversion, on=['District', 'Branch'], how='outer')
                    grouped_df = grouped_df.merge(total_collected, on=['District', 'Branch'], how='outer')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].infer_objects(copy=False).astype(float)



                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Branch': '',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions,
                        'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values with commas for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")
                    

                    # Reset the index and rename it to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Apply styling
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per Branch] 👇🏻")
                    st.write(styled_df)


            if role == 'Branch User':
                st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.7, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )
            if role == "District User":
                col3, col4 = st.columns([0.4,0.6])
                with col4:
                    st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.7, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=45, b=0, l=0, r=0)),
                        use_container_width=True
                    )
                with col3:
                    
                    # -- Per District and Branch --
                    # Drop duplicates to ensure unique branches for summarization
                    district_branch_summary = df_combine_arrears[['District', 'Branch']].drop_duplicates()

                    # Calculate Total Customers in Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # # Calculate Total Collected
                    # total_collected = ( df_combine_collection.groupby(['District', 'Branch']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge the summaries with the district and branch data
                    grouped_df = district_branch_summary.merge(total_customers_in_arrears, on=['District', 'Branch'], how='left')
                    grouped_df = grouped_df.merge(total_conversion, on=['District', 'Branch'], how='left')
                    # grouped_df = grouped_df.merge(total_collected, on=['District', 'Branch'], how='left')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    # grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0).astype(float)

                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    # total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Branch': '',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions
                        # 'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values with commas for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    # grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")

                    # Reset the index and rename it to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Apply styling
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per Branch] 👇🏻")
                    st.write(styled_df)

            
        
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
            tab2, tab3, tab4 = st.tabs(["In Arrears", "Collected", "Conversion"])
            

            with tab2:
                if role == 'District User':
                    st.markdown("""
                    <style>
                    [data-testid="stElementToolbar"] {
                    display: none;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">In Arrears Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_arrears.drop(columns=['arr_Id']).reset_index(drop=True).rename(lambda x: x + 1))
            with tab3:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_collection.drop(columns=['Loan_Id']).reset_index(drop=True).rename(lambda x: x + 1))
            
            with tab4:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Active Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_conversion.drop(columns=['arr_Id', 'Approved Amount', 'Approved Date', 'Maturity Date']).reset_index(drop=True).rename(lambda x: x + 1))
            # df_conversion
        elif active_tab == "Guyya & Kiyya-Informal":
            
            # unique_customer, unique_by_self, registed_by_branch, df_unique_all = load_unquiecustomer(role, username)
            df_combine_collection, df_combine_conversion, df_combine_arrears = load_customer_detail_informal(role, username)
            # df_combine_arrears['Michu Loan Product'] = df_combine_arrears['Michu Loan Product'].replace({'Michu 1.0': 'Wabbi'})


            # Combine unique values for filters
            combined_districts = sorted(set(df_combine_collection["District"].dropna().unique()) | set(df_combine_conversion["District"].dropna().unique()) | set(df_combine_arrears["District"].dropna().unique()))
            combined_branches = sorted(set(df_combine_collection["Branch"].dropna().unique()) | set(df_combine_conversion["Branch"].dropna().unique()) | set(df_combine_arrears["Branch"].dropna().unique()))

            start_dates = []
            end_dates = []

            

            if df_combine_conversion is not None and not df_combine_conversion.empty:
                start_dates.append(df_combine_conversion["Conversion Date"].min())
                end_dates.append(df_combine_conversion["Conversion Date"].max())
            
            # if df_combine_arrears is not None and not df_combine_arrears.empty:
            #     start_dates.append(df_combine_arrears["Maturity Date"].min())
            #     end_dates.append(df_combine_arrears["Maturity Date"].max())
            
            if df_combine_collection is not None and not df_combine_collection.empty:
                start_dates.append(df_combine_collection["Collected Date"].min())
                end_dates.append(df_combine_collection["Collected Date"].max())

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
                filtered_branches = sorted(set(df_combine_collection[df_combine_collection["District"].isin(district)]["Branch"].dropna().unique()) |
                                        set(df_combine_conversion[df_combine_conversion["District"].isin(district)]["Branch"].dropna().unique()) |
                                        set(df_combine_arrears[df_combine_arrears["District"].isin(district)]["Branch"].dropna().unique()))
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
                df_combine_collection = df_combine_collection[df_combine_collection["District"].isin(district)]
                df_combine_conversion = df_combine_conversion[df_combine_conversion["District"].isin(district)]
                df_combine_arrears = df_combine_arrears[df_combine_arrears["District"].isin(district)]
            
            if branch:
                df_combine_collection = df_combine_collection[df_combine_collection["Branch"].isin(branch)]
                df_combine_conversion = df_combine_conversion[df_combine_conversion["Branch"].isin(branch)]
                df_combine_arrears = df_combine_arrears[df_combine_arrears["Branch"].isin(branch)]


        
            df_combine_collection = df_combine_collection[(df_combine_collection["Collected Date"] >= date1) & (df_combine_collection["Collected Date"] <= date2)]
            df_combine_conversion = df_combine_conversion[(df_combine_conversion["Conversion Date"] >= date1) & (df_combine_conversion["Conversion Date"] <= date2)]
            # df_combine_arrears = df_combine_arrears[(df_combine_arrears["Maturity Date"] >= date1) & (df_combine_arrears["Maturity Date"] <= date2)]
            # st.write(df_combine_collection)


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

            total_in_arrears = df_combine_arrears['arr_Id'].nunique()
            total_collected =  df_combine_collection['Loan_Id'].nunique()
            total_conversion = df_combine_conversion['arr_Id'].nunique()
            collected_target =  total_in_arrears + total_conversion
            total_collectedd = total_collectedd = df_combine_collection[df_combine_collection['Paid Status'] == 'CLOSED']['Loan_Id'].nunique()

            principal_sum = df_combine_collection['Principal Collected'].sum()
            interest_sum = df_combine_collection['Interest Collected'].sum()
            penalty_sum = df_combine_collection['Penality Collected'].sum()

            amount_actual = float(principal_sum + interest_sum + penalty_sum)



            # amount_actual = float(df_combine_collection['Principal Collected'].sum())
            amount_target = float(df_combine_arrears['Approved Amount'].sum())
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
                fig.update_layout(height=300, margin=dict(t=30, b=30, l=0, r=0))
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
                fig.update_layout(height=300, margin=dict(t=30, b=30, l=0, r=0))
                return fig

        
            
            col2, col3, col4 = st.columns(3)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col2.metric(label="**Total In Arrears**", value=total_in_arrears, delta="Customer")
            col3.metric(label="**Total Collected**", value=total_collected, delta="Customer")
            col4.metric(label="**Total Conversion**", value=total_conversion, delta="Customer")
            # # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
            # # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

                
            # Usage in Streamlit
            if role == "Admin" or role == 'under_admin' or role == 'collection_admin':
                col1, col2 = st.columns(2)
                
                with col1:
                    st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )
                with col2:
                    st.plotly_chart(create_amount_gauge(value=amount_actual, target=amount_target, title="Amount Performance", thresholds=[0.5, 0.8, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )

                coll1, coll2 = st.columns(2)  
                with coll1:
                    # -- Per District --
                    # Drop duplicates to ensure unique District entries for summarization
                    district_summary = df_combine_arrears[['District']].drop_duplicates()

                    # Calculate Total In Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # Group by 'District' and sum the collected amounts
                    total_collected = (
                        df_combine_collection.groupby(['District'])
                        .agg({
                            'Principal Collected': 'sum',
                            'Interest Collected': 'sum',
                            'Penality Collected': 'sum'
                        })
                        .reset_index()
                    )
                    # Rename the total sum to 'Total Collected'
                    total_collected['Total Collected'] = (
                        total_collected['Principal Collected'] + 
                        total_collected['Interest Collected'] + 
                        total_collected['Penality Collected']
                    )
                    # Keep only relevant columns
                    total_collected = total_collected[['District', 'Total Collected']]

                    # # Calculate Total Collected
                    # total_collected = (df_combine_collection.groupby(['District']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge all summaries with the District summary
                    grouped_df = district_summary.merge(total_customers_in_arrears, on=['District'], how='left')
                    grouped_df = grouped_df.merge(total_conversion, on=['District'], how='left')
                    grouped_df = grouped_df.merge(total_collected, on=['District'], how='left')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].infer_objects(copy=False).astype(float)



                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions,
                        'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")

                    # Reset the index to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Define a styling function for the Total row
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    # Apply styling
                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per District ] 👇🏻")
                    st.write(styled_df)


                with coll2:
                    # -- Per District and Branch --
                    # Drop duplicates to ensure unique branches for summarization
                    district_branch_summary = df_combine_arrears[['District', 'Branch']].drop_duplicates()

                    # Calculate Total Customers in Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # Group by 'District' and sum the collected amounts
                    total_collected = (
                        df_combine_collection.groupby(['District', 'Branch'])
                        .agg({
                            'Principal Collected': 'sum',
                            'Interest Collected': 'sum',
                            'Penality Collected': 'sum'
                        })
                        .reset_index()
                    )
                    # Rename the total sum to 'Total Collected'
                    total_collected['Total Collected'] = (
                        total_collected['Principal Collected'] + 
                        total_collected['Interest Collected'] + 
                        total_collected['Penality Collected']
                    )
                    # Keep only relevant columns
                    total_collected = total_collected[['District', 'Branch', 'Total Collected']]

                    # # Calculate Total Collected
                    # total_collected = ( df_combine_collection.groupby(['District', 'Branch']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge the summaries with the district and branch data
                    grouped_df = district_branch_summary.merge(total_customers_in_arrears, on=['District', 'Branch'], how='outer')
                    grouped_df = grouped_df.merge(total_conversion, on=['District', 'Branch'], how='outer')
                    grouped_df = grouped_df.merge(total_collected, on=['District', 'Branch'], how='outer')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0)
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].infer_objects(copy=False).astype(float)



                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Branch': '',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions,
                        'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values with commas for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")
                    

                    # Reset the index and rename it to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Apply styling
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per Branch] 👇🏻")
                    st.write(styled_df)


            if role == 'Branch User':
                st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.7, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=50, b=0, l=0, r=0)),
                        use_container_width=True
                    )
            if role == "District User":
                col3, col4 = st.columns([0.4,0.6])
                with col4:
                    st.plotly_chart(create_conversion_gauge(value=total_conversion, target=collected_target, title="Conversion Performance", thresholds=[0.5, 0.7, 1.2], colors=["#f25829", "#f2a529", "#2bad4e"]
                        ).update_layout(margin=dict(t=45, b=0, l=0, r=0)),
                        use_container_width=True
                    )
                with col3:
                    
                    # -- Per District and Branch --
                    # Drop duplicates to ensure unique branches for summarization
                    district_branch_summary = df_combine_arrears[['District', 'Branch']].drop_duplicates()

                    # Calculate Total Customers in Arrears
                    total_customers_in_arrears = (df_combine_arrears.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_customers_in_arrears.rename(columns={'arr_Id': 'Total In Arrears'}, inplace=True)

                    # Calculate Total Conversion
                    total_conversion = (df_combine_conversion.groupby(['District', 'Branch']).agg({'arr_Id': 'count'}).reset_index())
                    total_conversion.rename(columns={'arr_Id': 'Total Conversion'}, inplace=True)

                    # # Calculate Total Collected
                    # total_collected = ( df_combine_collection.groupby(['District', 'Branch']).agg({'Principal Collected': 'sum'}).reset_index())
                    # total_collected.rename(columns={'Principal Collected': 'Total Collected'}, inplace=True)

                    # Merge the summaries with the district and branch data
                    grouped_df = district_branch_summary.merge(total_customers_in_arrears, on=['District', 'Branch'], how='left')
                    grouped_df = grouped_df.merge(total_conversion, on=['District', 'Branch'], how='left')
                    # grouped_df = grouped_df.merge(total_collected, on=['District', 'Branch'], how='left')

                    # Fill NaN values with 0 for missing data
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].fillna(0).astype(int)
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].fillna(0).astype(int)
                    # grouped_df['Total Collected'] = grouped_df['Total Collected'].fillna(0).astype(float)

                    # Calculate totals for the summary row
                    total_customers = grouped_df['Total In Arrears'].sum()
                    total_conversions = grouped_df['Total Conversion'].sum()
                    # total_collections = grouped_df['Total Collected'].sum()

                    # Add a summary row for totals
                    summary_row = pd.DataFrame([{
                        'District': 'Total',
                        'Branch': '',
                        'Total In Arrears': total_customers,
                        'Total Conversion': total_conversions
                        # 'Total Collected': total_collections
                    }])
                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                    # Format numeric values with commas for better readability
                    grouped_df['Total In Arrears'] = grouped_df['Total In Arrears'].map(lambda x: f"{x:,}")
                    grouped_df['Total Conversion'] = grouped_df['Total Conversion'].map(lambda x: f"{x:,}")
                    # grouped_df['Total Collected'] = grouped_df['Total Collected'].map(lambda x: f"{x:,.2f}")

                    # Reset the index and rename it to start from 1
                    grouped_df = grouped_df.reset_index(drop=True)
                    grouped_df.index = grouped_df.index + 1

                    # Apply styling
                    def highlight_total_row(s):
                        is_total = s['District'] == 'Total'
                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    styled_df = (
                        grouped_df.style.apply(highlight_total_row, axis=1)
                        .set_properties(**{'text-align': 'center'})
                    )

                    # Display the result
                    st.write(":blue[Per Branch] 👇🏻")
                    st.write(styled_df)

            
        
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
            tab2, tab3, tab4 = st.tabs(["In Arrears", "Collected", "Conversion"])
            

            with tab2:
                if role == 'District User':
                    st.markdown("""
                    <style>
                    [data-testid="stElementToolbar"] {
                    display: none;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">In Arrears Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_arrears.drop(columns=['arr_Id']).reset_index(drop=True).rename(lambda x: x + 1))
            with tab3:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Closed Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_collection.drop(columns=['Loan_Id']).reset_index(drop=True).rename(lambda x: x + 1))
            
            with tab4:
                st.markdown('<span style="color: #e38524;">**Michu Customer** (<span style="color: #00adef;">Active Status </span>)</span> 👇🏻', unsafe_allow_html=True)
                st.write(df_combine_conversion.drop(columns=['arr_Id', 'Approved Amount', 'Approved Date', 'Maturity Date']).reset_index(drop=True).rename(lambda x: x + 1))
             

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

