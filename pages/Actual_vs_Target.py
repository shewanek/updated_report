import streamlit as st
# from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import make_sidebar1, home_sidebar, logout
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import decimal
import numpy as np
from dependence import load_actual_vs_targetdata, load_kiyya_actual_vs_targetdata, load_actual_vs_targetdata_per_product
from dependence import update_activity, check_session_timeout
import traceback


pd.set_option('future.no_silent_downcasting', True)

# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()


# @st.cache_data
def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_cs = """
    <style>
        # div.block-container {
        #     padding-top: 1rem; /* Adjust this value to reduce padding-top */
        # }
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
    st.markdown(custom_cs, unsafe_allow_html=True)
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    update_activity()
    fy_start = st.session_state.get("fiscal_year_start")
    fy_end = st.session_state.get("fiscal_year_end")
    # print("Fiscal Year Start:", fy_start)
    st.markdown(custom_css, unsafe_allow_html=True)
    # with open('custom.css') as f:
    #     st.write(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    customm = """
        <style>
            .app-header {
                display: none;
            }
        </style>
        """

    # Apply the custom CSS
    st.markdown(customm, unsafe_allow_html=True)

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
        <center> <h3 class = "title_dash"> Target Performance Report</h3> </center>
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
    

    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        # st.switch_page("main.py")
        logout()

    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Initialize database connection using Singleton pattern
    # st.snow()
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    # Add custom CSS for margin
    st.markdown(
        """
        <style>
        .custom-radio {
            margin: 0 0; /* Adjust margin as needed (top and bottom) */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    fy_label = st.session_state.get("fiscal_year_label")

    if fy_label == "2024/2025":

        tab_options = ["Quarter (1 & 2)", "Quarter (3 & 4)"]
        # Add a div with a custom class around st.radio
        # st.markdown('<div class="custom-radio">', unsafe_allow_html=True)
        active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
        if active_tab == "Quarter (1 & 2)":
            try:
                # tab_options = ["Michu(Wabi & Guyya)", "Michu-Kiyya"]
                # active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
                # if active_tab == "Michu(Wabi & Guyya)":
                dis_branch, df_actual, df_target = load_actual_vs_targetdata(role, username, fy_start, fy_end)

                k_dis_branch, k_df_actual, k_df_target = load_kiyya_actual_vs_targetdata(role, username, fy_start, fy_end)
                # Get the maximum date of the current month

                
                # Get the current date and the maximum date for the current month
                current_date = datetime.now().date()
                current_month_max_date = current_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
                current_month_max_date = current_month_max_date.date()

                # Convert 'Actual Date' and 'Target Date' columns to datetime
                df_actual['Actual Date'] = pd.to_datetime(df_actual['Actual Date']).dt.date
                df_target['Target Date'] = pd.to_datetime(df_target['Target Date']).dt.date

                k_df_actual['Actual Date'] = pd.to_datetime(k_df_actual['Actual Date']).dt.date
                k_df_target['Target Date'] = pd.to_datetime(k_df_target['Target Date']).dt.date

                # Filter df_actual and df_target based on the current month's max date
                df_actual = df_actual[df_actual['Actual Date'] <= current_month_max_date]
                df_target = df_target[df_target['Target Date'] <= current_month_max_date]

                # Filter df_actual and df_target based on the current month's max date
                k_df_actual = k_df_actual[k_df_actual['Actual Date'] <= current_month_max_date]
                k_df_target = k_df_target[k_df_target['Target Date'] <= current_month_max_date]

                # Display the filtered DataFrames
                # dis_branch, df_actual, df_target
                merged_acttarg = pd.merge(df_actual, df_target, on='Branch Code', how='outer')
                df_merged =  pd.merge(dis_branch, merged_acttarg, on='Branch Code', how='inner')
                # df_merged

                # dis_branch, df_actual, df_target
                k_merged_acttarg = pd.merge(k_df_actual, k_df_target, on='Branch Code', how='outer')
                k_df_merged =  pd.merge(k_dis_branch, k_merged_acttarg, on='Branch Code', how='inner')

                # Combine unique values for filters
                combined_districts = sorted(set(df_merged["District"].dropna().unique()) | set(k_df_merged["District"].dropna().unique()))
                


                # Sidebar filters
                st.sidebar.image("pages/michu.png")
                # username = st.session_state.get("username", "")
                full_name = st.session_state.get("full_name", "")
                # role = st.session_state.get("role", "")
                # st.sidebar.write(f'Welcome, :orange[{full_name}]')
                st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
                st.sidebar.header("Please filter")

                # role = st.session_state.get("role", "")
                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':

                    district = st.sidebar.multiselect("Select District", options=combined_districts)
                    

                    if not district:
                        df_merged = df_merged.copy()
                        k_df_merged = k_df_merged.copy()
                    else:
                        df_merged = df_merged[df_merged["District"].isin(district)]
                        k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]

                if role != 'Branch User':
                    combined_branches = sorted(set(df_merged["Branch"].dropna().unique()) | set(k_df_merged["Branch"].dropna().unique()))
                    branch = st.sidebar.multiselect("Select Branch", options=combined_branches)

                    if not branch:
                        df_merged = df_merged.copy()
                        k_df_merged = k_df_merged.copy()
                    else:
                        df_merged = df_merged[df_merged["Branch"].isin(branch)]
                        k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                    
                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                    if not district and not branch:
                        df_merged = df_merged
                        k_df_merged = k_df_merged
                    elif district:
                        df_merged = df_merged[df_merged["District"].isin(district)]
                        k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]
                    elif branch:
                        df_merged = df_merged[df_merged["Branch"].isin(branch)]
                        k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                    else:
                        df_merged = df_merged[df_merged["District"].isin(district) & df_merged["Branch"].isin(branch)]
                        k_df_merged = k_df_merged[k_df_merged["District"].isin(district) & k_df_merged["Branch"].isin(branch)]

                if df_merged is not None and not df_merged.empty:
                    col1, col2 = st.sidebar.columns(2)

                    # Convert the date columns to datetime if they are not already
                    df_merged["Target Date"] = pd.to_datetime(df_merged["Target Date"], errors='coerce')
                    df_merged["Actual Date"] = pd.to_datetime(df_merged["Actual Date"], errors='coerce')

                    # Convert the date columns to datetime if they are not already
                    k_df_merged["Target Date"] = pd.to_datetime(k_df_merged["Target Date"], errors='coerce')
                    k_df_merged["Actual Date"] = pd.to_datetime(k_df_merged["Actual Date"], errors='coerce')

                    # Determine the overall min and max dates
                    overall_start_date = df_merged[["Target Date", "Actual Date"]].min().min()
                    overall_end_date = df_merged[["Target Date", "Actual Date"]].max().max()

                    # Sidebar date filters
                    with col1:
                        start_date = st.date_input(
                            "Start Date",
                            value=overall_start_date.date(),  # Convert to `date` for st.date_input
                            min_value=overall_start_date.date(),
                            max_value=overall_end_date.date(),
                        )

                    with col2:
                        end_date = st.date_input(
                            "End Date",
                            value=overall_end_date.date(),
                            min_value=overall_start_date.date(),
                            max_value=overall_end_date.date(),
                        )


                    # Convert start_date and end_date to datetime for comparison
                    start_date = pd.Timestamp(start_date)
                    end_date = pd.Timestamp(end_date)

                    # Filter the dataframe based on the selected date range
                    # df_filtered = df_merged[
                    #     (df_merged["Target Date"] >= start_date) & (df_merged["Target Date"] <= end_date)
                    # ].copy()

                    df_filtered = df_merged[
                        (start_date.to_period("M") <= df_merged["Target Date"].dt.to_period("M")) &
                        (end_date.to_period("M") >= df_merged["Target Date"].dt.to_period("M"))
                    ].copy()

                    # You can filter Actual Date separately if needed
                    df_filtered_actual = df_merged[
                        (df_merged["Actual Date"] >= start_date) & (df_merged["Actual Date"] <= end_date)
                    ].copy()


                    k_df_filtered = k_df_merged[
                        (start_date.to_period("M") <= k_df_merged["Target Date"].dt.to_period("M")) &
                        (end_date.to_period("M") >= k_df_merged["Target Date"].dt.to_period("M"))
                    ].copy()

                    # You can filter Actual Date separately if needed
                    k_df_filtered_actual = k_df_merged[
                        (k_df_merged["Actual Date"] >= start_date) & (k_df_merged["Actual Date"] <= end_date)
                    ].copy()



                # Hide the sidebar by default with custom CSS
                hide_sidebar_style = """
                    <style>
                        #MainMenu {visibility: hidden;}
                    </style>
                """
                st.markdown(hide_sidebar_style, unsafe_allow_html=True)
                if role == "Admin" or role == 'under_admin' or role == 'under_admin':
                    home_sidebar()
                else:
                    make_sidebar1()

            
                # df_combine
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
                
                # -- for admin and sales admin --

                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                    tab1, tab2= st.tabs(["📈 Aggregate Report", "🗃 Report per District & Branch"])
                    # # Drop duplicate target_Id and actual_Id
                    # with Tab3:
                    #     st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)

                    with tab1:
                        coll1, coll2 = st.columns(2)
                        with coll1:
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                            

                            
                            # Group by unique target_Id and sum the target columns
                            target_grouped = df_target_unique.groupby('target_Id').agg({
                                'Target Unique Customer': 'sum',
                                'Target Number Of Account': 'sum',
                                'Target Disbursed Amount': 'sum'
                            }).sum()
                
                            # Group by unique actual_Id and sum the actual columns
                            actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                                'Actual Unique Customer': 'sum',
                                'Actual Number Of Account': 'sum',
                                'Actual Disbursed Amount': 'sum'
                            }).sum()
                            # Aggregate the data to get total values
                            
                            totals = {
                                'Target Unique Customer': target_grouped['Target Unique Customer'],
                                'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                                'Target Number Of Account': target_grouped['Target Number Of Account'],
                                'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                                'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                                'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                            }

                            # Create the bar chart
                            fig = go.Figure()

                            # Add bars for Unique Customer and Number of Accounts
                            def format_num(num):
                                return f"{num:,.0f}"
                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                                name='Target',
                                marker_color= '#00adef',
                                yaxis='y1',
                                text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                                textposition='outside'
                            ))

                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y1',
                                text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                                textposition='outside'
                            ))

                            # Add bars for Disbursed Amount on secondary y-axis
                            # Function to format numbers with commas
                            def format_number(num):
                                if num >= 1_000_000:
                                    return f"{num / 1_000_000:,.2f}M"
                                return f"{num:,.2f}"
                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Target Disbursed Amount']],
                                name='Target',
                                marker_color='#00adef',
                                yaxis='y2',
                                text=[format_number(totals['Target Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Actual Disbursed Amount']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y2',
                                text=[format_number(totals['Actual Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            # Update the layout for better visualization
                            fig.update_layout(
                                title='Michu(Wabi & Guyya) YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                                xaxis=dict(title='Metrics'),
                                yaxis=dict(
                                    title='Unique Customer & Number of Accounts',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                ),
                                yaxis2=dict(
                                    title='Disbursed Amount',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                    anchor='free',
                                    overlaying='y',
                                    side='right',
                                    position=1
                                ),
                                barmode='group',  # Group the bars side by side
                                bargap=0.2,  # Gap between bars of adjacent location coordinates
                                bargroupgap=0.1, # Gap between bars of the same location coordinate
                                margin=dict(t=80),
                                # legend=dict(
                                # title='Legend',
                                # itemsizing='constant'
                                # )
                            )

                            # Display the chart in Streamlit
                            # st.write("### Michu - Target vs Actual Comparison")
                            st.plotly_chart(fig, use_container_width=True)


                        with coll2:
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')
                            

                            
                            # Group by unique target_Id and sum the target columns
                            target_grouped = k_df_target_unique.groupby('target_Id').agg({
                                'Target Unique Customer': 'sum',
                                'Target Number Of Account': 'sum',
                                'Target Disbursed Amount': 'sum'
                            }).sum()
                
                            # Group by unique actual_Id and sum the actual columns
                            actual_grouped = k_df_actual_unique.groupby('actual_Id').agg({
                                'Actual Unique Customer': 'sum',
                                'Actual Number Of Account': 'sum',
                                'Actual Disbursed Amount': 'sum'
                            }).sum()
                            # Aggregate the data to get total values
                            
                            totals = {
                                'Target Unique Customer': target_grouped['Target Unique Customer'],
                                'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                                'Target Number Of Account': target_grouped['Target Number Of Account'],
                                'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                                'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                                'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                            }

                            # Create the bar chart
                            fig = go.Figure()

                            # Add bars for Unique Customer and Number of Accounts
                            def format_num(num):
                                return f"{num:,.0f}"
                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                                name='Target',
                                marker_color= '#00adef',
                                yaxis='y1',
                                text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                                textposition='outside'
                            ))

                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y1',
                                text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                                textposition='outside'
                            ))

                            # Add bars for Disbursed Amount on secondary y-axis
                            # Function to format numbers with commas
                            def format_number(num):
                                if num >= 1_000_000:
                                    return f"{num / 1_000_000:,.2f}M"
                                return f"{num:,.2f}"
                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Target Disbursed Amount']],
                                name='Target',
                                marker_color='#00adef',
                                yaxis='y2',
                                text=[format_number(totals['Target Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Actual Disbursed Amount']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y2',
                                text=[format_number(totals['Actual Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            # Update the layout for better visualization
                            fig.update_layout(
                                title='Michu-Kiyya YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                                xaxis=dict(title='Metrics'),
                                yaxis=dict(
                                    title='Unique Customer & Number of Accounts',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                ),
                                yaxis2=dict(
                                    title='Disbursed Amount',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                    anchor='free',
                                    overlaying='y',
                                    side='right',
                                    position=1
                                ),
                                barmode='group',  # Group the bars side by side
                                bargap=0.2,  # Gap between bars of adjacent location coordinates
                                bargroupgap=0.1, # Gap between bars of the same location coordinate
                                margin=dict(t=80),
                                # legend=dict(
                                # title='Legend',
                                # itemsizing='constant'
                                # )
                            )

                            # Display the chart in Streamlit
                            # st.write("### Michu - Target vs Actual Comparison")
                            st.plotly_chart(fig, use_container_width=True)






                        col1,  col2 = st.columns([0.4, 0.4])

                        with col1:
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby('District').agg(
                                {'Target Unique Customer': 'sum', 'Target Number Of Account': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby('District').agg(
                                {'Actual Unique Customer': 'sum', 'Actual Number Of Account': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimal columns to float
                            target_grouped = target_grouped.apply(convert_to_float)
                            actual_grouped = actual_grouped.apply(convert_to_float)
                            # Merge the target and actual data on 'District' to align them
                            merged_df = target_grouped.merge(actual_grouped, on='District', how='outer')
                            

                            # Calculate the aggregated data for each metric
                            aggregated_data = {
                                'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                                'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                                'Target Number Of Account': merged_df['Target Number Of Account'].sum(),
                                'Actual Number Of Account': merged_df['Actual Number Of Account'].sum(),
                                'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                                'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                            }

                            # Calculate 'Percentage(%)' for each metric
                            aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                            aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                            aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)

                            # Define the metrics
                            metrics = ['Unique Customer', 'Number Of Account', 'Disbursed Amount']

                            # Create a list of dictionaries for final_df
                            final_df_data = []

                            for metric in metrics:
                                target_value = aggregated_data[f'Target {metric}']
                                actual_value = aggregated_data[f'Actual {metric}']
                                percent_value = aggregated_data[f'Percentage(%) {metric}']
                                
                                final_df_data.append({
                                    'Target': target_value,
                                    'Actual': actual_value,
                                    '%': percent_value,
                                    'Metric': metric
                                })

                            # Create final_df DataFrame
                            final_df = pd.DataFrame(final_df_data)

                            # Round the 'Target' and 'Actual' columns to two decimal points
                            final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                            final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format '%' with a percentage sign
                            final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                            # Drop rows where '%' is 'nan%'
                            filtered_df = final_df[final_df['%'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        else:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # green color for values 70% and above
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                    .set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '20px'
                                                    }) \
                                                    .set_table_styles([
                                                        dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                    ])

                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result with custom CSS
                            st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                            
                            st.markdown(styled_html, unsafe_allow_html=True)

                            st.write(" ")
                            st.write(" ")
                            st.write(" ")

                        with col2:
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = k_df_target_unique.groupby('District').agg(
                                {'Target Unique Customer': 'sum', 'Target Number Of Account': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = k_df_actual_unique.groupby('District').agg(
                                {'Actual Unique Customer': 'sum', 'Actual Number Of Account': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimal columns to float
                            target_grouped = target_grouped.apply(convert_to_float)
                            actual_grouped = actual_grouped.apply(convert_to_float)
                            # Merge the target and actual data on 'District' to align them
                            merged_df = target_grouped.merge(actual_grouped, on='District', how='outer')
                            

                            # Calculate the aggregated data for each metric
                            aggregated_data = {
                                'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                                'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                                'Target Number Of Account': merged_df['Target Number Of Account'].sum(),
                                'Actual Number Of Account': merged_df['Actual Number Of Account'].sum(),
                                'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                                'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                            }

                            # Calculate 'Percentage(%)' for each metric
                            aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                            aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                            aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)

                            # Define the metrics
                            metrics = ['Unique Customer', 'Number Of Account', 'Disbursed Amount']

                            # Create a list of dictionaries for final_df
                            final_df_data = []

                            for metric in metrics:
                                target_value = aggregated_data[f'Target {metric}']
                                actual_value = aggregated_data[f'Actual {metric}']
                                percent_value = aggregated_data[f'Percentage(%) {metric}']
                                
                                final_df_data.append({
                                    'Target': target_value,
                                    'Actual': actual_value,
                                    '%': percent_value,
                                    'Metric': metric
                                })

                            # Create final_df DataFrame
                            final_df = pd.DataFrame(final_df_data)

                            # Round the 'Target' and 'Actual' columns to two decimal points
                            final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                            final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format '%' with a percentage sign
                            final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                            # Drop rows where '%' is 'nan%'
                            filtered_df = final_df[final_df['%'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        else:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # green color for values 70% and above
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                    .set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '20px'
                                                    }) \
                                                    .set_table_styles([
                                                        dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                    ])

                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result with custom CSS
                            st.write(":orange[Michu-Kiyya YTD] (:blue[Year-To-Date]) 👇🏻")
                            
                            st.markdown(styled_html, unsafe_allow_html=True)

                            st.write(" ")
                            st.write(" ")
                            st.write(" ")

                    

                    with tab2:
                        tab3, tab4 = st.tabs(["Per District", "Per Branch"])
                        
                        # Display combined data in a table
                        
                        with tab3:
                            col1, col2 = st.columns([0.7, 0.7])
                            with col1:
                                # -- per District --
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='left')

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Unique Customer] 👇🏻")
                                st.write(styled_df)

                            with col1:
                                
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                                df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District']).agg(
                                    {'Target Number Of Account': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Number Of Account': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='left')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                                total_target_number = grouped_df['Target Number Of Account'].sum()
                                total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Number Of Account': total_target_number,
                                    'Actual Number Of Account': total_actual_number,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                                st.write(styled_df)
                            

                            with col1:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='left')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed != 0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('')
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                st.write(styled_df)

                            # Michu-Kiyya
                                
                            with col2:
                                # -- per District --
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Unique Customer'] = k_df_target_unique['Target Unique Customer'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Unique Customer'] = k_df_actual_unique['Actual Unique Customer'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()
                                
                                # st.write(target_grouped)

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                # st.write(grouped_df)

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Unique Customer] 👇🏻")
                                st.write(styled_df)

                            with col2:
                                
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Number Of Account'] = k_df_target_unique['Target Number Of Account'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Number Of Account'] = k_df_actual_unique['Actual Number Of Account'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District']).agg(
                                    {'Target Number Of Account': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District']).agg(
                                    {'Actual Number Of Account': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                                total_target_number = grouped_df['Target Number Of Account'].sum()
                                total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Number Of Account': total_target_number,
                                    'Actual Number Of Account': total_actual_number,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Number Of Account]  👇🏻")
                                st.write(styled_df)
                            

                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Disbursed Amount'] = k_df_target_unique['Target Disbursed Amount'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Disbursed Amount'] = k_df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed != 0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('')
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Disbursed Amount] 👇🏻")
                                st.write(styled_df)



                        with tab4:
                            col1, col2 = st.columns([0.6, 0.6])
                            # -- per branch --
                            with col1:

                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)



                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                                st.write(styled_df)



                            with col1:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                # # Ensure all numerical values are converted to floats
                                # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                                # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                                
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                                df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Number Of Account': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Number Of Account': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                                # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                                #     grouped_df['Target Number Of Account'].replace(0, np.nan)
                                # ) * 100


                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                                total_target_number = grouped_df['Target Number Of Account'].sum()
                                total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Number Of Account': total_target_number,
                                    'Actual Number Of Account': total_actual_number,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:.0f}")
                                grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                                st.write(styled_df)



                            with col1:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                st.write(styled_df)

                            # Michu Kiyya

                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Unique Customer'] = k_df_target_unique['Target Unique Customer'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Unique Customer'] = k_df_actual_unique['Actual Unique Customer'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Unique Customer]  👇🏻")
                                st.write(styled_df)



                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                # # Ensure all numerical values are converted to floats
                                # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                                # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                                
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Number Of Account'] = k_df_target_unique['Target Number Of Account'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Number Of Account'] = k_df_actual_unique['Actual Number Of Account'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Number Of Account': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Number Of Account': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                                # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                                #     grouped_df['Target Number Of Account'].replace(0, np.nan)
                                # ) * 100


                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                                total_target_number = grouped_df['Target Number Of Account'].sum()
                                total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Number Of Account': total_target_number,
                                    'Actual Number Of Account': total_actual_number,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:.0f}")
                                grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Number Of Account]  👇🏻")
                                st.write(styled_df)



                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                k_df_target_unique.loc[:,'Target Disbursed Amount'] = k_df_target_unique['Target Disbursed Amount'].astype(float)
                                k_df_actual_unique.loc[:,'Actual Disbursed Amount'] = k_df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                st.write(":orange[Michu-Kiyya Disbursed Amount] 👇🏻")
                                st.write(styled_df)



                    

                            
                # -- for role District User --

                if role == 'District User':
                    tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per Branch"])
                    # # Drop duplicate target_Id and actual_Id
                    # with Tab31:
                    #     st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)
                    with tab1:
                        cool1, cool2 = st.columns(2)
                        with cool1:
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            
                            # Group by unique target_Id and sum the target columns
                            target_grouped = df_target_unique.groupby('target_Id').agg({
                                'Target Unique Customer': 'sum',
                                'Target Number Of Account': 'sum',
                                'Target Disbursed Amount': 'sum'
                            }).sum()
                
                            # Group by unique actual_Id and sum the actual columns
                            actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                                'Actual Unique Customer': 'sum',
                                'Actual Number Of Account': 'sum',
                                'Actual Disbursed Amount': 'sum'
                            }).sum()
                            # Aggregate the data to get total values
                            
                            totals = {
                                'Target Unique Customer': target_grouped['Target Unique Customer'],
                                'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                                'Target Number Of Account': target_grouped['Target Number Of Account'],
                                'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                                'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                                'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                            }

                            # Create the bar chart
                            fig = go.Figure()

                            # Add bars for Unique Customer and Number of Accounts
                            def format_num(num):
                                return f"{num:,.0f}"
                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                                name='Target',
                                marker_color= '#00adef',
                                yaxis='y1',
                                text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                                textposition='outside'
                            ))

                            fig.add_trace(go.Bar(
                                x=['Unique Customer', 'Number of Accounts'],
                                y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y1',
                                text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                                textposition='outside'
                            ))

                            # Add bars for Disbursed Amount on secondary y-axis
                            # Function to format numbers with commas
                            def format_number(num):
                                if num >= 1_000_000:
                                    return f"{num / 1_000_000:,.2f}M"
                                return f"{num:,.2f}"
                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Target Disbursed Amount']],
                                name='Target',
                                marker_color='#00adef',
                                yaxis='y2',
                                text=[format_number(totals['Target Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            fig.add_trace(go.Bar(
                                x=['Disbursed Amount'],
                                y=[totals['Actual Disbursed Amount']],
                                name='Actual',
                                marker_color='#e38524',
                                yaxis='y2',
                                text=[format_number(totals['Actual Disbursed Amount'])],
                                textposition='outside',
                                showlegend=False
                            ))

                            # Update the layout for better visualization
                            fig.update_layout(
                                title='Michu(Wabi & Guyya) YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                                xaxis=dict(title='Metrics'),
                                yaxis=dict(
                                    title='Unique Customer & Number of Accounts',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                ),
                                yaxis2=dict(
                                    title='Disbursed Amount',
                                    titlefont=dict(color='black'),
                                    tickfont=dict(color='black'),
                                    anchor='free',
                                    overlaying='y',
                                    side='right',
                                    position=1
                                ),
                                barmode='group',  # Group the bars side by side
                                bargap=0.2,  # Gap between bars of adjacent location coordinates
                                bargroupgap=0.1, # Gap between bars of the same location coordinate
                                margin=dict(t=80),
                                # legend=dict(
                                # title='Legend',
                                # itemsizing='constant'
                                # )
                            )

                            # Display the chart in Streamlit
                            # st.write("### Michu - Target vs Actual Comparison")
                            st.plotly_chart(fig, use_container_width=True)


                            
                            with cool1:
                                # Drop duplicates based on target_Id and actual_Id
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                                def convert_to_float(series):
                                    return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                                # Group and aggregate the data for each metric using unique IDs
                                unique_customer_df = df_target_unique.groupby(['District']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_unique_customer_df = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()
                                # Convert decimals to float
                                unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                                actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                                
                                unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='left')

                                unique_customer_df['Percentage(%)'] = (
                                    (unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100).round(0)
                                unique_customer_df['Metric'] = 'Unique Customer'

                                account_df = df_target_unique.groupby(['District']).agg(
                                    {'Target Number Of Account': 'sum'}).reset_index()
                                actual_account_df = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Number Of Account': 'sum'}).reset_index()
                                account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                                actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                                account_df = account_df.merge(actual_account_df, on=['District'], how='left')
                                account_df['Percentage(%)'] = (
                                    account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                                account_df['Metric'] = 'Number Of Account'

                                disbursed_amount_df = df_target_unique.groupby(['District']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_disbursed_amount_df = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()
                                # Convert decimals to float
                                disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                                
                                actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                                
                                disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='left')
                                disbursed_amount_df['Percentage(%)'] = (
                                    disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                                disbursed_amount_df['Metric'] = 'Disbursed Amount'

                                # Rename columns to have consistent names
                                unique_customer_df = unique_customer_df.rename(columns={
                                    'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                                account_df = account_df.rename(columns={
                                    'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                                disbursed_amount_df = disbursed_amount_df.rename(columns={
                                    'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                                # Combine the DataFrames into one
                                combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])
                                # Round the 'Target' and 'Actual' columns to 2 decimal points
                                combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                                combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                                # Format 'Percentage(%)' with a percentage sign
                                combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Reset the index and rename it to start from 1
                                combined_df_reset = combined_df.reset_index(drop=True)
                                combined_df_reset.index = combined_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('')
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors
                                
                                styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                                .set_properties(**{
                                                                    'text-align': 'center'
                                                                }) \
                                                                .set_table_styles([
                                                                    dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                                ])
                                # Convert styled DataFrame to HTML
                                styled_html = styled_df.to_html()

                                # Display the result
                                st.write(":orange[Target vs Actual YTD] (:blue[Year-To-Date]) 👇🏻")
                                st.write(styled_html, unsafe_allow_html=True)



                                st.write("")
                                st.write("")

                            with cool2:
                                k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                                
                                # Group by unique target_Id and sum the target columns
                                target_grouped = k_df_target_unique.groupby('target_Id').agg({
                                    'Target Unique Customer': 'sum',
                                    'Target Number Of Account': 'sum',
                                    'Target Disbursed Amount': 'sum'
                                }).sum()
                    
                                # Group by unique actual_Id and sum the actual columns
                                actual_grouped = k_df_actual_unique.groupby('actual_Id').agg({
                                    'Actual Unique Customer': 'sum',
                                    'Actual Number Of Account': 'sum',
                                    'Actual Disbursed Amount': 'sum'
                                }).sum()
                                # Aggregate the data to get total values
                                
                                totals = {
                                    'Target Unique Customer': target_grouped['Target Unique Customer'],
                                    'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                                    'Target Number Of Account': target_grouped['Target Number Of Account'],
                                    'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                                    'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                                    'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                                }

                                # Create the bar chart
                                fig = go.Figure()

                                # Add bars for Unique Customer and Number of Accounts
                                def format_num(num):
                                    return f"{num:,.0f}"
                                fig.add_trace(go.Bar(
                                    x=['Unique Customer', 'Number of Accounts'],
                                    y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                                    name='Target',
                                    marker_color= '#00adef',
                                    yaxis='y1',
                                    text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                                    textposition='outside'
                                ))

                                fig.add_trace(go.Bar(
                                    x=['Unique Customer', 'Number of Accounts'],
                                    y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                                    name='Actual',
                                    marker_color='#e38524',
                                    yaxis='y1',
                                    text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                                    textposition='outside'
                                ))

                                # Add bars for Disbursed Amount on secondary y-axis
                                # Function to format numbers with commas
                                def format_number(num):
                                    if num >= 1_000_000:
                                        return f"{num / 1_000_000:,.2f}M"
                                    return f"{num:,.2f}"
                                fig.add_trace(go.Bar(
                                    x=['Disbursed Amount'],
                                    y=[totals['Target Disbursed Amount']],
                                    name='Target',
                                    marker_color='#00adef',
                                    yaxis='y2',
                                    text=[format_number(totals['Target Disbursed Amount'])],
                                    textposition='outside',
                                    showlegend=False
                                ))

                                fig.add_trace(go.Bar(
                                    x=['Disbursed Amount'],
                                    y=[totals['Actual Disbursed Amount']],
                                    name='Actual',
                                    marker_color='#e38524',
                                    yaxis='y2',
                                    text=[format_number(totals['Actual Disbursed Amount'])],
                                    textposition='outside',
                                    showlegend=False
                                ))

                                # Update the layout for better visualization
                                fig.update_layout(
                                    title='Michu-Kiyya YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                                    xaxis=dict(title='Metrics'),
                                    yaxis=dict(
                                        title='Unique Customer & Number of Accounts',
                                        titlefont=dict(color='black'),
                                        tickfont=dict(color='black'),
                                    ),
                                    yaxis2=dict(
                                        title='Disbursed Amount',
                                        titlefont=dict(color='black'),
                                        tickfont=dict(color='black'),
                                        anchor='free',
                                        overlaying='y',
                                        side='right',
                                        position=1
                                    ),
                                    barmode='group',  # Group the bars side by side
                                    bargap=0.2,  # Gap between bars of adjacent location coordinates
                                    bargroupgap=0.1, # Gap between bars of the same location coordinate
                                    margin=dict(t=80),
                                    # legend=dict(
                                    # title='Legend',
                                    # itemsizing='constant'
                                    # )
                                )

                                # Display the chart in Streamlit
                                # st.write("### Michu - Target vs Actual Comparison")
                                st.plotly_chart(fig, use_container_width=True)


                                # col1, col2 = st.columns([0.1, 0.9])
                                with cool2:
                                    # Drop duplicates based on target_Id and actual_Id
                                    k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                                    k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')
                                    def convert_to_float(series):
                                        return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                                    # Group and aggregate the data for each metric using unique IDs
                                    unique_customer_df = k_df_target_unique.groupby(['District']).agg(
                                        {'Target Unique Customer': 'sum'}).reset_index()
                                    actual_unique_customer_df = k_df_actual_unique.groupby(['District']).agg(
                                        {'Actual Unique Customer': 'sum'}).reset_index()
                                    # Convert decimals to float
                                    unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                                    actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                                    
                                    unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='outer')

                                    unique_customer_df['Percentage(%)'] = (
                                        (unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100).round(0)
                                    unique_customer_df['Metric'] = 'Unique Customer'

                                    account_df = k_df_target_unique.groupby(['District']).agg(
                                        {'Target Number Of Account': 'sum'}).reset_index()
                                    actual_account_df = k_df_actual_unique.groupby(['District']).agg(
                                        {'Actual Number Of Account': 'sum'}).reset_index()
                                    account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                                    actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                                    account_df = account_df.merge(actual_account_df, on=['District'], how='outer')
                                    account_df['Percentage(%)'] = (
                                        account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                                    account_df['Metric'] = 'Number Of Account'

                                    disbursed_amount_df = k_df_target_unique.groupby(['District']).agg(
                                        {'Target Disbursed Amount': 'sum'}).reset_index()
                                    actual_disbursed_amount_df = k_df_actual_unique.groupby(['District']).agg(
                                        {'Actual Disbursed Amount': 'sum'}).reset_index()
                                    # Convert decimals to float
                                    disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                                    
                                    actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                                    
                                    disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='outer')
                                    disbursed_amount_df['Percentage(%)'] = (
                                        disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                                    disbursed_amount_df['Metric'] = 'Disbursed Amount'

                                    # Rename columns to have consistent names
                                    unique_customer_df = unique_customer_df.rename(columns={
                                        'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                                    account_df = account_df.rename(columns={
                                        'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                                    disbursed_amount_df = disbursed_amount_df.rename(columns={
                                        'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                                    # Combine the DataFrames into one
                                    combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])
                                    # Round the 'Target' and 'Actual' columns to 2 decimal points
                                    combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                                    combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                                    # Format 'Percentage(%)' with a percentage sign
                                    combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Reset the index and rename it to start from 1
                                    combined_df_reset = combined_df.reset_index(drop=True)
                                    combined_df_reset.index = combined_df_reset.index + 1

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('')
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors
                                    
                                    styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                                    .set_properties(**{
                                                                        'text-align': 'center'
                                                                    }) \
                                                                    .set_table_styles([
                                                                        dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                                    ])
                                    # Convert styled DataFrame to HTML
                                    styled_html = styled_df.to_html()

                                    # Display the result
                                    st.write(":orange[Target vs Actual YTD] (:blue[Year-To-Date]) 👇🏻")
                                    st.write(styled_html, unsafe_allow_html=True)



                                    st.write("")
                                    st.write("")




                    with tab2:
                        colll1, colll2 = st.columns(2)
                        # Display combined data in a table
                        with colll1:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                            df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                            # Calculate Percentage(%)
                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                    else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                    else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                ),
                                axis=1
                            )

                            # # Calculate 'Percentage(%)' and handle division by zero
                            # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                            total_target_unique = grouped_df['Target Unique Customer'].sum()
                            total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                            total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                            
                            # # Handle division by zero
                            # if total_target_unique == 'nan':
                            #     total_percentage = 0
                            # else:
                            #     total_percentage = (total_actual_unique / total_target_unique) * 100

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Unique Customer': total_target_unique,
                                'Actual Unique Customer': total_actual_unique,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                            # Reset the index and rename it to start from 1

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                            
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1
                            # st.markdown("""
                            # <style>
                            #     [data-testid="stElementToolbar"] {
                            #     display: none;
                            #     }
                            # </style>
                            # """, unsafe_allow_html=True)

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                            st.write(styled_df)



                        with colll1:
                            # # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            # # Ensure all numerical values are converted to floats
                            # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                            # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                            
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                            df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                            # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                            #         grouped_df['Target Number Of Account'].replace(0, np.nan)
                            #     ) * 100

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                            
                            total_target_number = grouped_df['Target Number Of Account'].sum()
                            total_actual_number = grouped_df['Actual Number Of Account'].sum()
                            total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number !=0 else 0
                            

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Number Of Account': total_target_number,
                                'Actual Number Of Account': total_actual_number,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('') 
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                            st.write(styled_df)



                        with colll1:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                            df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='left')

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                    else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                    else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                ),
                                axis=1
                            )

                            # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                            total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                            total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                            total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Disbursed Amount': total_target_disbursed,
                                'Actual Disbursed Amount': total_actual_disbursed,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                            # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                            grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount]  👇🏻")
                            st.write(styled_df)

                        # Michu-Kiyya

                        with colll2:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            k_df_target_unique.loc[:,'Target Unique Customer'] = k_df_target_unique['Target Unique Customer'].astype(float)
                            k_df_actual_unique.loc[:,'Actual Unique Customer'] = k_df_actual_unique['Actual Unique Customer'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                            # Calculate Percentage(%)
                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                    else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                    else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                ),
                                axis=1
                            )

                            # # Calculate 'Percentage(%)' and handle division by zero
                            # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                            total_target_unique = grouped_df['Target Unique Customer'].sum()
                            total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                            total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                            
                            # # Handle division by zero
                            # if total_target_unique == 'nan':
                            #     total_percentage = 0
                            # else:
                            #     total_percentage = (total_actual_unique / total_target_unique) * 100

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Unique Customer': total_target_unique,
                                'Actual Unique Customer': total_actual_unique,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                            # Reset the index and rename it to start from 1

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                            
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1
                            # st.markdown("""
                            # <style>
                            #     [data-testid="stElementToolbar"] {
                            #     display: none;
                            #     }
                            # </style>
                            # """, unsafe_allow_html=True)

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('') 
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":orange[Michu-Kiyya Unique Customer]  👇🏻")
                            st.write(styled_df)



                        with colll2:
                            # # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            # # Ensure all numerical values are converted to floats
                            # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                            # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                            
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            k_df_target_unique.loc[:,'Target Number Of Account'] = k_df_target_unique['Target Number Of Account'].astype(float)
                            k_df_actual_unique.loc[:,'Actual Number Of Account'] = k_df_actual_unique['Actual Number Of Account'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                            # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                            #         grouped_df['Target Number Of Account'].replace(0, np.nan)
                            #     ) * 100

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                            
                            total_target_number = grouped_df['Target Number Of Account'].sum()
                            total_actual_number = grouped_df['Actual Number Of Account'].sum()
                            total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number !=0 else 0
                            

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Number Of Account': total_target_number,
                                'Actual Number Of Account': total_actual_number,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('') 
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":orange[Michu-Kiyya Number Of Account]  👇🏻")
                            st.write(styled_df)



                        with colll2:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            k_df_target_unique.loc[:,'Target Disbursed Amount'] = k_df_target_unique['Target Disbursed Amount'].astype(float)
                            k_df_actual_unique.loc[:,'Actual Disbursed Amount'] = k_df_actual_unique['Actual Disbursed Amount'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                    else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                    else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                ),
                                axis=1
                            )

                            # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                            total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                            total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                            total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Disbursed Amount': total_target_disbursed,
                                'Actual Disbursed Amount': total_actual_disbursed,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                            # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                            grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            st.write(":orange[Michu-Kiyya Disbursed Amount]  👇🏻")
                            st.write(styled_df)

                    



                    

                if role == 'Branch User':
                    ccool1, ccool2 = st.columns(2)
                    with ccool1:
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = df_target_unique.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()

                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        fig.update_layout(
                            title='Michu(Wabi & Guyya) YTD(<span style="color: #00adef;">Year-To-Date </span>)',
                            xaxis=dict(title='Metrics'),
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)
                        # col1, col2 = st.columns([0.1, 0.9])
                    with ccool1:
                        # Drop duplicates based on target_Id and actual_Id
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Function to convert decimal.Decimal to float
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                        # Group and aggregate the data for each metric
                        unique_customer_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_unique_customer_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()

                        # Convert decimals to float
                        unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                        actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                        unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='left')

                        # Function to calculate percentage safely
                        def calculate_percentage_unique(row):
                            if row['Target Unique Customer'] == 0:
                                if row['Actual Unique Customer'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                        
                        # unique_customer_df['Percentage(%)'] = (
                        #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                        unique_customer_df['Metric'] = 'Unique Customer'

                        account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Number Of Account': 'sum'}).reset_index()
                        actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Number Of Account': 'sum'}).reset_index()

                        # Convert decimals to float
                        account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                        actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                        account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_account(row):
                            if row['Target Number Of Account'] == 0:
                                if row['Actual Number Of Account'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                        # account_df['Percentage(%)'] = (
                        #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                        account_df['Metric'] = 'Number Of Account'

                        disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()

                        # Convert decimals to float
                        disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                        actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                        disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_dis(row):
                            if row['Target Disbursed Amount'] == 0:
                                if row['Actual Disbursed Amount'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                        # disbursed_amount_df['Percentage(%)'] = (
                        #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                        disbursed_amount_df['Metric'] = 'Disbursed Amount'

                        # Rename columns to have consistent names
                        unique_customer_df = unique_customer_df.rename(columns={
                            'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                        account_df = account_df.rename(columns={
                            'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                        disbursed_amount_df = disbursed_amount_df.rename(columns={
                            'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                        # Combine the DataFrames into one
                        combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])

                        combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                        combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format 'Percentage(%)' with a percentage sign
                        combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Reset the index and rename it to start from 1
                        combined_df_reset = combined_df.reset_index(drop=True)
                        combined_df_reset.index = combined_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                            .set_properties(**{
                                                                'text-align': 'center'
                                                            }) \
                                                            .set_table_styles([
                                                                dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                            ])
                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result
                        st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                        # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                        st.write(styled_html, unsafe_allow_html=True)

                        st.write(" ")
                        st.write(" ")
                        st.write(" ")



                    with ccool2:
                        k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                        k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = k_df_target_unique.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()

                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = k_df_actual_unique.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        fig.update_layout(
                            title='Michu-Kiyya YTD(<span style="color: #00adef;">Year-To-Date </span>)',
                            xaxis=dict(title='Metrics'),
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)
                        col1, col2 = st.columns([0.1, 0.9])
                        
                        with col2:
                            # Drop duplicates based on target_Id and actual_Id
                            k_df_target_unique = k_df_filtered.drop_duplicates(subset='target_Id')
                            k_df_actual_unique = k_df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Function to convert decimal.Decimal to float
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                            # Group and aggregate the data for each metric
                            unique_customer_df = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_unique_customer_df = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()

                            # Convert decimals to float
                            unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                            actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                            unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='outer')

                            # Function to calculate percentage safely
                            def calculate_percentage_unique(row):
                                if row['Target Unique Customer'] == 0:
                                    if row['Actual Unique Customer'] == 0:
                                        return np.nan  # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                            
                            # unique_customer_df['Percentage(%)'] = (
                            #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                            unique_customer_df['Metric'] = 'Unique Customer'

                            account_df = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_account_df = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()

                            # Convert decimals to float
                            account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                            actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                            account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='outer')

                            def calculate_percentage_account(row):
                                if row['Target Number Of Account'] == 0:
                                    if row['Actual Number Of Account'] == 0:
                                        return np.nan  # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                            # account_df['Percentage(%)'] = (
                            #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                            account_df['Metric'] = 'Number Of Account'

                            disbursed_amount_df = k_df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_disbursed_amount_df = k_df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()

                            # Convert decimals to float
                            disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                            actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                            disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='outer')

                            def calculate_percentage_dis(row):
                                if row['Target Disbursed Amount'] == 0:
                                    if row['Actual Disbursed Amount'] == 0:
                                        return np.nan  # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                            # disbursed_amount_df['Percentage(%)'] = (
                            #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                            disbursed_amount_df['Metric'] = 'Disbursed Amount'

                            # Rename columns to have consistent names
                            unique_customer_df = unique_customer_df.rename(columns={
                                'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                            account_df = account_df.rename(columns={
                                'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                            disbursed_amount_df = disbursed_amount_df.rename(columns={
                                'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                            # Combine the DataFrames into one
                            combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])

                            combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                            combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format 'Percentage(%)' with a percentage sign
                            combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Reset the index and rename it to start from 1
                            combined_df_reset = combined_df.reset_index(drop=True)
                            combined_df_reset.index = combined_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                                .set_properties(**{
                                                                    'text-align': 'center'
                                                                }) \
                                                                .set_table_styles([
                                                                    dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                                ])
                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result
                            st.write(":orange[Michu-Kiyya YTD] (:blue[Year-To-Date]) 👇🏻")
                            # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                            st.write(styled_html, unsafe_allow_html=True)

                            st.write(" ")
                            st.write(" ")
                            st.write(" ")

                        
                    
                    
                    # st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)



            except Exception as e:
                st.error(f"An error occurred while loading data: {e}")
            # finally:
            #     if db_instance:
            #         db_instance.close_connection()
            # Auto-refresh interval (in seconds)
            refresh_interval = 600  # 5 minutes
            st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")









        if active_tab == "Quarter (3 & 4)":
            try:
                
                # tab_options = ["Michu(Wabi & Guyya)", "Michu-Kiyya"]
                # active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
                # if active_tab == "Michu(Wabi & Guyya)":
                dis_branch, df_actual, df_target = load_actual_vs_targetdata_per_product(role, username, fy_start, fy_end)

                # k_dis_branch, k_df_actual, k_df_target = load_kiyya_actual_vs_targetdata(role, username)
                # Get the maximum date of the current month

                
                # Get the current date and the maximum date for the current month
                current_date = datetime.now().date()
                current_month_max_date = current_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
                current_month_max_date = current_month_max_date.date()

                # Convert 'Actual Date' and 'Target Date' columns to datetime
                df_actual['Actual Date'] = pd.to_datetime(df_actual['Actual Date']).dt.date
                df_target['Target Date'] = pd.to_datetime(df_target['Target Date']).dt.date

                # k_df_actual['Actual Date'] = pd.to_datetime(k_df_actual['Actual Date']).dt.date
                # k_df_target['Target Date'] = pd.to_datetime(k_df_target['Target Date']).dt.date

                # Filter df_actual and df_target based on the current month's max date
                df_actual = df_actual[df_actual['Actual Date'] <= current_month_max_date]
                df_target = df_target[df_target['Target Date'] <= current_month_max_date]

                # # Filter df_actual and df_target based on the current month's max date
                # k_df_actual = k_df_actual[k_df_actual['Actual Date'] <= current_month_max_date]
                # k_df_target = k_df_target[k_df_target['Target Date'] <= current_month_max_date]
                # st.write(df_target)

                # Display the filtered DataFrames
                # dis_branch, df_actual, df_target
                merged_acttarg = pd.merge(df_actual, df_target, on=['Branch Code', 'Product Type'], how='outer') 
                # merged_acttarg
                    
                df_merged =  pd.merge(dis_branch, merged_acttarg, on='Branch Code', how='right')

                # df_merged

                # # dis_branch, df_actual, df_target
                # k_merged_acttarg = pd.merge(k_df_actual, k_df_target, on='Branch Code', how='outer')
                # k_df_merged =  pd.merge(k_dis_branch, k_merged_acttarg, on='Branch Code', how='inner')

                # Combine unique values for filters
                combined_districts = sorted(set(df_merged["District"].dropna().unique()))
                

                # Sidebar filters
                st.sidebar.image("pages/michu.png")
                # username = st.session_state.get("username", "")
                full_name = st.session_state.get("full_name", "")
                # role = st.session_state.get("role", "")
                # st.sidebar.write(f'Welcome, :orange[{full_name}]')
                st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
                st.sidebar.header("Please filter")

                
                # Get unique product types
                combined_products = sorted(df_merged["Product Type"].dropna().unique())

                # Add a product filter at the top of the page 
                selected_product = st.selectbox("Select Product Type", options=["All"] + combined_products)

                # Apply the product filter if a specific product type is selected
                if selected_product != "All":
                    df_merged = df_merged[df_merged["Product Type"] == selected_product]


                # st.write(df_merged)
                    
                # role = st.session_state.get("role", "")
                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':

                    district = st.sidebar.multiselect("Select District", options=combined_districts)
                    

                    if not district:
                        df_merged = df_merged.copy()
                        # k_df_merged = k_df_merged.copy()
                    else:
                        df_merged = df_merged[df_merged["District"].isin(district)]
                        # k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]

                if role != 'Branch User':
                    combined_branches = sorted(set(df_merged["Branch"].dropna().unique()))
                    branch = st.sidebar.multiselect("Select Branch", options=combined_branches)

                    if not branch:
                        df_merged = df_merged.copy()
                        # k_df_merged = k_df_merged.copy()
                    else:
                        df_merged = df_merged[df_merged["Branch"].isin(branch)]
                        # k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                    
                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                    if not district and not branch:
                        df_merged = df_merged
                        # k_df_merged = k_df_merged
                    elif district:
                        df_merged = df_merged[df_merged["District"].isin(district)]
                        # k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]
                    elif branch:
                        df_merged = df_merged[df_merged["Branch"].isin(branch)]
                        # k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                    else:
                        df_merged = df_merged[df_merged["District"].isin(district) & df_merged["Branch"].isin(branch)]
                        # k_df_merged = k_df_merged[k_df_merged["District"].isin(district) & k_df_merged["Branch"].isin(branch)]

                if df_merged is not None and not df_merged.empty:
                    col1, col2 = st.sidebar.columns(2)

                    # Convert the date columns to datetime if they are not already
                    df_merged["Target Date"] = pd.to_datetime(df_merged["Target Date"], errors='coerce')
                    df_merged["Actual Date"] = pd.to_datetime(df_merged["Actual Date"], errors='coerce')

                    # # Convert the date columns to datetime if they are not already
                    # k_df_merged["Target Date"] = pd.to_datetime(k_df_merged["Target Date"], errors='coerce')
                    # k_df_merged["Actual Date"] = pd.to_datetime(k_df_merged["Actual Date"], errors='coerce')

                    # Determine the overall min and max dates
                    overall_start_date = df_merged[["Target Date", "Actual Date"]].min().min()
                    overall_end_date = df_merged[["Target Date", "Actual Date"]].max().max()

                    # Sidebar date filters
                    with col1:
                        start_date = st.date_input(
                            "Start Date",
                            value=overall_start_date.date(),  # Convert to `date` for st.date_input
                            min_value=overall_start_date.date(),
                            max_value=overall_end_date.date(),
                        )

                    with col2:
                        end_date = st.date_input(
                            "End Date",
                            value=overall_end_date.date(),
                            min_value=overall_start_date.date(),
                            max_value=overall_end_date.date(),
                        )


                    # Convert start_date and end_date to datetime for comparison
                    start_date = pd.Timestamp(start_date)
                    end_date = pd.Timestamp(end_date)

                    # Filter the dataframe based on the selected date range
                    # df_filtered = df_merged[
                    #     (df_merged["Target Date"] >= start_date) & (df_merged["Target Date"] <= end_date)
                    # ].copy()

                    df_filtered = df_merged[
                        (start_date.to_period("M") <= df_merged["Target Date"].dt.to_period("M")) &
                        (end_date.to_period("M") >= df_merged["Target Date"].dt.to_period("M"))
                    ].copy()

                    # You can filter Actual Date separately if needed
                    df_filtered_actual = df_merged[
                        (df_merged["Actual Date"] >= start_date) & (df_merged["Actual Date"] <= end_date)
                    ].copy()


                    # k_df_filtered = k_df_merged[
                    #     (start_date.to_period("M") <= k_df_merged["Target Date"].dt.to_period("M")) &
                    #     (end_date.to_period("M") >= k_df_merged["Target Date"].dt.to_period("M"))
                    # ].copy()

                    # # You can filter Actual Date separately if needed
                    # k_df_filtered_actual = k_df_merged[
                    #     (k_df_merged["Actual Date"] >= start_date) & (k_df_merged["Actual Date"] <= end_date)
                    # ].copy()



                # Hide the sidebar by default with custom CSS
                hide_sidebar_style = """
                    <style>
                        #MainMenu {visibility: hidden;}
                    </style>
                """
                st.markdown(hide_sidebar_style, unsafe_allow_html=True)
                if role == "Admin" or role == 'under_admin' or role == 'under_admin':
                    home_sidebar()
                else:
                    make_sidebar1()

            
                # df_combine
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
                
                # -- for admin and sales admin --

                if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                    tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per District & Branch"])
                    # # Drop duplicate target_Id and actual_Id
                    # with Tab3:
                    #     st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)

                    with tab1:
                        coll1, coll2 = st.columns(2)
                        
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                        

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = df_target_unique.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()
            
                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        fig.update_layout(
                            title=f'<span style="text-decoration: underline;"> Michu([<span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span>] YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date</span>) </span>',
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)


                    





                        





                        col1,  col2 = st.columns([0.2, 0.8])

                        with col2:
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby('District').agg(
                                {'Target Unique Customer': 'sum', 'Target Number Of Account': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby('District').agg(
                                {'Actual Unique Customer': 'sum', 'Actual Number Of Account': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimal columns to float
                            target_grouped = target_grouped.apply(convert_to_float)
                            actual_grouped = actual_grouped.apply(convert_to_float)
                            # Merge the target and actual data on 'District' to align them
                            merged_df = target_grouped.merge(actual_grouped, on='District', how='outer')
                            

                            # Calculate the aggregated data for each metric
                            aggregated_data = {
                                'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                                'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                                'Target Number Of Account': merged_df['Target Number Of Account'].sum(),
                                'Actual Number Of Account': merged_df['Actual Number Of Account'].sum(),
                                'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                                'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                            }

                            # Calculate 'Percentage(%)' for each metric
                            aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                            aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                            aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)

                            # Define the metrics
                            metrics = ['Unique Customer', 'Number Of Account', 'Disbursed Amount']

                            # Create a list of dictionaries for final_df
                            final_df_data = []

                            for metric in metrics:
                                target_value = aggregated_data[f'Target {metric}']
                                actual_value = aggregated_data[f'Actual {metric}']
                                percent_value = aggregated_data[f'Percentage(%) {metric}']
                                
                                final_df_data.append({
                                    'Target': target_value,
                                    'Actual': actual_value,
                                    '%': percent_value,
                                    'Metric': metric
                                })

                            # Create final_df DataFrame
                            final_df = pd.DataFrame(final_df_data)

                            # Round the 'Target' and 'Actual' columns to two decimal points
                            final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                            final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format '%' with a percentage sign
                            final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                            # Drop rows where '%' is 'nan%'
                            filtered_df = final_df[final_df['%'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        else:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # green color for values 70% and above
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                    .set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '20px'
                                                    }) \
                                                    .set_table_styles([
                                                        dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                    ])

                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result with custom CSS
                            # st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                            st.write(
                                f'<span style="text-decoration: underline;">Michu([<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                                unsafe_allow_html=True
                            )

                            st.markdown(styled_html, unsafe_allow_html=True)

                            st.write(" ")
                            st.write(" ")
                            st.write(" ")

                    

                    with tab2:
                        col21, col22 = st.columns([0.1, 0.9])
                        with col22:
                            tab3, tab4 = st.tabs(["Per District", "Per Branch"])
                            
                            # Display combined data in a table
                            
                            with tab3: 
                                col1, col2 = st.columns([0.1, 0.9])
                                with col2:
                                    # -- per District --
                                    # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Replace None/NaN with zero and convert to float
                                    df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                    df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)
                                    


                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District']).agg(
                                        {'Target Unique Customer': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District']).agg(
                                        {'Actual Unique Customer': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)

                                    # # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                    # Calculate Percentage(%)
                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                            else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                            else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                        ),
                                        axis=1
                                    )

                                    # # Calculate 'Percentage(%)' and handle division by zero
                                    # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                    total_target_unique = grouped_df['Target Unique Customer'].sum()
                                    total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                    total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                    
                                    # # Handle division by zero
                                    # if total_target_unique == 'nan':
                                    #     total_percentage = 0
                                    # else:
                                    #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Target Unique Customer': total_target_unique,
                                        'Actual Unique Customer': total_actual_unique,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                    grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                                    grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                                    # Reset the index and rename it to start from 1

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                    
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1
                                    # st.markdown("""
                                    # <style>
                                    #     [data-testid="stElementToolbar"] {
                                    #     display: none;
                                    #     }
                                    # </style>
                                    # """, unsafe_allow_html=True)

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('') 
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Unique Customer] 👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Unique Customer</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)

                                with col2:
                                    
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Ensure all numerical values are converted to floats
                                    df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                                    df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District']).agg(
                                        {'Target Number Of Account': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District']).agg(
                                        {'Actual Number Of Account': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)
                                    # Create an explicit copy
                                    # grouped_df.fillna(0, inplace=True)  # Replace None/NaN with 0  

                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                            else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                            else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                        ),
                                        axis=1
                                    )

                                    # # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                    
                                    total_target_number = grouped_df['Target Number Of Account'].sum()
                                    total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                    total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                    

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Target Number Of Account': total_target_number,
                                        'Actual Number Of Account': total_actual_number,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                    grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                                    grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                    # Reset the index and rename it to start from 1
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('') 
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Number Of Account</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)
                                

                                with col2:
                                    # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Ensure all numerical values are converted to floats
                                    df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                    df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District']).agg(
                                        {'Target Disbursed Amount': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District']).agg(
                                        {'Actual Disbursed Amount': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)

                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                            else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                            else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                        ),
                                        axis=1
                                    )

                                    # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                    total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                    total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                    total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed != 0 else 0

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Target Disbursed Amount': total_target_disbursed,
                                        'Actual Disbursed Amount': total_actual_disbursed,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                    # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                    grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                    grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                    # Reset the index and rename it to start from 1
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('')
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Disbursed Amount</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)

                        

                            with tab4:
                                col1, col2 = st.columns([0.1, 0.9])
                                # -- per branch --
                                with col2:

                                    # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Ensure all numerical values are converted to floats
                                    df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                    df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)



                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                        {'Target Unique Customer': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                        {'Actual Unique Customer': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)
                                    # st.write(grouped_df)

                                    # # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                    # Calculate Percentage(%)
                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                            else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                            else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                        ),
                                        axis=1
                                    )

                                    # # Calculate 'Percentage(%)' and handle division by zero
                                    # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                    total_target_unique = grouped_df['Target Unique Customer'].sum()
                                    total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                    total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                    
                                    # # Handle division by zero
                                    # if total_target_unique == 'nan':
                                    #     total_percentage = 0
                                    # else:
                                    #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Branch': '',
                                        'Target Unique Customer': total_target_unique,
                                        'Actual Unique Customer': total_actual_unique,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                    grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:.0f}")
                                    grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:.0f}")

                                    # Reset the index and rename it to start from 1

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                    
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1
                                    # st.markdown("""
                                    # <style>
                                    #     [data-testid="stElementToolbar"] {
                                    #     display: none;
                                    #     }
                                    # </style>
                                    # """, unsafe_allow_html=True)

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('') 
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Unique Customer</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)



                                with col2:
                                    # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                    # # Ensure all numerical values are converted to floats
                                    # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                                    # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                                    
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Ensure all numerical values are converted to floats
                                    df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                                    df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                        {'Target Number Of Account': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                        {'Actual Number Of Account': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)

                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                            else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                            else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                        ),
                                        axis=1
                                    )

                                    # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                                    #     grouped_df['Target Number Of Account'].replace(0, np.nan)
                                    # ) * 100


                                    # # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                    
                                    total_target_number = grouped_df['Target Number Of Account'].sum()
                                    total_actual_number = grouped_df['Actual Number Of Account'].sum()
                                    total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                    

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Branch': '',
                                        'Target Number Of Account': total_target_number,
                                        'Actual Number Of Account': total_actual_number,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                    grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:.0f}")
                                    grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:.0f}")

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                    # Reset the index and rename it to start from 1
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('') 
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Number Of Account</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)



                                with col2:
                                    # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                    # Ensure all numerical values are converted to floats
                                    df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                    df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                    # Group and aggregate the data for each metric using unique IDs
                                    target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                        {'Target Disbursed Amount': 'sum'}).reset_index()
                                    actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                        {'Actual Disbursed Amount': 'sum'}).reset_index()

                                    # Merge the target and actual data on 'District' and 'Branch' to align them
                                    grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                                    # Replace all NaN/None values with zero
                                    grouped_df = grouped_df.fillna(0)

                                    grouped_df['Percentage(%)'] = grouped_df.apply(
                                        lambda row: (
                                            np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                            else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                            else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                        ),
                                        axis=1
                                    )

                                    # Calculate 'Percentage(%)'
                                    # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                    # Format 'Percentage(%)' with a percentage sign
                                    grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                    # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                    total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                    total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                    total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                                    # Create a summary row
                                    summary_row = pd.DataFrame([{
                                        'District': 'Total',
                                        'Branch': '',
                                        'Target Disbursed Amount': total_target_disbursed,
                                        'Actual Disbursed Amount': total_actual_disbursed,
                                        'Percentage(%)': f"{total_percentage:.2f}%"
                                    }])

                                    # Append the summary row to the grouped DataFrame
                                    grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                    # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                    grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                    grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                    # Drop rows where 'Percentage(%)' is 'nan%'
                                    filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                    # Reset the index and rename it to start from 1
                                    grouped_df_reset = filtered_df.reset_index(drop=True)
                                    grouped_df_reset.index = grouped_df_reset.index + 1

                                    # Apply styling
                                    def highlight_columns(s):
                                        colors = []
                                        for val in s:
                                            if isinstance(val, str) and '%' in val:
                                                percentage_value = float(val.strip('%'))
                                                if percentage_value < 50:
                                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                                elif 50 <= percentage_value < 70:
                                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                                elif percentage_value >= 70:
                                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                                else:
                                                    colors.append('') 
                                            else:
                                                colors.append('')  # no color for other values
                                        return colors

                                    # Define function to highlight the Total row
                                    def highlight_total_row(s):
                                        is_total = s['District'] == 'Total'
                                        return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                    # Center-align data and apply styling
                                    styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                    .apply(highlight_total_row, axis=1)\
                                                                    .set_properties(**{'text-align': 'center'})

                                    # Display the result
                                    # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                    st.write(
                                        f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Disbursed Amount</span></span>',
                                        unsafe_allow_html=True
                                    )
                                    st.write(styled_df)

                            


                    with tab1:
                        col1, col2 = st.columns([0.5, 0.5])
                        # with col1:
                        # Get the current date
                        current_date = datetime.now().date()

                        # Calculate the start and end date of the current month
                        start_of_month = current_date.replace(day=1)
                        end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                        # Filter the dataframe based on the selected date range
                        df_filtered = df_merged[
                            (df_merged["Target Date"].dt.date >= start_of_month) & 
                            (df_merged["Target Date"].dt.date <= end_of_month)
                        ].copy()

                        df_filtered_actual = df_merged[
                            (df_merged["Actual Date"].dt.date >= start_of_month) & 
                            (df_merged["Actual Date"].dt.date <= end_of_month)
                        ].copy()

                        # Drop duplicates before aggregating if needed (optional)
                        df_filtered = df_filtered.drop_duplicates(subset='target_Id')
                        df_filtered_actual = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = df_filtered.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()
            
                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = df_filtered_actual.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        fig.update_layout(
                            # title='Michu(Wabi & Guyya) MTD (<span style="color: #00adef;">Month-To-Date </span>)',
                            title=f'<span style="text-decoration: underline;"> Michu([<span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span>] MTD (<span style="color: #00adef; text-decoration: underline;">Month-To-Date</span>) </span>',
                            xaxis=dict(title='Metrics'),
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)

                            
                        c0ll12, coll22 = st.columns([0.2, 0.8])
                        with coll22:
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby('District').agg(
                                {'Target Unique Customer': 'sum', 'Target Number Of Account': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby('District').agg(
                                {'Actual Unique Customer': 'sum', 'Actual Number Of Account': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimal columns to float
                            target_grouped = target_grouped.apply(convert_to_float)
                            actual_grouped = actual_grouped.apply(convert_to_float)
                            # Merge the target and actual data on 'District' to align them
                            merged_df = target_grouped.merge(actual_grouped, on='District', how='left')
                            

                            # Calculate the aggregated data for each metric
                            aggregated_data = {
                                'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                                'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                                'Target Number Of Account': merged_df['Target Number Of Account'].sum(),
                                'Actual Number Of Account': merged_df['Actual Number Of Account'].sum(),
                                'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                                'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                            }

                            # Calculate 'Percentage(%)' for each metric
                            aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                            aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                            aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)


                            # Define the metrics
                            metrics = ['Unique Customer', 'Number Of Account', 'Disbursed Amount']

                            # Create a list of dictionaries for final_df
                            final_df_data = []

                            for metric in metrics:
                                target_value = aggregated_data[f'Target {metric}']
                                actual_value = aggregated_data[f'Actual {metric}']
                                percent_value = aggregated_data[f'Percentage(%) {metric}']
                                
                                final_df_data.append({
                                    'Target': target_value,
                                    'Actual': actual_value,
                                    '%': percent_value,
                                    'Metric': metric
                                })

                            # Create final_df DataFrame
                            final_df = pd.DataFrame(final_df_data)

                            # Round the 'Target' and 'Actual' columns to two decimal points
                            final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                            final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format '%' with a percentage sign
                            final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                            # Drop rows where '%' is 'nan%'
                            filtered_df = final_df[final_df['%'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                    .set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '20px'
                                                    }) \
                                                    .set_table_styles([
                                                        dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                    ])

                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result with custom CSS
                            # st.write(":orange[Michu(Wabi & Guyya) MTD] (:blue[Month-To-Date]) 👇🏻")
                            st.write(
                                    f'<span style="text-decoration: underline;">Michu([<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] MTD (<span style="color: #00adef;">Month-To-Date</span>)</span>',
                                    unsafe_allow_html=True
                                )
                            
                            st.markdown(styled_html, unsafe_allow_html=True)

                            st.write(" ")
                            st.write(" ")
                            st.write(" ")

                            


                            
                # -- for role District User --

                if role == 'District User':
                    tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per Branch"])
                    # # Drop duplicate target_Id and actual_Id
                    # with Tab31:
                    #     st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)
                    with tab1:
                        
                        # with cool1:
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = df_target_unique.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()
            
                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        fig.update_layout(
                            # title='Michu(Wabi & Guyya) YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                            title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date </span>) </span>',
                            xaxis=dict(title='Metrics'),
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)


                        cool1, cool2 = st.columns([0.2, 0.8])
                        with cool2:
                            # Drop duplicates based on target_Id and actual_Id
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                            # Group and aggregate the data for each metric using unique IDs
                            unique_customer_df = df_target_unique.groupby(['District']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_unique_customer_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()
                            # Convert decimals to float
                            unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                            actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                            
                            unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='left')

                            unique_customer_df['Percentage(%)'] = (
                                (unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100).round(0)
                            unique_customer_df['Metric'] = 'Unique Customer'

                            account_df = df_target_unique.groupby(['District']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_account_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()
                            account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                            actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                            account_df = account_df.merge(actual_account_df, on=['District'], how='left')
                            account_df['Percentage(%)'] = (
                                account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                            account_df['Metric'] = 'Number Of Account'

                            disbursed_amount_df = df_target_unique.groupby(['District']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_disbursed_amount_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimals to float
                            disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                            
                            actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                            
                            disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='left')
                            disbursed_amount_df['Percentage(%)'] = (
                                disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                            disbursed_amount_df['Metric'] = 'Disbursed Amount'

                            # Rename columns to have consistent names
                            unique_customer_df = unique_customer_df.rename(columns={
                                'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                            account_df = account_df.rename(columns={
                                'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                            disbursed_amount_df = disbursed_amount_df.rename(columns={
                                'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                            # Combine the DataFrames into one
                            combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])
                            # Round the 'Target' and 'Actual' columns to 2 decimal points
                            combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                            combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format 'Percentage(%)' with a percentage sign
                            combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Reset the index and rename it to start from 1
                            combined_df_reset = combined_df.reset_index(drop=True)
                            combined_df_reset.index = combined_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors
                            
                            styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                            .set_properties(**{
                                                                'text-align': 'center'
                                                            }) \
                                                            .set_table_styles([
                                                                dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                            ])
                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result
                            # st.write(":orange[Target vs Actual YTD] (:blue[Year-To-Date]) 👇🏻")
                            st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                                unsafe_allow_html=True
                            )
                            st.write(styled_html, unsafe_allow_html=True)



                            st.write("")
                            st.write("")

                            




                    with tab2:
                        colll1, colll2 = st.columns([0.1, 0.9])
                        # Display combined data in a table
                        with colll2:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                            df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                            # grouped_df
                            grouped_df = grouped_df.fillna(0)

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                            # Calculate Percentage(%)
                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                    else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                    else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                ),
                                axis=1
                            )

                            # # Calculate 'Percentage(%)' and handle division by zero
                            # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                            total_target_unique = grouped_df['Target Unique Customer'].sum()
                            total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                            total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                            
                            # # Handle division by zero
                            # if total_target_unique == 'nan':
                            #     total_percentage = 0
                            # else:
                            #     total_percentage = (total_actual_unique / total_target_unique) * 100

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Unique Customer': total_target_unique,
                                'Actual Unique Customer': total_actual_unique,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                            # Reset the index and rename it to start from 1

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                            
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1
                            # st.markdown("""
                            # <style>
                            #     [data-testid="stElementToolbar"] {
                            #     display: none;
                            #     }
                            # </style>
                            # """, unsafe_allow_html=True)

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            # st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                            st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Unique Customer</span></span>',
                                unsafe_allow_html=True
                            )
                            st.write(styled_df)



                        with colll2:
                            # # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            # # Ensure all numerical values are converted to floats
                            # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                            # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                            
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                            df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                            grouped_df = grouped_df.fillna(0)

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                                        else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                                        else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                                    ),
                                    axis=1
                                )

                            # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                            #         grouped_df['Target Number Of Account'].replace(0, np.nan)
                            #     ) * 100

                            # # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                            
                            total_target_number = grouped_df['Target Number Of Account'].sum()
                            total_actual_number = grouped_df['Actual Number Of Account'].sum()
                            total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number !=0 else 0
                            

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Number Of Account': total_target_number,
                                'Actual Number Of Account': total_actual_number,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('') 
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                            st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Number Of Account</span></span>',
                                unsafe_allow_html=True
                            )
                            st.write(styled_df)



                        with colll2:
                            # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            # Ensure all numerical values are converted to floats
                            df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                            df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                            # Group and aggregate the data for each metric using unique IDs
                            target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()

                            # Merge the target and actual data on 'District' and 'Branch' to align them
                            grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                            grouped_df = grouped_df.fillna(0)

                            grouped_df['Percentage(%)'] = grouped_df.apply(
                                lambda row: (
                                    np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                    else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                    else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                ),
                                axis=1
                            )

                            # Calculate 'Percentage(%)'
                            # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                            # Format 'Percentage(%)' with a percentage sign
                            grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                            total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                            total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                            total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                            # Create a summary row
                            summary_row = pd.DataFrame([{
                                'District': 'Total',
                                'Branch': '',
                                'Target Disbursed Amount': total_target_disbursed,
                                'Actual Disbursed Amount': total_actual_disbursed,
                                'Percentage(%)': f"{total_percentage:.2f}%"
                            }])

                            # Append the summary row to the grouped DataFrame
                            grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                            # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                            grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                            grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                            # Drop rows where 'Percentage(%)' is 'nan%'
                            filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            # Reset the index and rename it to start from 1
                            grouped_df_reset = filtered_df.reset_index(drop=True)
                            grouped_df_reset.index = grouped_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors

                            # Define function to highlight the Total row
                            def highlight_total_row(s):
                                is_total = s['District'] == 'Total'
                                return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            # Center-align data and apply styling
                            styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                            .apply(highlight_total_row, axis=1)\
                                                            .set_properties(**{'text-align': 'center'})

                            # Display the result
                            # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount]  👇🏻")
                            st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Disbursed Amount</span></span>',
                                unsafe_allow_html=True
                            )
                            st.write(styled_df)

                        # Michu-Kiyya


                    



                    with tab1:
                        ccol1, ccol2 = st.columns(2)
                        # with ccol1:
                        # Get the current date
                        current_date = datetime.now().date()

                        # Calculate the start and end date of the current month
                        start_of_month = current_date.replace(day=1)
                        end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                        # Filter the dataframe based on the selected date range
                        df_filtered = df_merged[
                            (df_merged["Target Date"].dt.date >= start_of_month) & 
                            (df_merged["Target Date"].dt.date <= end_of_month)
                        ].copy()

                        df_filtered_actual = df_merged[
                            (df_merged["Actual Date"].dt.date >= start_of_month) & 
                            (df_merged["Actual Date"].dt.date <= end_of_month)
                        ].copy()

                        # Drop duplicates before aggregating if needed (optional)
                        df_filtered = df_filtered.drop_duplicates(subset='target_Id')
                        df_filtered_actual = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        # Group by unique target_Id and sum the target columns
                        target_grouped = df_filtered.groupby('target_Id').agg({
                            'Target Unique Customer': 'sum',
                            'Target Number Of Account': 'sum',
                            'Target Disbursed Amount': 'sum'
                        }).sum()
            
                        # Group by unique actual_Id and sum the actual columns
                        actual_grouped = df_filtered_actual.groupby('actual_Id').agg({
                            'Actual Unique Customer': 'sum',
                            'Actual Number Of Account': 'sum',
                            'Actual Disbursed Amount': 'sum'
                        }).sum()
                        # Aggregate the data to get total values
                        
                        totals = {
                            'Target Unique Customer': target_grouped['Target Unique Customer'],
                            'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                            'Target Number Of Account': target_grouped['Target Number Of Account'],
                            'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                            'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                            'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                        }

                        # Create the bar chart
                        fig = go.Figure()

                        # Add bars for Unique Customer and Number of Accounts
                        def format_num(num):
                            return f"{num:,.0f}"
                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                            name='Target',
                            marker_color= '#00adef',
                            yaxis='y1',
                            text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                            textposition='outside'
                        ))

                        fig.add_trace(go.Bar(
                            x=['Unique Customer', 'Number of Accounts'],
                            y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y1',
                            text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                            textposition='outside'
                        ))

                        # Add bars for Disbursed Amount on secondary y-axis
                        # Function to format numbers with commas
                        def format_number(num):
                            if num >= 1_000_000:
                                return f"{num / 1_000_000:,.2f}M"
                            return f"{num:,.2f}"
                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Target Disbursed Amount']],
                            name='Target',
                            marker_color='#00adef',
                            yaxis='y2',
                            text=[format_number(totals['Target Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        fig.add_trace(go.Bar(
                            x=['Disbursed Amount'],
                            y=[totals['Actual Disbursed Amount']],
                            name='Actual',
                            marker_color='#e38524',
                            yaxis='y2',
                            text=[format_number(totals['Actual Disbursed Amount'])],
                            textposition='outside',
                            showlegend=False
                        ))

                        # Update the layout for better visualization
                        current_month_name = datetime.now().strftime("%B")
                        fig.update_layout(
                            # title=f'Michu(Wabi & Guyya), Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
                            
                            title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef; text-decoration: underline;">{current_month_name} </span>) </span>',
                            xaxis=dict(title='Metrics'),
                            yaxis=dict(
                                title='Unique Customer & Number of Accounts',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                            ),
                            yaxis2=dict(
                                title='Disbursed Amount',
                                titlefont=dict(color='black'),
                                tickfont=dict(color='black'),
                                anchor='free',
                                overlaying='y',
                                side='right',
                                position=1
                            ),
                            barmode='group',  # Group the bars side by side
                            bargap=0.2,  # Gap between bars of adjacent location coordinates
                            bargroupgap=0.1, # Gap between bars of the same location coordinate
                            margin=dict(t=80),
                            # legend=dict(
                            # title='Legend',
                            # itemsizing='constant'
                            # )
                        )

                        # Display the chart in Streamlit
                        # st.write("### Michu - Target vs Actual Comparison")
                        st.plotly_chart(fig, use_container_width=True)


                        col1, col2 = st.columns([0.2, 0.8])
                        with col2:
                            # Drop duplicates based on target_Id and actual_Id
                            df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            
                            def convert_to_float(series):
                                return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                            # Group and aggregate the data for each metric using unique IDs
                            unique_customer_df = df_target_unique.groupby(['District']).agg(
                                {'Target Unique Customer': 'sum'}).reset_index()
                            actual_unique_customer_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Unique Customer': 'sum'}).reset_index()
                            # Convert decimals to float
                            unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                            actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                            
                            unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='left')

                            # Function to calculate percentage safely
                            def calculate_percentage_unique(row):
                                if row['Target Unique Customer'] == 0:
                                    if row['Actual Unique Customer'] == 0:
                                        return 0 # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)

                            unique_customer_df['Metric'] = 'Unique Customer'

                            account_df = df_target_unique.groupby(['District']).agg(
                                {'Target Number Of Account': 'sum'}).reset_index()
                            actual_account_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Number Of Account': 'sum'}).reset_index()
                            account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                            actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                            account_df = account_df.merge(actual_account_df, on=['District'], how='left')

                            def calculate_percentage_account(row):
                                if row['Target Number Of Account'] == 0:
                                    if row['Actual Number Of Account'] == 0:
                                        return 0  # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                            account_df['Metric'] = 'Number Of Account'

                            disbursed_amount_df = df_target_unique.groupby(['District']).agg(
                                {'Target Disbursed Amount': 'sum'}).reset_index()
                            actual_disbursed_amount_df = df_actual_unique.groupby(['District']).agg(
                                {'Actual Disbursed Amount': 'sum'}).reset_index()
                            # Convert decimals to float
                            disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                            
                            actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                            
                            disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='left')

                            def calculate_percentage_dis(row):
                                if row['Target Disbursed Amount'] == 0:
                                    if row['Actual Disbursed Amount'] == 0:
                                        return np.nan  # Case 1: Both Target and Actual are 0
                                    else:
                                        return np.inf  # Case 2: Target is 0 but Actual is not
                                else:
                                    return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                            # Apply the function to each row
                            disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                            disbursed_amount_df['Metric'] = 'Disbursed Amount'

                            # Rename columns to have consistent names
                            unique_customer_df = unique_customer_df.rename(columns={
                                'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                            account_df = account_df.rename(columns={
                                'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                            disbursed_amount_df = disbursed_amount_df.rename(columns={
                                'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                            # Combine the DataFrames into one
                            combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])
                            # Round the 'Target' and 'Actual' columns to 2 decimal points
                            combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                            combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                            # Format 'Percentage(%)' with a percentage sign
                            combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            # Reset the index and rename it to start from 1
                            combined_df_reset = combined_df.reset_index(drop=True)
                            combined_df_reset.index = combined_df_reset.index + 1

                            # Apply styling
                            def highlight_columns(s):
                                colors = []
                                for val in s:
                                    if isinstance(val, str) and '%' in val:
                                        percentage_value = float(val.strip('%'))
                                        if percentage_value < 50:
                                            colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                        elif 50 <= percentage_value < 70:
                                            colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                        elif percentage_value >= 70:
                                            colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                        else:
                                            colors.append('')
                                    else:
                                        colors.append('')  # no color for other values
                                return colors
                            
                            styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                            .set_properties(**{
                                                                'text-align': 'center'
                                                            }) \
                                                            .set_table_styles([
                                                                dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                            ])
                            # Convert styled DataFrame to HTML
                            styled_html = styled_df.to_html()

                            # Display the result
                            # st.write(f":orange[Michu(Wabi & Guyya), Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                            st.write(
                                    f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef;">{current_month_name}</span>)</span>',
                                    unsafe_allow_html=True
                                )
                            st.write(styled_html, unsafe_allow_html=True)



                            st.write("")
                            st.write("")

                        

                if role == 'Branch User':
                    ccool1, ccool2 = st.columns(2)
                    # with ccool1:
                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_target_unique.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Number Of Account': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()

                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Number Of Account': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Number Of Account': target_grouped['Target Number Of Account'],
                        'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer', 'Number of Accounts'],
                        y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer', 'Number of Accounts'],
                        y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    fig.update_layout(
                        # title='Michu(Wabi & Guyya) YTD(<span style="color: #00adef;">Year-To-Date </span>)',
                        title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date </span>) </span>',
                        xaxis=dict(title='Metrics'),
                        yaxis=dict(
                            title='Unique Customer & Number of Accounts',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)
                        # col1, col2 = st.columns([0.1, 0.9])



                    col11, col22 = st.columns([0.2, 0.8])

                    with col22:
                        # Drop duplicates based on target_Id and actual_Id
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Function to convert decimal.Decimal to float
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                        # Group and aggregate the data for each metric
                        unique_customer_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_unique_customer_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()

                        # Convert decimals to float
                        unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                        actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                        unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='left')

                        # Function to calculate percentage safely
                        def calculate_percentage_unique(row):
                            if row['Target Unique Customer'] == 0:
                                if row['Actual Unique Customer'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                        
                        # unique_customer_df['Percentage(%)'] = (
                        #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                        unique_customer_df['Metric'] = 'Unique Customer'

                        account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Number Of Account': 'sum'}).reset_index()
                        actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Number Of Account': 'sum'}).reset_index()

                        # Convert decimals to float
                        account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                        actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                        account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_account(row):
                            if row['Target Number Of Account'] == 0:
                                if row['Actual Number Of Account'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                        # account_df['Percentage(%)'] = (
                        #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                        account_df['Metric'] = 'Number Of Account'

                        disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()

                        # Convert decimals to float
                        disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                        actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                        disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_dis(row):
                            if row['Target Disbursed Amount'] == 0:
                                if row['Actual Disbursed Amount'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                        # disbursed_amount_df['Percentage(%)'] = (
                        #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                        disbursed_amount_df['Metric'] = 'Disbursed Amount'

                        # Rename columns to have consistent names
                        unique_customer_df = unique_customer_df.rename(columns={
                            'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                        account_df = account_df.rename(columns={
                            'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                        disbursed_amount_df = disbursed_amount_df.rename(columns={
                            'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                        # Combine the DataFrames into one
                        combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])

                        combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                        combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format 'Percentage(%)' with a percentage sign
                        combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Reset the index and rename it to start from 1
                        combined_df_reset = combined_df.reset_index(drop=True)
                        combined_df_reset.index = combined_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                            .set_properties(**{
                                                                'text-align': 'center'
                                                            }) \
                                                            .set_table_styles([
                                                                dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                            ])
                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result
                        # st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                        st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                                unsafe_allow_html=True
                            )
                        # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                        st.write(styled_html, unsafe_allow_html=True)

                        st.write(" ")
                        st.write(" ")
                        st.write(" ")



                    

                        
                    # with ccool1:
                    # Get the current date
                    # current_date = datetime.now().date()

                    # Get the current date
                    current_date = datetime.now().date()

                    # Calculate the start and end date of the current month
                    start_of_month = current_date.replace(day=1)
                    end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                    # Filter the dataframe based on the selected date range
                    df_filtered = df_merged[
                        (df_merged["Target Date"].dt.date >= start_of_month) & 
                        (df_merged["Target Date"].dt.date <= end_of_month)
                    ].copy()

                    df_filtered_actual = df_merged[
                        (df_merged["Actual Date"].dt.date >= start_of_month) & 
                        (df_merged["Actual Date"].dt.date <= end_of_month)
                    ].copy()
                    

                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_target_unique.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Number Of Account': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()

                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Number Of Account': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Number Of Account': target_grouped['Target Number Of Account'],
                        'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer', 'Number of Accounts'],
                        y=[totals['Target Unique Customer'], totals['Target Number Of Account']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer']), format_num(totals['Target Number Of Account'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer', 'Number of Accounts'],
                        y=[totals['Actual Unique Customer'], totals['Actual Number Of Account']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer']), format_num(totals['Actual Number Of Account'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    current_month_name = datetime.now().strftime("%B")
                    fig.update_layout(
                        # title=f'Michu(Wabi & Guyya), Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
                        title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef; text-decoration: underline;">{current_month_name} </span>) </span>',
                        xaxis=dict(title='Metrics'),
                        yaxis=dict(
                            title='Unique Customer & Number of Accounts',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)






                    coll11, coll22 = st.columns([0.2, 0.8])
                    with coll22:
                        # Drop duplicates based on target_Id and actual_Id
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Function to convert decimal.Decimal to float
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                        # Group and aggregate the data for each metric
                        unique_customer_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_unique_customer_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()

                        # Convert decimals to float
                        unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                        actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                        unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='left')
                        def calculate_percentage_unique(row):
                            if row['Target Unique Customer'] == 0:
                                if row['Actual Unique Customer'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                        
                        # unique_customer_df['Percentage(%)'] = (
                        #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                        unique_customer_df['Metric'] = 'Unique Customer'

                        account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Number Of Account': 'sum'}).reset_index()
                        actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Number Of Account': 'sum'}).reset_index()

                        # Convert decimals to float
                        account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                        actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                        account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_account(row):
                            if row['Target Number Of Account'] == 0:
                                if row['Actual Number Of Account'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                        # account_df['Percentage(%)'] = (
                        #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                        account_df['Metric'] = 'Number Of Account'

                        disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()


                        # Convert decimals to float
                        disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                        actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                        disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='left')

                        def calculate_percentage_dis(row):
                            if row['Target Disbursed Amount'] == 0:
                                if row['Actual Disbursed Amount'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                        # disbursed_amount_df['Percentage(%)'] = (
                        #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                        disbursed_amount_df['Metric'] = 'Disbursed Amount'

                        # Rename columns to have consistent names
                        unique_customer_df = unique_customer_df.rename(columns={
                            'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                        account_df = account_df.rename(columns={
                            'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                        disbursed_amount_df = disbursed_amount_df.rename(columns={
                            'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                        # Combine the DataFrames into one
                        combined_df = pd.concat([unique_customer_df, account_df, disbursed_amount_df])

                        combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                        combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format 'Percentage(%)' with a percentage sign
                        combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Reset the index and rename it to start from 1
                        combined_df_reset = combined_df.reset_index(drop=True)
                        combined_df_reset.index = combined_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('') 
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                            .set_properties(**{
                                                                'text-align': 'center'
                                                            }) \
                                                            .set_table_styles([
                                                                dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                            ])
                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result
                        st.write(f":orange[Michu(Wabi & Guyya), Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                        st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef;">{current_month_name}</span>)</span>',
                                unsafe_allow_html=True
                            )
                        # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                        st.write(styled_html, unsafe_allow_html=True)

                        st.write(" ")
                        st.write(" ")
                        st.write(" ")


                
                    
                    # st.write("""
                    #             **Note the following points regarding the Target Performance Report:**

                    #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                                
                    #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                    #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                    #             """)



            except Exception as e:
                st.error(f"An error occurred while loading data: {e}")
            # finally:
            #     if db_instance:
            #         db_instance.close_connection()
            # Auto-refresh interval (in seconds)
            refresh_interval = 600  # 5 minutes
            st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")
    else:
        try:
                
            # tab_options = ["Michu(Wabi & Guyya)", "Michu-Kiyya"]
            # active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
            # if active_tab == "Michu(Wabi & Guyya)":
            dis_branch, df_actual, df_target = load_actual_vs_targetdata_per_product(role, username, fy_start, fy_end)

            # k_dis_branch, k_df_actual, k_df_target = load_kiyya_actual_vs_targetdata(role, username)
            # Get the maximum date of the current month

            
            # Get the current date and the maximum date for the current month
            current_date = datetime.now().date()
            current_month_max_date = current_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
            current_month_max_date = current_month_max_date.date()

            # Convert 'Actual Date' and 'Target Date' columns to datetime
            df_actual['Actual Date'] = pd.to_datetime(df_actual['Actual Date']).dt.date
            df_target['Target Date'] = pd.to_datetime(df_target['Target Date']).dt.date

            # k_df_actual['Actual Date'] = pd.to_datetime(k_df_actual['Actual Date']).dt.date
            # k_df_target['Target Date'] = pd.to_datetime(k_df_target['Target Date']).dt.date

            # Filter df_actual and df_target based on the current month's max date
            df_actual = df_actual[df_actual['Actual Date'] <= current_month_max_date]
            df_target = df_target[df_target['Target Date'] <= current_month_max_date]

            # # Filter df_actual and df_target based on the current month's max date
            # k_df_actual = k_df_actual[k_df_actual['Actual Date'] <= current_month_max_date]
            # k_df_target = k_df_target[k_df_target['Target Date'] <= current_month_max_date]
            # st.write(df_target)

            # Display the filtered DataFrames
            # dis_branch, df_actual, df_target
            merged_acttarg = pd.merge(df_actual, df_target, on=['Branch Code', 'Product Type'], how='outer') 
            # merged_acttarg
                
            df_merged =  pd.merge(dis_branch, merged_acttarg, on='Branch Code', how='right')

            # df_merged

            # # dis_branch, df_actual, df_target
            # k_merged_acttarg = pd.merge(k_df_actual, k_df_target, on='Branch Code', how='outer')
            # k_df_merged =  pd.merge(k_dis_branch, k_merged_acttarg, on='Branch Code', how='inner')

            # Combine unique values for filters
            combined_districts = sorted(set(df_merged["District"].dropna().unique()))
            

            # Sidebar filters
            st.sidebar.image("pages/michu.png")
            # username = st.session_state.get("username", "")
            full_name = st.session_state.get("full_name", "")
            # role = st.session_state.get("role", "")
            # st.sidebar.write(f'Welcome, :orange[{full_name}]')
            st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
            st.sidebar.header("Please filter")

            
            # Get unique product types
            combined_products = sorted(df_merged["Product Type"].dropna().unique())

            # Add a product filter at the top of the page 
            selected_product = st.selectbox("Select Product Type", options=["All"] + combined_products)

            # Apply the product filter if a specific product type is selected
            if selected_product != "All":
                df_merged = df_merged[df_merged["Product Type"] == selected_product]


            # st.write(df_merged)
                
            # role = st.session_state.get("role", "")
            if role == "Admin" or role == "Sales Admin" or role == 'under_admin':

                district = st.sidebar.multiselect("Select District", options=combined_districts)
                

                if not district:
                    df_merged = df_merged.copy()
                    # k_df_merged = k_df_merged.copy()
                else:
                    df_merged = df_merged[df_merged["District"].isin(district)]
                    # k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]

            if role != 'Branch User':
                combined_branches = sorted(set(df_merged["Branch"].dropna().unique()))
                branch = st.sidebar.multiselect("Select Branch", options=combined_branches)

                if not branch:
                    df_merged = df_merged.copy()
                    # k_df_merged = k_df_merged.copy()
                else:
                    df_merged = df_merged[df_merged["Branch"].isin(branch)]
                    # k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                
            if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                if not district and not branch:
                    df_merged = df_merged
                    # k_df_merged = k_df_merged
                    
                elif district:
                    df_merged = df_merged[df_merged["District"].isin(district)]
                    # k_df_merged = k_df_merged[k_df_merged["District"].isin(district)]
                elif branch:
                    df_merged = df_merged[df_merged["Branch"].isin(branch)]
                    # k_df_merged = k_df_merged[k_df_merged["Branch"].isin(branch)]
                else:
                    df_merged = df_merged[df_merged["District"].isin(district) & df_merged["Branch"].isin(branch)]
                    # k_df_merged = k_df_merged[k_df_merged["District"].isin(district) & k_df_merged["Branch"].isin(branch)]

            if df_merged is not None and not df_merged.empty:
                col1, col2 = st.sidebar.columns(2)

                # Convert the date columns to datetime if they are not already
                df_merged["Target Date"] = pd.to_datetime(df_merged["Target Date"], errors='coerce')
                df_merged["Actual Date"] = pd.to_datetime(df_merged["Actual Date"], errors='coerce')

                # # Convert the date columns to datetime if they are not already
                # k_df_merged["Target Date"] = pd.to_datetime(k_df_merged["Target Date"], errors='coerce')
                # k_df_merged["Actual Date"] = pd.to_datetime(k_df_merged["Actual Date"], errors='coerce')

                # Determine the overall min and max dates
                overall_start_date = df_merged[["Target Date", "Actual Date"]].min().min()
                overall_end_date = df_merged[["Target Date", "Actual Date"]].max().max()

                # Sidebar date filters
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        value=overall_start_date.date(),  # Convert to `date` for st.date_input
                        min_value=overall_start_date.date(),
                        max_value=overall_end_date.date(),
                    )

                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=overall_end_date.date(),
                        min_value=overall_start_date.date(),
                        max_value=overall_end_date.date(),
                    )


                # Convert start_date and end_date to datetime for comparison
                start_date = pd.Timestamp(start_date)
                end_date = pd.Timestamp(end_date)

                # Filter the dataframe based on the selected date range
                # df_filtered = df_merged[
                #     (df_merged["Target Date"] >= start_date) & (df_merged["Target Date"] <= end_date)
                # ].copy()

                df_filtered = df_merged[
                    (start_date.to_period("M") <= df_merged["Target Date"].dt.to_period("M")) &
                    (end_date.to_period("M") >= df_merged["Target Date"].dt.to_period("M"))
                ].copy()

                # You can filter Actual Date separately if needed
                df_filtered_actual = df_merged[
                    (df_merged["Actual Date"] >= start_date) & (df_merged["Actual Date"] <= end_date)
                ].copy()


                # k_df_filtered = k_df_merged[
                #     (start_date.to_period("M") <= k_df_merged["Target Date"].dt.to_period("M")) &
                #     (end_date.to_period("M") >= k_df_merged["Target Date"].dt.to_period("M"))
                # ].copy()

                # # You can filter Actual Date separately if needed
                # k_df_filtered_actual = k_df_merged[
                #     (k_df_merged["Actual Date"] >= start_date) & (k_df_merged["Actual Date"] <= end_date)
                # ].copy()



            # Hide the sidebar by default with custom CSS
            hide_sidebar_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                </style>
            """
            st.markdown(hide_sidebar_style, unsafe_allow_html=True)
            if role == "Admin" or role == 'under_admin' or role == 'under_admin':
                home_sidebar()
            else:
                make_sidebar1()

        
            # df_combine
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
            
            # -- for admin and sales admin --

            if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
                tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per District & Branch"])
                # # Drop duplicate target_Id and actual_Id
                # with Tab3:
                #     st.write("""
                #             **Note the following points regarding the Target Performance Report:**

                #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                            
                #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                #             """)

                with tab1:
                    coll1, coll2 = st.columns(2)
                    
                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                    

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_target_unique.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Number Of Account': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()
        
                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Number Of Account': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Number Of Account': target_grouped['Target Number Of Account'],
                        'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Target Unique Customer']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Actual Unique Customer']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    fig.update_layout(
                        title=f'<span style="text-decoration: underline;"> Michu([<span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span>] YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date</span>) </span>',
                        yaxis=dict(
                            title='Unique Customer',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)


                





                    





                    col1,  col2 = st.columns([0.2, 0.8])

                    with col2:
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                        # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Group and aggregate the data for each metric using unique IDs
                        target_grouped = df_target_unique.groupby('District').agg(
                            {'Target Unique Customer': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_grouped = df_actual_unique.groupby('District').agg(
                            {'Actual Unique Customer': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                        # Convert decimal columns to float
                        target_grouped = target_grouped.apply(convert_to_float)
                        actual_grouped = actual_grouped.apply(convert_to_float)
                        # Merge the target and actual data on 'District' to align them
                        merged_df = target_grouped.merge(actual_grouped, on='District', how='outer')
                        

                        # Calculate the aggregated data for each metric
                        aggregated_data = {
                            'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                            'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                            'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                            'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                        }

                        # Calculate 'Percentage(%)' for each metric
                        aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                        # aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                        aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)

                        # Define the metrics
                        metrics = ['Unique Customer', 'Disbursed Amount']

                        # Create a list of dictionaries for final_df
                        final_df_data = []

                        for metric in metrics:
                            target_value = aggregated_data[f'Target {metric}']
                            actual_value = aggregated_data[f'Actual {metric}']
                            percent_value = aggregated_data[f'Percentage(%) {metric}']
                            
                            final_df_data.append({
                                'Target': target_value,
                                'Actual': actual_value,
                                '%': percent_value,
                                'Metric': metric
                            })

                        # Create final_df DataFrame
                        final_df = pd.DataFrame(final_df_data)

                        # Round the 'Target' and 'Actual' columns to two decimal points
                        final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                        final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format '%' with a percentage sign
                        final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                        # Drop rows where '%' is 'nan%'
                        filtered_df = final_df[final_df['%'] != 'nan%']

                        # Reset the index and rename it to start from 1
                        grouped_df_reset = filtered_df.reset_index(drop=True)
                        grouped_df_reset.index = grouped_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    else:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # green color for values 70% and above
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                .set_properties(**{
                                                    'text-align': 'center',
                                                    'font-size': '20px'
                                                }) \
                                                .set_table_styles([
                                                    dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                ])

                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result with custom CSS
                        # st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                        st.write(
                            f'<span style="text-decoration: underline;">Michu([<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                            unsafe_allow_html=True
                        )

                        st.markdown(styled_html, unsafe_allow_html=True)

                        st.write(" ")
                        st.write(" ")
                        st.write(" ")

                

                with tab2:
                    col21, col22 = st.columns([0.1, 0.9])
                    with col22:
                        tab3, tab4 = st.tabs(["Per District", "Per Branch"])
                        
                        # Display combined data in a table
                        
                        with tab3: 
                            col1, col2 = st.columns([0.1, 0.9])
                            with col2:
                                # -- per District --
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Replace None/NaN with zero and convert to float
                                df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)
                                


                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                # Replace all NaN/None values with zero
                                grouped_df = grouped_df.fillna(0)

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                # st.write(":blue[Michu(Wabi & Guyya) Unique Customer] 👇🏻")
                                st.write(
                                    f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Unique Customer</span></span>',
                                    unsafe_allow_html=True
                                )
                                st.write(styled_df)

                            # with col2:
                                
                            #     df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            #     df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            #     # Ensure all numerical values are converted to floats
                            #     df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                            #     df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                            #     # Group and aggregate the data for each metric using unique IDs
                            #     target_grouped = df_target_unique.groupby(['District']).agg(
                            #         {'Target Number Of Account': 'sum'}).reset_index()
                            #     actual_grouped = df_actual_unique.groupby(['District']).agg(
                            #         {'Actual Number Of Account': 'sum'}).reset_index()

                            #     # Merge the target and actual data on 'District' and 'Branch' to align them
                            #     grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                            #     # Replace all NaN/None values with zero
                            #     grouped_df = grouped_df.fillna(0)
                            #     # Create an explicit copy
                            #     # grouped_df.fillna(0, inplace=True)  # Replace None/NaN with 0  

                            #     grouped_df['Percentage(%)'] = grouped_df.apply(
                            #         lambda row: (
                            #             np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                            #             else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                            #             else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                            #         ),
                            #         axis=1
                            #     )

                            #     # # Calculate 'Percentage(%)'
                            #     # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                            #     # Format 'Percentage(%)' with a percentage sign
                            #     grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            #     # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                            #     total_target_number = grouped_df['Target Number Of Account'].sum()
                            #     total_actual_number = grouped_df['Actual Number Of Account'].sum()
                            #     total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                            #     # Create a summary row
                            #     summary_row = pd.DataFrame([{
                            #         'District': 'Total',
                            #         'Target Number Of Account': total_target_number,
                            #         'Actual Number Of Account': total_actual_number,
                            #         'Percentage(%)': f"{total_percentage:.2f}%"
                            #     }])

                            #     # Append the summary row to the grouped DataFrame
                            #     grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            #     grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                            #     grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                            #     # Drop rows where 'Percentage(%)' is 'nan%'
                            #     filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            #     # Reset the index and rename it to start from 1
                            #     grouped_df_reset = filtered_df.reset_index(drop=True)
                            #     grouped_df_reset.index = grouped_df_reset.index + 1

                            #     # Apply styling
                            #     def highlight_columns(s):
                            #         colors = []
                            #         for val in s:
                            #             if isinstance(val, str) and '%' in val:
                            #                 percentage_value = float(val.strip('%'))
                            #                 if percentage_value < 50:
                            #                     colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                            #                 elif 50 <= percentage_value < 70:
                            #                     colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                            #                 elif percentage_value >= 70:
                            #                     colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                            #                 else:
                            #                     colors.append('') 
                            #             else:
                            #                 colors.append('')  # no color for other values
                            #         return colors

                            #     # Define function to highlight the Total row
                            #     def highlight_total_row(s):
                            #         is_total = s['District'] == 'Total'
                            #         return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            #     # Center-align data and apply styling
                            #     styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                            #                                     .apply(highlight_total_row, axis=1)\
                            #                                     .set_properties(**{'text-align': 'center'})

                            #     # Display the result
                            #     # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                            #     st.write(
                            #         f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Number Of Account</span></span>',
                            #         unsafe_allow_html=True
                            #     )
                            #     st.write(styled_df)
                            

                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District'], how='outer')
                                # Replace all NaN/None values with zero
                                grouped_df = grouped_df.fillna(0)

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed != 0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('')
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                st.write(
                                    f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Disbursed Amount</span></span>',
                                    unsafe_allow_html=True
                                )
                                st.write(styled_df)

                    

                        with tab4:
                            col1, col2 = st.columns([0.1, 0.9])
                            # -- per branch --
                            with col2:

                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                                df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)



                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Unique Customer': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Unique Customer': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                                # Replace all NaN/None values with zero
                                grouped_df = grouped_df.fillna(0)
                                # st.write(grouped_df)

                                # # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                                # Calculate Percentage(%)
                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                        else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                        else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                                    ),
                                    axis=1
                                )

                                # # Calculate 'Percentage(%)' and handle division by zero
                                # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                                total_target_unique = grouped_df['Target Unique Customer'].sum()
                                total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                                total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                                
                                # # Handle division by zero
                                # if total_target_unique == 'nan':
                                #     total_percentage = 0
                                # else:
                                #     total_percentage = (total_actual_unique / total_target_unique) * 100

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Unique Customer': total_target_unique,
                                    'Actual Unique Customer': total_actual_unique,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                                grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:.0f}")
                                grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:.0f}")

                                # Reset the index and rename it to start from 1

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                                
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1
                                # st.markdown("""
                                # <style>
                                #     [data-testid="stElementToolbar"] {
                                #     display: none;
                                #     }
                                # </style>
                                # """, unsafe_allow_html=True)

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                # st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                                st.write(
                                    f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Unique Customer</span></span>',
                                    unsafe_allow_html=True
                                )
                                st.write(styled_df)



                            # with col2:
                            #     # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                            #     # # Ensure all numerical values are converted to floats
                            #     # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                            #     # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                                
                            #     df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                            #     df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                            #     # Ensure all numerical values are converted to floats
                            #     df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                            #     df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                            #     # Group and aggregate the data for each metric using unique IDs
                            #     target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                            #         {'Target Number Of Account': 'sum'}).reset_index()
                            #     actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                            #         {'Actual Number Of Account': 'sum'}).reset_index()

                            #     # Merge the target and actual data on 'District' and 'Branch' to align them
                            #     grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                            #     # Replace all NaN/None values with zero
                            #     grouped_df = grouped_df.fillna(0)

                            #     grouped_df['Percentage(%)'] = grouped_df.apply(
                            #         lambda row: (
                            #             np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                            #             else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                            #             else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                            #         ),
                            #         axis=1
                            #     )

                            #     # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                            #     #     grouped_df['Target Number Of Account'].replace(0, np.nan)
                            #     # ) * 100


                            #     # # Calculate 'Percentage(%)'
                            #     # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                            #     # Format 'Percentage(%)' with a percentage sign
                            #     grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                            #     # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                                
                            #     total_target_number = grouped_df['Target Number Of Account'].sum()
                            #     total_actual_number = grouped_df['Actual Number Of Account'].sum()
                            #     total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number != 0 else 0
                                

                            #     # Create a summary row
                            #     summary_row = pd.DataFrame([{
                            #         'District': 'Total',
                            #         'Branch': '',
                            #         'Target Number Of Account': total_target_number,
                            #         'Actual Number Of Account': total_actual_number,
                            #         'Percentage(%)': f"{total_percentage:.2f}%"
                            #     }])

                            #     # Append the summary row to the grouped DataFrame
                            #     grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                            #     grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:.0f}")
                            #     grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:.0f}")

                            #     # Drop rows where 'Percentage(%)' is 'nan%'
                            #     filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                            #     # Reset the index and rename it to start from 1
                            #     grouped_df_reset = filtered_df.reset_index(drop=True)
                            #     grouped_df_reset.index = grouped_df_reset.index + 1

                            #     # Apply styling
                            #     def highlight_columns(s):
                            #         colors = []
                            #         for val in s:
                            #             if isinstance(val, str) and '%' in val:
                            #                 percentage_value = float(val.strip('%'))
                            #                 if percentage_value < 50:
                            #                     colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                            #                 elif 50 <= percentage_value < 70:
                            #                     colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                            #                 elif percentage_value >= 70:
                            #                     colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                            #                 else:
                            #                     colors.append('') 
                            #             else:
                            #                 colors.append('')  # no color for other values
                            #         return colors

                            #     # Define function to highlight the Total row
                            #     def highlight_total_row(s):
                            #         is_total = s['District'] == 'Total'
                            #         return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                            #     # Center-align data and apply styling
                            #     styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                            #                                     .apply(highlight_total_row, axis=1)\
                            #                                     .set_properties(**{'text-align': 'center'})

                            #     # Display the result
                            #     # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                            #     st.write(
                            #         f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Number Of Account</span></span>',
                            #         unsafe_allow_html=True
                            #     )
                            #     st.write(styled_df)



                            with col2:
                                # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                                # Ensure all numerical values are converted to floats
                                df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                                df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                                # Group and aggregate the data for each metric using unique IDs
                                target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                                    {'Target Disbursed Amount': 'sum'}).reset_index()
                                actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                                    {'Actual Disbursed Amount': 'sum'}).reset_index()

                                # Merge the target and actual data on 'District' and 'Branch' to align them
                                grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                                # Replace all NaN/None values with zero
                                grouped_df = grouped_df.fillna(0)

                                grouped_df['Percentage(%)'] = grouped_df.apply(
                                    lambda row: (
                                        np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                        else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                        else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                                    ),
                                    axis=1
                                )

                                # Calculate 'Percentage(%)'
                                # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                                # Format 'Percentage(%)' with a percentage sign
                                grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                                # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                                total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                                total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                                total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                                # Create a summary row
                                summary_row = pd.DataFrame([{
                                    'District': 'Total',
                                    'Branch': '',
                                    'Target Disbursed Amount': total_target_disbursed,
                                    'Actual Disbursed Amount': total_actual_disbursed,
                                    'Percentage(%)': f"{total_percentage:.2f}%"
                                }])

                                # Append the summary row to the grouped DataFrame
                                grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                                # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                                grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                                grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                                # Drop rows where 'Percentage(%)' is 'nan%'
                                filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                                # Reset the index and rename it to start from 1
                                grouped_df_reset = filtered_df.reset_index(drop=True)
                                grouped_df_reset.index = grouped_df_reset.index + 1

                                # Apply styling
                                def highlight_columns(s):
                                    colors = []
                                    for val in s:
                                        if isinstance(val, str) and '%' in val:
                                            percentage_value = float(val.strip('%'))
                                            if percentage_value < 50:
                                                colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                            elif 50 <= percentage_value < 70:
                                                colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                            elif percentage_value >= 70:
                                                colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                            else:
                                                colors.append('') 
                                        else:
                                            colors.append('')  # no color for other values
                                    return colors

                                # Define function to highlight the Total row
                                def highlight_total_row(s):
                                    is_total = s['District'] == 'Total'
                                    return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                                # Center-align data and apply styling
                                styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                                .apply(highlight_total_row, axis=1)\
                                                                .set_properties(**{'text-align': 'center'})

                                # Display the result
                                # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount] 👇🏻")
                                st.write(
                                    f'<span style="text-decoration: underline;">Michu[<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] <span style="color: #00adef;">Disbursed Amount</span></span>',
                                    unsafe_allow_html=True
                                )
                                st.write(styled_df)

                        


                with tab1:
                    col1, col2 = st.columns([0.5, 0.5])
                    # with col1:
                    # Get the current date
                    current_date = datetime.now().date()

                    # Calculate the start and end date of the current month
                    start_of_month = current_date.replace(day=1)
                    end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                    # Filter the dataframe based on the selected date range
                    df_filtered = df_merged[
                        (df_merged["Target Date"].dt.date >= start_of_month) & 
                        (df_merged["Target Date"].dt.date <= end_of_month)
                    ].copy()

                    df_filtered_actual = df_merged[
                        (df_merged["Actual Date"].dt.date >= start_of_month) & 
                        (df_merged["Actual Date"].dt.date <= end_of_month)
                    ].copy()

                    # Drop duplicates before aggregating if needed (optional)
                    df_filtered = df_filtered.drop_duplicates(subset='target_Id')
                    df_filtered_actual = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_filtered.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()
        
                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_filtered_actual.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Target Unique Customer']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Actual Unique Customer']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    fig.update_layout(
                        # title='Michu(Wabi & Guyya) MTD (<span style="color: #00adef;">Month-To-Date </span>)',
                        title=f'<span style="text-decoration: underline;"> Michu([<span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span>] MTD (<span style="color: #00adef; text-decoration: underline;">Month-To-Date</span>) </span>',
                        xaxis=dict(title='Metrics'),
                        yaxis=dict(
                            title='Unique Customer',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)

                        
                    c0ll12, coll22 = st.columns([0.2, 0.8])
                    with coll22:
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
                        # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Group and aggregate the data for each metric using unique IDs
                        target_grouped = df_target_unique.groupby('District').agg(
                            {'Target Unique Customer': 'sum', 'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_grouped = df_actual_unique.groupby('District').agg(
                            {'Actual Unique Customer': 'sum', 'Actual Disbursed Amount': 'sum'}).reset_index()
                        # Convert decimal columns to float
                        target_grouped = target_grouped.apply(convert_to_float)
                        actual_grouped = actual_grouped.apply(convert_to_float)
                        # Merge the target and actual data on 'District' to align them
                        merged_df = target_grouped.merge(actual_grouped, on='District', how='left')
                        

                        # Calculate the aggregated data for each metric
                        aggregated_data = {
                            'Target Unique Customer': merged_df['Target Unique Customer'].sum(),
                            'Actual Unique Customer': merged_df['Actual Unique Customer'].sum(),
                            'Target Disbursed Amount': merged_df['Target Disbursed Amount'].sum(),
                            'Actual Disbursed Amount': merged_df['Actual Disbursed Amount'].sum()
                        }

                        # Calculate 'Percentage(%)' for each metric
                        aggregated_data['Percentage(%) Unique Customer'] = (aggregated_data['Actual Unique Customer'] / aggregated_data['Target Unique Customer'] * 100 if aggregated_data['Target Unique Customer'] != 0 else 0)
                        # aggregated_data['Percentage(%) Number Of Account'] = (aggregated_data['Actual Number Of Account'] / aggregated_data['Target Number Of Account'] * 100 if aggregated_data['Target Number Of Account'] != 0 else 0)
                        aggregated_data['Percentage(%) Disbursed Amount'] = (aggregated_data['Actual Disbursed Amount'] / aggregated_data['Target Disbursed Amount'] * 100 if aggregated_data['Target Disbursed Amount'] != 0 else 0)


                        # Define the metrics
                        metrics = ['Unique Customer', 'Disbursed Amount']

                        # Create a list of dictionaries for final_df
                        final_df_data = []

                        for metric in metrics:
                            target_value = aggregated_data[f'Target {metric}']
                            actual_value = aggregated_data[f'Actual {metric}']
                            percent_value = aggregated_data[f'Percentage(%) {metric}']
                            
                            final_df_data.append({
                                'Target': target_value,
                                'Actual': actual_value,
                                '%': percent_value,
                                'Metric': metric
                            })

                        # Create final_df DataFrame
                        final_df = pd.DataFrame(final_df_data)

                        # Round the 'Target' and 'Actual' columns to two decimal points
                        final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                        final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format '%' with a percentage sign
                        final_df['%'] = final_df['%'].map(lambda x: f"{x:.2f}%")
                        # Drop rows where '%' is 'nan%'
                        filtered_df = final_df[final_df['%'] != 'nan%']

                        # Reset the index and rename it to start from 1
                        grouped_df_reset = filtered_df.reset_index(drop=True)
                        grouped_df_reset.index = grouped_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0) \
                                                .set_properties(**{
                                                    'text-align': 'center',
                                                    'font-size': '20px'
                                                }) \
                                                .set_table_styles([
                                                    dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                ])

                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result with custom CSS
                        # st.write(":orange[Michu(Wabi & Guyya) MTD] (:blue[Month-To-Date]) 👇🏻")
                        st.write(
                                f'<span style="text-decoration: underline;">Michu([<span style="color: #e38524; font-size: 20px;">{selected_product}</span>] MTD (<span style="color: #00adef;">Month-To-Date</span>)</span>',
                                unsafe_allow_html=True
                            )
                        
                        st.markdown(styled_html, unsafe_allow_html=True)

                        st.write(" ")
                        st.write(" ")
                        st.write(" ")

                        


                        
            # -- for role District User --

            if role == 'District User':
                tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per Branch"])
                # # Drop duplicate target_Id and actual_Id
                # with Tab31:
                #     st.write("""
                #             **Note the following points regarding the Target Performance Report:**

                #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                            
                #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                #             """)
                with tab1:
                    
                    # with cool1:
                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_target_unique.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()
        
                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Target Unique Customer']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Actual Unique Customer']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    fig.update_layout(
                        # title='Michu(Wabi & Guyya) YTD (<span style="color: #00adef;">Year-To-Date </span>)',
                        title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date </span>) </span>',
                        xaxis=dict(title='Metrics'),
                        yaxis=dict(
                            title='Unique Customer',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)


                    cool1, cool2 = st.columns([0.2, 0.8])
                    with cool2:
                        # Drop duplicates based on target_Id and actual_Id
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                        # Group and aggregate the data for each metric using unique IDs
                        unique_customer_df = df_target_unique.groupby(['District']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_unique_customer_df = df_actual_unique.groupby(['District']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()
                        # Convert decimals to float
                        unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                        actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                        
                        unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='left')

                        unique_customer_df['Percentage(%)'] = (
                            (unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100).round(0)
                        unique_customer_df['Metric'] = 'Unique Customer'

                        # account_df = df_target_unique.groupby(['District']).agg(
                        #     {'Target Number Of Account': 'sum'}).reset_index()
                        # actual_account_df = df_actual_unique.groupby(['District']).agg(
                        #     {'Actual Number Of Account': 'sum'}).reset_index()
                        # account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                        # actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                        # account_df = account_df.merge(actual_account_df, on=['District'], how='left')
                        # account_df['Percentage(%)'] = (
                        #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                        # account_df['Metric'] = 'Number Of Account'

                        disbursed_amount_df = df_target_unique.groupby(['District']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_disbursed_amount_df = df_actual_unique.groupby(['District']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()
                        # Convert decimals to float
                        disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                        
                        actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                        
                        disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='left')
                        disbursed_amount_df['Percentage(%)'] = (
                            disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                        disbursed_amount_df['Metric'] = 'Disbursed Amount'

                        # Rename columns to have consistent names
                        unique_customer_df = unique_customer_df.rename(columns={
                            'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                        # account_df = account_df.rename(columns={
                        #     'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                        disbursed_amount_df = disbursed_amount_df.rename(columns={
                            'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                        # Combine the DataFrames into one
                        combined_df = pd.concat([unique_customer_df, disbursed_amount_df])
                        # Round the 'Target' and 'Actual' columns to 2 decimal points
                        combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                        combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format 'Percentage(%)' with a percentage sign
                        combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Reset the index and rename it to start from 1
                        combined_df_reset = combined_df.reset_index(drop=True)
                        combined_df_reset.index = combined_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors
                        
                        styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                        .set_properties(**{
                                                            'text-align': 'center'
                                                        }) \
                                                        .set_table_styles([
                                                            dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                        ])
                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result
                        # st.write(":orange[Target vs Actual YTD] (:blue[Year-To-Date]) 👇🏻")
                        st.write(
                            f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                            unsafe_allow_html=True
                        )
                        st.write(styled_html, unsafe_allow_html=True)



                        st.write("")
                        st.write("")

                        




                with tab2:
                    colll1, colll2 = st.columns([0.1, 0.9])
                    # Display combined data in a table
                    with colll2:
                        # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Ensure all numerical values are converted to floats
                        df_target_unique.loc[:,'Target Unique Customer'] = df_target_unique['Target Unique Customer'].astype(float)
                        df_actual_unique.loc[:,'Actual Unique Customer'] = df_actual_unique['Actual Unique Customer'].astype(float)

                        # Group and aggregate the data for each metric using unique IDs
                        target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()

                        # Merge the target and actual data on 'District' and 'Branch' to align them
                        grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                        # grouped_df
                        grouped_df = grouped_df.fillna(0)

                        # # Calculate 'Percentage(%)'
                        # grouped_df['Percentage(%)'] = (grouped_df['Actual Unique Customer'] / grouped_df['Target Unique Customer']) * 100
                        # Calculate Percentage(%)
                        grouped_df['Percentage(%)'] = grouped_df.apply(
                            lambda row: (
                                np.nan if row['Actual Unique Customer'] == 0 and row['Target Unique Customer'] == 0
                                else np.inf if row['Target Unique Customer'] == 0 and row['Actual Unique Customer'] != 0
                                else (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100
                            ),
                            axis=1
                        )

                        # # Calculate 'Percentage(%)' and handle division by zero
                        # grouped_df['Percentage(%)'] = grouped_df.apply(lambda row: (row['Actual Unique Customer'] / row['Target Unique Customer'] * 100) if row['Target Unique Customer'] != 0 else 0, axis=1)


                        # Format 'Percentage(%)' with a percentage sign
                        grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Calculate the totals for 'Target Unique Customer' and 'Actual Unique Customer'
                        total_target_unique = grouped_df['Target Unique Customer'].sum()
                        total_actual_unique = grouped_df['Actual Unique Customer'].sum()
                        total_percentage = (total_actual_unique / total_target_unique) * 100 if total_target_unique != 0 else 0
                        
                        # # Handle division by zero
                        # if total_target_unique == 'nan':
                        #     total_percentage = 0
                        # else:
                        #     total_percentage = (total_actual_unique / total_target_unique) * 100

                        # Create a summary row
                        summary_row = pd.DataFrame([{
                            'District': 'Total',
                            'Branch': '',
                            'Target Unique Customer': total_target_unique,
                            'Actual Unique Customer': total_actual_unique,
                            'Percentage(%)': f"{total_percentage:.2f}%"
                        }])

                        

                        # Append the summary row to the grouped DataFrame
                        grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                        grouped_df['Target Unique Customer'] = grouped_df['Target Unique Customer'].map(lambda x: f"{x:,.0f}")
                        grouped_df['Actual Unique Customer'] = grouped_df['Actual Unique Customer'].map(lambda x: f"{x:,.0f}")

                        # Reset the index and rename it to start from 1

                        # Drop rows where 'Percentage(%)' is 'nan%'
                        filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']
                        
                        grouped_df_reset = filtered_df.reset_index(drop=True)
                        grouped_df_reset.index = grouped_df_reset.index + 1
                        # st.markdown("""
                        # <style>
                        #     [data-testid="stElementToolbar"] {
                        #     display: none;
                        #     }
                        # </style>
                        # """, unsafe_allow_html=True)

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        # Define function to highlight the Total row
                        def highlight_total_row(s):
                            is_total = s['District'] == 'Total'
                            return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                        # Center-align data and apply styling
                        styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                        .apply(highlight_total_row, axis=1)\
                                                        .set_properties(**{'text-align': 'center'})

                        # Display the result
                        # st.write(":blue[Michu(Wabi & Guyya) Unique Customer]  👇🏻")
                        st.write(
                            f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Unique Customer</span></span>',
                            unsafe_allow_html=True
                        )
                        st.write(styled_df)



                    # with colll2:
                    #     # # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                    #     # # Ensure all numerical values are converted to floats
                    #     # df_merged['Target Number Of Account'] = df_merged['Target Number Of Account'].astype(float)
                    #     # df_merged['Actual Number Of Account'] = df_merged['Actual Number Of Account'].astype(float)

                        
                    #     df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    #     df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    #     # Ensure all numerical values are converted to floats
                    #     df_target_unique.loc[:,'Target Number Of Account'] = df_target_unique['Target Number Of Account'].astype(float)
                    #     df_actual_unique.loc[:,'Actual Number Of Account'] = df_actual_unique['Actual Number Of Account'].astype(float)

                    #     # Group and aggregate the data for each metric using unique IDs
                    #     target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                    #         {'Target Number Of Account': 'sum'}).reset_index()
                    #     actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                    #         {'Actual Number Of Account': 'sum'}).reset_index()

                    #     # Merge the target and actual data on 'District' and 'Branch' to align them
                    #     grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                    #     grouped_df = grouped_df.fillna(0)

                    #     grouped_df['Percentage(%)'] = grouped_df.apply(
                    #             lambda row: (
                    #                 np.nan if row['Actual Number Of Account'] == 0 and row['Target Number Of Account'] == 0
                    #                 else np.inf if row['Target Number Of Account'] == 0 and row['Actual Number Of Account'] != 0
                    #                 else (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100
                    #             ),
                    #             axis=1
                    #         )

                    #     # grouped_df['Percentage(%)'] = grouped_df['Actual Number Of Account'].div(
                    #     #         grouped_df['Target Number Of Account'].replace(0, np.nan)
                    #     #     ) * 100

                    #     # # Calculate 'Percentage(%)'
                    #     # grouped_df['Percentage(%)'] = (grouped_df['Actual Number Of Account'] / grouped_df['Target Number Of Account']) * 100

                    #     # Format 'Percentage(%)' with a percentage sign
                    #     grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                    #     # Calculate the totals for 'Target Number Of Account' and 'Actual Number Of Account'
                        
                    #     total_target_number = grouped_df['Target Number Of Account'].sum()
                    #     total_actual_number = grouped_df['Actual Number Of Account'].sum()
                    #     total_percentage = (total_actual_number / total_target_number) * 100 if total_target_number !=0 else 0
                        

                    #     # Create a summary row
                    #     summary_row = pd.DataFrame([{
                    #         'District': 'Total',
                    #         'Branch': '',
                    #         'Target Number Of Account': total_target_number,
                    #         'Actual Number Of Account': total_actual_number,
                    #         'Percentage(%)': f"{total_percentage:.2f}%"
                    #     }])

                    #     # Append the summary row to the grouped DataFrame
                    #     grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)
                    #     grouped_df['Target Number Of Account'] = grouped_df['Target Number Of Account'].map(lambda x: f"{x:,.0f}")
                    #     grouped_df['Actual Number Of Account'] = grouped_df['Actual Number Of Account'].map(lambda x: f"{x:,.0f}")

                    #     # Drop rows where 'Percentage(%)' is 'nan%'
                    #     filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                    #     # Reset the index and rename it to start from 1
                    #     grouped_df_reset = filtered_df.reset_index(drop=True)
                    #     grouped_df_reset.index = grouped_df_reset.index + 1

                    #     # Apply styling
                    #     def highlight_columns(s):
                    #         colors = []
                    #         for val in s:
                    #             if isinstance(val, str) and '%' in val:
                    #                 percentage_value = float(val.strip('%'))
                    #                 if percentage_value < 50:
                    #                     colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                    #                 elif 50 <= percentage_value < 70:
                    #                     colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                    #                 elif percentage_value >= 70:
                    #                     colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                    #                 else:
                    #                     colors.append('') 
                    #             else:
                    #                 colors.append('')  # no color for other values
                    #         return colors

                    #     # Define function to highlight the Total row
                    #     def highlight_total_row(s):
                    #         is_total = s['District'] == 'Total'
                    #         return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                    #     # Center-align data and apply styling
                    #     styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                    #                                     .apply(highlight_total_row, axis=1)\
                    #                                     .set_properties(**{'text-align': 'center'})

                    #     # Display the result
                    #     # st.write(":blue[Michu(Wabi & Guyya) Number Of Account]  👇🏻")
                    #     st.write(
                    #         f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Number Of Account</span></span>',
                    #         unsafe_allow_html=True
                    #     )
                    #     st.write(styled_df)



                    with colll2:
                        # Drop duplicates based on target_Id and actual_Id to ensure unique IDs for summation
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        # Ensure all numerical values are converted to floats
                        df_target_unique.loc[:,'Target Disbursed Amount'] = df_target_unique['Target Disbursed Amount'].astype(float)
                        df_actual_unique.loc[:,'Actual Disbursed Amount'] = df_actual_unique['Actual Disbursed Amount'].astype(float)

                        # Group and aggregate the data for each metric using unique IDs
                        target_grouped = df_target_unique.groupby(['District', 'Branch']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_grouped = df_actual_unique.groupby(['District', 'Branch']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()

                        # Merge the target and actual data on 'District' and 'Branch' to align them
                        grouped_df = target_grouped.merge(actual_grouped, on=['District', 'Branch'], how='outer')
                        grouped_df = grouped_df.fillna(0)

                        grouped_df['Percentage(%)'] = grouped_df.apply(
                            lambda row: (
                                np.nan if row['Actual Disbursed Amount'] == 0 and row['Target Disbursed Amount'] == 0
                                else np.inf if row['Target Disbursed Amount'] == 0 and row['Actual Disbursed Amount'] != 0
                                else (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100
                            ),
                            axis=1
                        )

                        # Calculate 'Percentage(%)'
                        # grouped_df['Percentage(%)'] = (grouped_df['Actual Disbursed Amount'] / grouped_df['Target Disbursed Amount']) * 100

                        # Format 'Percentage(%)' with a percentage sign
                        grouped_df['Percentage(%)'] = grouped_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Calculate the totals for 'Target Disbursed Amount' and 'Actual Disbursed Amount'
                        total_target_disbursed = grouped_df['Target Disbursed Amount'].sum()
                        total_actual_disbursed = grouped_df['Actual Disbursed Amount'].sum()
                        total_percentage = (total_actual_disbursed / total_target_disbursed) * 100 if total_target_disbursed !=0 else 0

                        # Create a summary row
                        summary_row = pd.DataFrame([{
                            'District': 'Total',
                            'Branch': '',
                            'Target Disbursed Amount': total_target_disbursed,
                            'Actual Disbursed Amount': total_actual_disbursed,
                            'Percentage(%)': f"{total_percentage:.2f}%"
                        }])

                        # Append the summary row to the grouped DataFrame
                        grouped_df = pd.concat([grouped_df, summary_row], ignore_index=True)

                        # Format 'Target Disbursed Amount' and 'Actual Disbursed Amount' to no decimal places
                        grouped_df['Target Disbursed Amount'] = grouped_df['Target Disbursed Amount'].map(lambda x: f"{x:,.0f}")
                        grouped_df['Actual Disbursed Amount'] = grouped_df['Actual Disbursed Amount'].map(lambda x: f"{x:,.0f}")

                        # Drop rows where 'Percentage(%)' is 'nan%'
                        filtered_df = grouped_df[grouped_df['Percentage(%)'] != 'nan%']

                        # Reset the index and rename it to start from 1
                        grouped_df_reset = filtered_df.reset_index(drop=True)
                        grouped_df_reset.index = grouped_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors

                        # Define function to highlight the Total row
                        def highlight_total_row(s):
                            is_total = s['District'] == 'Total'
                            return ['background-color: #00adef; text-align: center' if is_total else 'text-align: center' for _ in s]

                        # Center-align data and apply styling
                        styled_df = grouped_df_reset.style.apply(highlight_columns, axis=0)\
                                                        .apply(highlight_total_row, axis=1)\
                                                        .set_properties(**{'text-align': 'center'})

                        # Display the result
                        # st.write(":blue[Michu(Wabi & Guyya) Disbursed Amount]  👇🏻")
                        st.write(
                            f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product <span style="color: #00adef;">Disbursed Amount</span></span>',
                            unsafe_allow_html=True
                        )
                        st.write(styled_df)

                    # Michu-Kiyya


                



                with tab1:
                    ccol1, ccol2 = st.columns(2)
                    # with ccol1:
                    # Get the current date
                    current_date = datetime.now().date()

                    # Calculate the start and end date of the current month
                    start_of_month = current_date.replace(day=1)
                    end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                    # Filter the dataframe based on the selected date range
                    df_filtered = df_merged[
                        (df_merged["Target Date"].dt.date >= start_of_month) & 
                        (df_merged["Target Date"].dt.date <= end_of_month)
                    ].copy()

                    df_filtered_actual = df_merged[
                        (df_merged["Actual Date"].dt.date >= start_of_month) & 
                        (df_merged["Actual Date"].dt.date <= end_of_month)
                    ].copy()

                    # Drop duplicates before aggregating if needed (optional)
                    df_filtered = df_filtered.drop_duplicates(subset='target_Id')
                    df_filtered_actual = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    
                    # Group by unique target_Id and sum the target columns
                    target_grouped = df_filtered.groupby('target_Id').agg({
                        'Target Unique Customer': 'sum',
                        'Target Disbursed Amount': 'sum'
                    }).sum()
        
                    # Group by unique actual_Id and sum the actual columns
                    actual_grouped = df_filtered_actual.groupby('actual_Id').agg({
                        'Actual Unique Customer': 'sum',
                        'Actual Disbursed Amount': 'sum'
                    }).sum()
                    # Aggregate the data to get total values
                    
                    totals = {
                        'Target Unique Customer': target_grouped['Target Unique Customer'],
                        'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                        'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                        'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                    }

                    # Create the bar chart
                    fig = go.Figure()

                    # Add bars for Unique Customer and Number of Accounts
                    def format_num(num):
                        return f"{num:,.0f}"
                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Target Unique Customer']],
                        name='Target',
                        marker_color= '#00adef',
                        yaxis='y1',
                        text=[format_num(totals['Target Unique Customer'])],
                        textposition='outside'
                    ))

                    fig.add_trace(go.Bar(
                        x=['Unique Customer'],
                        y=[totals['Actual Unique Customer']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y1',
                        text=[format_num(totals['Actual Unique Customer'])],
                        textposition='outside'
                    ))

                    # Add bars for Disbursed Amount on secondary y-axis
                    # Function to format numbers with commas
                    def format_number(num):
                        if num >= 1_000_000:
                            return f"{num / 1_000_000:,.2f}M"
                        return f"{num:,.2f}"
                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Target Disbursed Amount']],
                        name='Target',
                        marker_color='#00adef',
                        yaxis='y2',
                        text=[format_number(totals['Target Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    fig.add_trace(go.Bar(
                        x=['Disbursed Amount'],
                        y=[totals['Actual Disbursed Amount']],
                        name='Actual',
                        marker_color='#e38524',
                        yaxis='y2',
                        text=[format_number(totals['Actual Disbursed Amount'])],
                        textposition='outside',
                        showlegend=False
                    ))

                    # Update the layout for better visualization
                    current_month_name = datetime.now().strftime("%B")
                    fig.update_layout(
                        # title=f'Michu(Wabi & Guyya), Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
                        
                        title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef; text-decoration: underline;">{current_month_name} </span>) </span>',
                        xaxis=dict(title='Metrics'),
                        yaxis=dict(
                            title='Unique Customer',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                        ),
                        yaxis2=dict(
                            title='Disbursed Amount',
                            titlefont=dict(color='black'),
                            tickfont=dict(color='black'),
                            anchor='free',
                            overlaying='y',
                            side='right',
                            position=1
                        ),
                        barmode='group',  # Group the bars side by side
                        bargap=0.2,  # Gap between bars of adjacent location coordinates
                        bargroupgap=0.1, # Gap between bars of the same location coordinate
                        margin=dict(t=80),
                        # legend=dict(
                        # title='Legend',
                        # itemsizing='constant'
                        # )
                    )

                    # Display the chart in Streamlit
                    # st.write("### Michu - Target vs Actual Comparison")
                    st.plotly_chart(fig, use_container_width=True)


                    col1, col2 = st.columns([0.2, 0.8])
                    with col2:
                        # Drop duplicates based on target_Id and actual_Id
                        df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                        df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                        
                        def convert_to_float(series):
                            return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                        # Group and aggregate the data for each metric using unique IDs
                        unique_customer_df = df_target_unique.groupby(['District']).agg(
                            {'Target Unique Customer': 'sum'}).reset_index()
                        actual_unique_customer_df = df_actual_unique.groupby(['District']).agg(
                            {'Actual Unique Customer': 'sum'}).reset_index()
                        # Convert decimals to float
                        unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                        actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])
                        
                        unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='left')

                        # Function to calculate percentage safely
                        def calculate_percentage_unique(row):
                            if row['Target Unique Customer'] == 0:
                                if row['Actual Unique Customer'] == 0:
                                    return 0 # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)

                        unique_customer_df['Metric'] = 'Unique Customer'

                        # account_df = df_target_unique.groupby(['District']).agg(
                        #     {'Target Number Of Account': 'sum'}).reset_index()
                        # actual_account_df = df_actual_unique.groupby(['District']).agg(
                        #     {'Actual Number Of Account': 'sum'}).reset_index()
                        # account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                        # actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                        # account_df = account_df.merge(actual_account_df, on=['District'], how='left')

                        # def calculate_percentage_account(row):
                        #     if row['Target Number Of Account'] == 0:
                        #         if row['Actual Number Of Account'] == 0:
                        #             return 0  # Case 1: Both Target and Actual are 0
                        #         else:
                        #             return np.inf  # Case 2: Target is 0 but Actual is not
                        #     else:
                        #         return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                        # # Apply the function to each row
                        # account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                        # account_df['Metric'] = 'Number Of Account'

                        disbursed_amount_df = df_target_unique.groupby(['District']).agg(
                            {'Target Disbursed Amount': 'sum'}).reset_index()
                        actual_disbursed_amount_df = df_actual_unique.groupby(['District']).agg(
                            {'Actual Disbursed Amount': 'sum'}).reset_index()
                        # Convert decimals to float
                        disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                        
                        actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])
                        
                        disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='left')

                        def calculate_percentage_dis(row):
                            if row['Target Disbursed Amount'] == 0:
                                if row['Actual Disbursed Amount'] == 0:
                                    return np.nan  # Case 1: Both Target and Actual are 0
                                else:
                                    return np.inf  # Case 2: Target is 0 but Actual is not
                            else:
                                return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                        # Apply the function to each row
                        disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                        disbursed_amount_df['Metric'] = 'Disbursed Amount'

                        # Rename columns to have consistent names
                        unique_customer_df = unique_customer_df.rename(columns={
                            'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                        # account_df = account_df.rename(columns={
                        #     'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                        disbursed_amount_df = disbursed_amount_df.rename(columns={
                            'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                        # Combine the DataFrames into one
                        combined_df = pd.concat([unique_customer_df, disbursed_amount_df])
                        # Round the 'Target' and 'Actual' columns to 2 decimal points
                        combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                        combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                        # Format 'Percentage(%)' with a percentage sign
                        combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                        # Reset the index and rename it to start from 1
                        combined_df_reset = combined_df.reset_index(drop=True)
                        combined_df_reset.index = combined_df_reset.index + 1

                        # Apply styling
                        def highlight_columns(s):
                            colors = []
                            for val in s:
                                if isinstance(val, str) and '%' in val:
                                    percentage_value = float(val.strip('%'))
                                    if percentage_value < 50:
                                        colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                    elif 50 <= percentage_value < 70:
                                        colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                    elif percentage_value >= 70:
                                        colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                    else:
                                        colors.append('')
                                else:
                                    colors.append('')  # no color for other values
                            return colors
                        
                        styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                        .set_properties(**{
                                                            'text-align': 'center'
                                                        }) \
                                                        .set_table_styles([
                                                            dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                        ])
                        # Convert styled DataFrame to HTML
                        styled_html = styled_df.to_html()

                        # Display the result
                        # st.write(f":orange[Michu(Wabi & Guyya), Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                        st.write(
                                f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef;">{current_month_name}</span>)</span>',
                                unsafe_allow_html=True
                            )
                        st.write(styled_html, unsafe_allow_html=True)



                        st.write("")
                        st.write("")

                    

            if role == 'Branch User':
                ccool1, ccool2 = st.columns(2)
                # with ccool1:
                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                
                # Group by unique target_Id and sum the target columns
                target_grouped = df_target_unique.groupby('target_Id').agg({
                    'Target Unique Customer': 'sum',
                    'Target Disbursed Amount': 'sum'
                }).sum()

                # Group by unique actual_Id and sum the actual columns
                actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                    'Actual Unique Customer': 'sum',
                    'Actual Disbursed Amount': 'sum'
                }).sum()
                # Aggregate the data to get total values
                
                totals = {
                    'Target Unique Customer': target_grouped['Target Unique Customer'],
                    'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                    'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                    'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                }

                # Create the bar chart
                fig = go.Figure()

                # Add bars for Unique Customer and Number of Accounts
                def format_num(num):
                    return f"{num:,.0f}"
                fig.add_trace(go.Bar(
                    x=['Unique Customer'],
                    y=[totals['Target Unique Customer']],
                    name='Target',
                    marker_color= '#00adef',
                    yaxis='y1',
                    text=[format_num(totals['Target Unique Customer'])],
                    textposition='outside'
                ))

                fig.add_trace(go.Bar(
                    x=['Unique Customer'],
                    y=[totals['Actual Unique Customer']],
                    name='Actual',
                    marker_color='#e38524',
                    yaxis='y1',
                    text=[format_num(totals['Actual Unique Customer'])],
                    textposition='outside'
                ))

                # Add bars for Disbursed Amount on secondary y-axis
                # Function to format numbers with commas
                def format_number(num):
                    if num >= 1_000_000:
                        return f"{num / 1_000_000:,.2f}M"
                    return f"{num:,.2f}"
                fig.add_trace(go.Bar(
                    x=['Disbursed Amount'],
                    y=[totals['Target Disbursed Amount']],
                    name='Target',
                    marker_color='#00adef',
                    yaxis='y2',
                    text=[format_number(totals['Target Disbursed Amount'])],
                    textposition='outside',
                    showlegend=False
                ))

                fig.add_trace(go.Bar(
                    x=['Disbursed Amount'],
                    y=[totals['Actual Disbursed Amount']],
                    name='Actual',
                    marker_color='#e38524',
                    yaxis='y2',
                    text=[format_number(totals['Actual Disbursed Amount'])],
                    textposition='outside',
                    showlegend=False
                ))

                # Update the layout for better visualization
                fig.update_layout(
                    # title='Michu(Wabi & Guyya) YTD(<span style="color: #00adef;">Year-To-Date </span>)',
                    title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product YTD (<span style="color: #00adef; text-decoration: underline;">Year-To-Date </span>) </span>',
                    xaxis=dict(title='Metrics'),
                    yaxis=dict(
                        title='Unique Customer',
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                    ),
                    yaxis2=dict(
                        title='Disbursed Amount',
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        anchor='free',
                        overlaying='y',
                        side='right',
                        position=1
                    ),
                    barmode='group',  # Group the bars side by side
                    bargap=0.2,  # Gap between bars of adjacent location coordinates
                    bargroupgap=0.1, # Gap between bars of the same location coordinate
                    margin=dict(t=80),
                    # legend=dict(
                    # title='Legend',
                    # itemsizing='constant'
                    # )
                )

                # Display the chart in Streamlit
                # st.write("### Michu - Target vs Actual Comparison")
                st.plotly_chart(fig, use_container_width=True)
                    # col1, col2 = st.columns([0.1, 0.9])



                col11, col22 = st.columns([0.2, 0.8])

                with col22:
                    # Drop duplicates based on target_Id and actual_Id
                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    # Function to convert decimal.Decimal to float
                    def convert_to_float(series):
                        return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                    # Group and aggregate the data for each metric
                    unique_customer_df = df_target_unique.groupby(['District', 'Branch']).agg(
                        {'Target Unique Customer': 'sum'}).reset_index()
                    actual_unique_customer_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                        {'Actual Unique Customer': 'sum'}).reset_index()

                    # Convert decimals to float
                    unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                    actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                    unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='left')

                    # Function to calculate percentage safely
                    def calculate_percentage_unique(row):
                        if row['Target Unique Customer'] == 0:
                            if row['Actual Unique Customer'] == 0:
                                return np.nan  # Case 1: Both Target and Actual are 0
                            else:
                                return np.inf  # Case 2: Target is 0 but Actual is not
                        else:
                            return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                    # Apply the function to each row
                    unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                    
                    # unique_customer_df['Percentage(%)'] = (
                    #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                    unique_customer_df['Metric'] = 'Unique Customer'

                    # account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                    #     {'Target Number Of Account': 'sum'}).reset_index()
                    # actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                    #     {'Actual Number Of Account': 'sum'}).reset_index()

                    # # Convert decimals to float
                    # account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                    # actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                    # account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='left')

                    # def calculate_percentage_account(row):
                    #     if row['Target Number Of Account'] == 0:
                    #         if row['Actual Number Of Account'] == 0:
                    #             return np.nan  # Case 1: Both Target and Actual are 0
                    #         else:
                    #             return np.inf  # Case 2: Target is 0 but Actual is not
                    #     else:
                    #         return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                    # # Apply the function to each row
                    # account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                    # # account_df['Percentage(%)'] = (
                    # #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                    # account_df['Metric'] = 'Number Of Account'

                    disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                        {'Target Disbursed Amount': 'sum'}).reset_index()
                    actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                        {'Actual Disbursed Amount': 'sum'}).reset_index()

                    # Convert decimals to float
                    disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                    actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                    disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='left')

                    def calculate_percentage_dis(row):
                        if row['Target Disbursed Amount'] == 0:
                            if row['Actual Disbursed Amount'] == 0:
                                return np.nan  # Case 1: Both Target and Actual are 0
                            else:
                                return np.inf  # Case 2: Target is 0 but Actual is not
                        else:
                            return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                    # Apply the function to each row
                    disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                    # disbursed_amount_df['Percentage(%)'] = (
                    #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                    disbursed_amount_df['Metric'] = 'Disbursed Amount'

                    # Rename columns to have consistent names
                    unique_customer_df = unique_customer_df.rename(columns={
                        'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                    # account_df = account_df.rename(columns={
                    #     'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                    disbursed_amount_df = disbursed_amount_df.rename(columns={
                        'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                    # Combine the DataFrames into one
                    combined_df = pd.concat([unique_customer_df, disbursed_amount_df])

                    combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                    combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                    # Format 'Percentage(%)' with a percentage sign
                    combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                    # Reset the index and rename it to start from 1
                    combined_df_reset = combined_df.reset_index(drop=True)
                    combined_df_reset.index = combined_df_reset.index + 1

                    # Apply styling
                    def highlight_columns(s):
                        colors = []
                        for val in s:
                            if isinstance(val, str) and '%' in val:
                                percentage_value = float(val.strip('%'))
                                if percentage_value < 50:
                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                elif 50 <= percentage_value < 70:
                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                elif percentage_value >= 70:
                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                else:
                                    colors.append('')
                            else:
                                colors.append('')  # no color for other values
                        return colors

                    styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                        .set_properties(**{
                                                            'text-align': 'center'
                                                        }) \
                                                        .set_table_styles([
                                                            dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                        ])
                    # Convert styled DataFrame to HTML
                    styled_html = styled_df.to_html()

                    # Display the result
                    # st.write(":orange[Michu(Wabi & Guyya) YTD] (:blue[Year-To-Date]) 👇🏻")
                    st.write(
                            f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product YTD (<span style="color: #00adef;">Year-To-Date</span>)</span>',
                            unsafe_allow_html=True
                        )
                    # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                    st.write(styled_html, unsafe_allow_html=True)

                    st.write(" ")
                    st.write(" ")
                    st.write(" ")



                

                    
                # with ccool1:
                # Get the current date
                # current_date = datetime.now().date()

                # Get the current date
                current_date = datetime.now().date()

                # Calculate the start and end date of the current month
                start_of_month = current_date.replace(day=1)
                end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                # Filter the dataframe based on the selected date range
                df_filtered = df_merged[
                    (df_merged["Target Date"].dt.date >= start_of_month) & 
                    (df_merged["Target Date"].dt.date <= end_of_month)
                ].copy()

                df_filtered_actual = df_merged[
                    (df_merged["Actual Date"].dt.date >= start_of_month) & 
                    (df_merged["Actual Date"].dt.date <= end_of_month)
                ].copy()
                

                df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                
                # Group by unique target_Id and sum the target columns
                target_grouped = df_target_unique.groupby('target_Id').agg({
                    'Target Unique Customer': 'sum',
                    'Target Disbursed Amount': 'sum'
                }).sum()

                # Group by unique actual_Id and sum the actual columns
                actual_grouped = df_actual_unique.groupby('actual_Id').agg({
                    'Actual Unique Customer': 'sum',
                    'Actual Disbursed Amount': 'sum'
                }).sum()
                # Aggregate the data to get total values
                
                totals = {
                    'Target Unique Customer': target_grouped['Target Unique Customer'],
                    'Actual Unique Customer': actual_grouped['Actual Unique Customer'],
                    # 'Target Number Of Account': target_grouped['Target Number Of Account'],
                    # 'Actual Number Of Account': actual_grouped['Actual Number Of Account'],
                    'Target Disbursed Amount': target_grouped['Target Disbursed Amount'],
                    'Actual Disbursed Amount': actual_grouped['Actual Disbursed Amount'],
                }

                # Create the bar chart
                fig = go.Figure()

                # Add bars for Unique Customer and Number of Accounts
                def format_num(num):
                    return f"{num:,.0f}"
                fig.add_trace(go.Bar(
                    x=['Unique Customer'],
                    y=[totals['Target Unique Customer']],
                    name='Target',
                    marker_color= '#00adef',
                    yaxis='y1',
                    text=[format_num(totals['Target Unique Customer'])],
                    textposition='outside'
                ))

                fig.add_trace(go.Bar(
                    x=['Unique Customer'],
                    y=[totals['Actual Unique Customer']],
                    name='Actual',
                    marker_color='#e38524',
                    yaxis='y1',
                    text=[format_num(totals['Actual Unique Customer'])],
                    textposition='outside'
                ))

                # Add bars for Disbursed Amount on secondary y-axis
                # Function to format numbers with commas
                def format_number(num):
                    if num >= 1_000_000:
                        return f"{num / 1_000_000:,.2f}M"
                    return f"{num:,.2f}"
                fig.add_trace(go.Bar(
                    x=['Disbursed Amount'],
                    y=[totals['Target Disbursed Amount']],
                    name='Target',
                    marker_color='#00adef',
                    yaxis='y2',
                    text=[format_number(totals['Target Disbursed Amount'])],
                    textposition='outside',
                    showlegend=False
                ))

                fig.add_trace(go.Bar(
                    x=['Disbursed Amount'],
                    y=[totals['Actual Disbursed Amount']],
                    name='Actual',
                    marker_color='#e38524',
                    yaxis='y2',
                    text=[format_number(totals['Actual Disbursed Amount'])],
                    textposition='outside',
                    showlegend=False
                ))

                # Update the layout for better visualization
                current_month_name = datetime.now().strftime("%B")
                fig.update_layout(
                    # title=f'Michu(Wabi & Guyya), Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
                    title=f'<span style="text-decoration: underline;"> Michu  <span style="color: #e38524; font-size: 20px; text-decoration: underline;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef; text-decoration: underline;">{current_month_name} </span>) </span>',
                    xaxis=dict(title='Metrics'),
                    yaxis=dict(
                        title='Unique Customer',
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                    ),
                    yaxis2=dict(
                        title='Disbursed Amount',
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        anchor='free',
                        overlaying='y',
                        side='right',
                        position=1
                    ),
                    barmode='group',  # Group the bars side by side
                    bargap=0.2,  # Gap between bars of adjacent location coordinates
                    bargroupgap=0.1, # Gap between bars of the same location coordinate
                    margin=dict(t=80),
                    # legend=dict(
                    # title='Legend',
                    # itemsizing='constant'
                    # )
                )

                # Display the chart in Streamlit
                # st.write("### Michu - Target vs Actual Comparison")
                st.plotly_chart(fig, use_container_width=True)






                coll11, coll22 = st.columns([0.2, 0.8])
                with coll22:
                    # Drop duplicates based on target_Id and actual_Id
                    df_target_unique = df_filtered.drop_duplicates(subset='target_Id')
                    df_actual_unique = df_filtered_actual.drop_duplicates(subset='actual_Id')

                    # Function to convert decimal.Decimal to float
                    def convert_to_float(series):
                        return series.apply(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

                    # Group and aggregate the data for each metric
                    unique_customer_df = df_target_unique.groupby(['District', 'Branch']).agg(
                        {'Target Unique Customer': 'sum'}).reset_index()
                    actual_unique_customer_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                        {'Actual Unique Customer': 'sum'}).reset_index()

                    # Convert decimals to float
                    unique_customer_df['Target Unique Customer'] = convert_to_float(unique_customer_df['Target Unique Customer'])
                    actual_unique_customer_df['Actual Unique Customer'] = convert_to_float(actual_unique_customer_df['Actual Unique Customer'])

                    unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='left')
                    def calculate_percentage_unique(row):
                        if row['Target Unique Customer'] == 0:
                            if row['Actual Unique Customer'] == 0:
                                return np.nan  # Case 1: Both Target and Actual are 0
                            else:
                                return np.inf  # Case 2: Target is 0 but Actual is not
                        else:
                            return (row['Actual Unique Customer'] / row['Target Unique Customer']) * 100  # Case 3: Safe to calculate

                    # Apply the function to each row
                    unique_customer_df['Percentage(%)'] = unique_customer_df.apply(calculate_percentage_unique, axis=1)
                    
                    # unique_customer_df['Percentage(%)'] = (
                    #     unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100
                    unique_customer_df['Metric'] = 'Unique Customer'

                    # account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                    #     {'Target Number Of Account': 'sum'}).reset_index()
                    # actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                    #     {'Actual Number Of Account': 'sum'}).reset_index()

                    # # Convert decimals to float
                    # account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                    # actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])

                    # account_df = account_df.merge(actual_account_df, on=['District', 'Branch'], how='left')

                    # def calculate_percentage_account(row):
                    #     if row['Target Number Of Account'] == 0:
                    #         if row['Actual Number Of Account'] == 0:
                    #             return np.nan  # Case 1: Both Target and Actual are 0
                    #         else:
                    #             return np.inf  # Case 2: Target is 0 but Actual is not
                    #     else:
                    #         return (row['Actual Number Of Account'] / row['Target Number Of Account']) * 100  # Case 3: Safe to calculate

                    # # Apply the function to each row
                    # account_df['Percentage(%)'] = account_df.apply(calculate_percentage_account, axis=1)

                    # # account_df['Percentage(%)'] = (
                    # #     account_df['Actual Number Of Account'] / account_df['Target Number Of Account']) * 100
                    # account_df['Metric'] = 'Number Of Account'

                    disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                        {'Target Disbursed Amount': 'sum'}).reset_index()
                    actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
                        {'Actual Disbursed Amount': 'sum'}).reset_index()


                    # Convert decimals to float
                    disbursed_amount_df['Target Disbursed Amount'] = convert_to_float(disbursed_amount_df['Target Disbursed Amount'])
                    actual_disbursed_amount_df['Actual Disbursed Amount'] = convert_to_float(actual_disbursed_amount_df['Actual Disbursed Amount'])

                    disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District', 'Branch'], how='left')

                    def calculate_percentage_dis(row):
                        if row['Target Disbursed Amount'] == 0:
                            if row['Actual Disbursed Amount'] == 0:
                                return np.nan  # Case 1: Both Target and Actual are 0
                            else:
                                return np.inf  # Case 2: Target is 0 but Actual is not
                        else:
                            return (row['Actual Disbursed Amount'] / row['Target Disbursed Amount']) * 100  # Case 3: Safe to calculate

                    # Apply the function to each row
                    disbursed_amount_df['Percentage(%)'] = disbursed_amount_df.apply(calculate_percentage_dis, axis=1)

                    # disbursed_amount_df['Percentage(%)'] = (
                    #     disbursed_amount_df['Actual Disbursed Amount'] / disbursed_amount_df['Target Disbursed Amount']) * 100
                    disbursed_amount_df['Metric'] = 'Disbursed Amount'

                    # Rename columns to have consistent names
                    unique_customer_df = unique_customer_df.rename(columns={
                        'Target Unique Customer': 'Target', 'Actual Unique Customer': 'Actual'})
                    # account_df = account_df.rename(columns={
                    #     'Target Number Of Account': 'Target', 'Actual Number Of Account': 'Actual'})
                    disbursed_amount_df = disbursed_amount_df.rename(columns={
                        'Target Disbursed Amount': 'Target', 'Actual Disbursed Amount': 'Actual'})

                    # Combine the DataFrames into one
                    combined_df = pd.concat([unique_customer_df, disbursed_amount_df])

                    combined_df['Target'] = combined_df['Target'].map(lambda x: f"{x:,.0f}")
                    combined_df['Actual'] = combined_df['Actual'].map(lambda x: f"{x:,.0f}")

                    # Format 'Percentage(%)' with a percentage sign
                    combined_df['Percentage(%)'] = combined_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                    # Reset the index and rename it to start from 1
                    combined_df_reset = combined_df.reset_index(drop=True)
                    combined_df_reset.index = combined_df_reset.index + 1

                    # Apply styling
                    def highlight_columns(s):
                        colors = []
                        for val in s:
                            if isinstance(val, str) and '%' in val:
                                percentage_value = float(val.strip('%'))
                                if percentage_value < 50:
                                    colors.append('background-color: #FF0000; color: black; font-weight: bold;')  # red color for values below 50%
                                elif 50 <= percentage_value < 70:
                                    colors.append('background-color: #ffff00; color: black; font-weight: bold;')
                                elif percentage_value >= 70:
                                    colors.append('background-color: #008000; color: black; font-weight: bold;')  # blue color for values 50% and above
                                else:
                                    colors.append('') 
                            else:
                                colors.append('')  # no color for other values
                        return colors

                    styled_df = combined_df_reset.style.apply(highlight_columns, axis=0) \
                                                        .set_properties(**{
                                                            'text-align': 'center'
                                                        }) \
                                                        .set_table_styles([
                                                            dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('font-weight', 'bold')])
                                                        ])
                    # Convert styled DataFrame to HTML
                    styled_html = styled_df.to_html()

                    # Display the result
                    st.write(f":orange[Michu(Wabi & Guyya), Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                    st.write(
                            f'<span style="text-decoration: underline;">Michu <span style="color: #e38524; font-size: 20px;">{selected_product}</span> Product Month-To-Date (<span style="color: #00adef;">{current_month_name}</span>)</span>',
                            unsafe_allow_html=True
                        )
                    # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                    st.write(styled_html, unsafe_allow_html=True)

                    st.write(" ")
                    st.write(" ")
                    st.write(" ")


            
                
                # st.write("""
                #             **Note the following points regarding the Target Performance Report:**

                #             1. *Michu (Wabi & Guyya)* includes the entire Michu Product Performance Report to the end of October. So, the Michu (Wabi & Guyya) YTD (Year-To-Date) tab includes all product Target Performance Reports until the end of October, but only includes Wabi & Guyya products starting  November 1.
                            
                #             2. The *Michu-Kiyya* YTD (Year-To-Date) tab includes only Kiyya products, starting from November 1.

                #             :blue[**NB:** Kiyya product performance prior to November 1 is treated as part of the Michu Target Performance Report (Wabi & Guyya). This is because no specific targets were set for Kiyya products before November 1, and their performance was included under the Michu (Wabi & Guyya) objectives.]
                #             """)



        except Exception as e:
            traceback.print_exc()
            st.error(f"An error occurred while loading data: {e}")
        # finally:
        #     if db_instance:
        #         db_instance.close_connection()
        # Auto-refresh interval (in seconds)
        refresh_interval = 600  # 5 minutes
        st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")






        
               

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
    # new
    main()
