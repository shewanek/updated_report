import streamlit as st
from navigation import make_sidebar1, home_sidebar
import pandas as pd
import plotly.graph_objects as go
import numpy as np
# from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import decimal
from dependence import load_kiyya_actual_vs_targetdata
from dependence import initialize_session, update_activity, check_session_timeout




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
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
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
    update_activity()
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
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
        <center> <h3 class = "title_dash"> Target Performance Report of Kiyya(Informal & Formal) </h3> </center>
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
        st.switch_page("main.py")

    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Initialize database connection using Singleton pattern
    st.snow()
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    try:
        
        dis_branch, df_actual, df_target = load_kiyya_actual_vs_targetdata(role, username)
        
        # Get the maximum date of the current month
        # Get the current date and the maximum date for the current month
        current_date = datetime.now().date()
        current_month_max_date = current_date.replace(day=1) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        current_month_max_date = current_month_max_date.date()

        # Convert 'Actual Date' and 'Target Date' columns to datetime
        df_actual['Actual Date'] = pd.to_datetime(df_actual['Actual Date']).dt.date
        df_target['Target Date'] = pd.to_datetime(df_target['Target Date']).dt.date

        # Filter df_actual and df_target based on the current month's max date
        df_actual = df_actual[df_actual['Actual Date'] <= current_month_max_date]
        df_target = df_target[df_target['Target Date'] <= current_month_max_date]

        
        # Display the filtered DataFrames
        # dis_branch, df_actual, df_target
        merged_acttarg = pd.merge(df_actual, df_target, on='Branch Code', how='outer')
        df_merged =  pd.merge(dis_branch, merged_acttarg, on='Branch Code', how='inner')
        # df_merged

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
            district = st.sidebar.multiselect("Select District", options=df_merged["District"].dropna().unique())

            if not district:
                df_merged = df_merged.copy()
            else:
                df_merged = df_merged[df_merged["District"].isin(district)]

        if role != 'Branch User':
            branch = st.sidebar.multiselect("Select Branch", options=df_merged["Branch"].dropna().unique())

            if not branch:
                df_merged = df_merged.copy()
            else:
                df_merged = df_merged[df_merged["Branch"].isin(branch)]
            

        if df_merged is not None and not df_merged.empty:
            col1, col2 = st.sidebar.columns(2)

            # Convert the date columns to datetime if they are not already
            df_merged["Target Date"] = pd.to_datetime(df_merged["Target Date"], errors='coerce')
            df_merged["Actual Date"] = pd.to_datetime(df_merged["Actual Date"], errors='coerce')

            # Extract the year and month for filtering
            df_merged['Target Year-Month'] = df_merged['Target Date'].dt.to_period('M')
            df_merged['Actual Year-Month'] = df_merged['Actual Date'].dt.to_period('M')

            # Getting the min and max month
            target_start_month  = df_merged["Target Year-Month"].min()
            target_end_month = df_merged["Target Year-Month"].max()
            actual_start_month = df_merged["Actual Year-Month"].min()
            actual_end_month = df_merged["Actual Year-Month"].max()
            # st.write(actual_start_month)

            # Determine the overall min and max months
            # overall_start_month = min(target_start_month, actual_start_month)
            # overall_end_month = max(target_end_month, actual_end_month)
            # Handle start month
            overall_start_month = (
                target_start_month if pd.isna(actual_start_month)
                else actual_start_month if pd.isna(target_start_month)
                else min(target_start_month, actual_start_month)
            )

            # Handle end month
            overall_end_month = (
                target_end_month if pd.isna(actual_end_month)
                else actual_end_month if pd.isna(target_end_month)
                else max(target_end_month, actual_end_month)
            )
            # st.write(overall_start_month)
            

            # Create a list of months between the overall start and end
            all_months = pd.period_range(start=overall_start_month, end=overall_end_month, freq='M')
            # Map the periods to month names
            # Map the periods to month names
            month_names = all_months.strftime('%B %Y')

            with col1:
                start_period = st.selectbox("Start Month", month_names)

            with col2:
                end_period = st.selectbox("End Month", month_names, index=len(month_names) - 1)

            # Convert selected periods back to Period type for comparison
            start_period = pd.Period(start_period, freq='M')
            end_period = pd.Period(end_period, freq='M')

            # # Filter the dataframe based on the selected months
            # df_merged = df_merged[
            #     (df_merged["Target Year-Month"] >= start_period) & (df_merged["Target Year-Month"] <= end_period) &
            #     (df_merged["Actual Year-Month"] >= start_period) & (df_merged["Actual Year-Month"] <= end_period)
            # ].copy()

            df_filtered = df_merged[
                (df_merged["Target Year-Month"] >= start_period) & (df_merged["Target Year-Month"] <= end_period)
            ].copy()

            # You can filter Actual Year-Month separately if needed
            df_filtered_actual = df_merged[
                (df_merged["Actual Year-Month"] >= start_period) & (df_merged["Actual Year-Month"] <= end_period)
            ].copy()


        
        if role == "Admin" or role == "Sales Admin" or role == 'under_admin':
            if not district and not branch:
                df_merged = df_merged
            elif district:
                df_merged = df_merged[df_merged["District"].isin(district)]
            elif branch:
                df_merged = df_merged[df_merged["Branch"].isin(branch)]
            else:
                df_merged = df_merged[df_merged["District"].isin(district) & df_merged["Branch"].isin(branch)]


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
            # Drop duplicate target_Id and actual_Id
            with tab1:
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
                    title='Target vs Actual YTD (<span style="color: #00adef;">Year-To-Date </span>)',
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
                            'Percentage(%)': percent_value,
                            'Metric': metric
                        })

                    # Create final_df DataFrame
                    final_df = pd.DataFrame(final_df_data)

                    # Round the 'Target' and 'Actual' columns to two decimal points
                    final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                    final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                    # Format 'Percentage(%)' with a percentage sign
                    final_df['Percentage(%)'] = final_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")
                    # Drop rows where 'Percentage(%)' is 'nan%'
                    filtered_df = final_df[final_df['Percentage(%)'] != 'nan%']

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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                else:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(":orange[Target vs Actual YTD] (:blue[Year-To-Date]) 👇🏻")
                    
                    st.markdown(styled_html, unsafe_allow_html=True)

                    st.write(" ")
                    st.write(" ")
                    st.write(" ")
            

            with tab2:
                tab3, tab4 = st.tabs(["Per District", "Per Branch"])
                
                # Display combined data in a table
                
                with tab3:
                    col1, col2 = st.columns([0.1, 0.9])
                    with col2:
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":blue[Unique Customer] 👇🏻")
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":blue[Number Of Account]  👇🏻")
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":blue[Disbursed Amount] 👇🏻")
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":orange[Unique Customer]  👇🏻")
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":orange[Number Of Account]  👇🏻")
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
                                        colors.append('background-color: #800020')  # dark color for values below 50%
                                    elif 50 <= percentage_value < 75:
                                        colors.append('background-color: #FF0000')
                                    elif 75 <= percentage_value < 100:
                                        colors.append('background-color: #e38524')
                                    elif 100 <= percentage_value < 120:
                                        colors.append('background-color: #3CB371')
                                    elif percentage_value >= 120:
                                        colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                        st.write(":orange[Disbursed Amount] 👇🏻")
                        st.write(styled_df)
            with tab1:
                # Get the current date
                current_date = datetime.now().date()

                # Calculate the start and end date of the current month
                start_of_month = current_date.replace(day=1)
                end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                # Ensure 'start_period' and 'end_period' are of Period type
                start_period = pd.Period(start_of_month, freq='M')
                end_period = pd.Period(end_of_month, freq='M')

                # Filter the dataframe based on the selected periods
                df_filtered = df_merged[
                    (df_merged["Target Year-Month"] >= start_period) & (df_merged["Target Year-Month"] <= end_period)
                ].copy()

                df_filtered_actual = df_merged[
                    (df_merged["Actual Year-Month"] >= start_period) & (df_merged["Actual Year-Month"] <= end_period)
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
                    title='Target vs Actual MTD (<span style="color: #00adef;">Month-To-Date </span>)',
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
                            'Percentage(%)': percent_value,
                            'Metric': metric
                        })

                    # Create final_df DataFrame
                    final_df = pd.DataFrame(final_df_data)

                    # Round the 'Target' and 'Actual' columns to two decimal points
                    final_df['Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                    final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}")

                    # Format 'Percentage(%)' with a percentage sign
                    final_df['Percentage(%)'] = final_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")
                    # Drop rows where 'Percentage(%)' is 'nan%'
                    filtered_df = final_df[final_df['Percentage(%)'] != 'nan%']

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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                else:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(":orange[Target vs Actual MTD] (:blue[Month-To-Date]) 👇🏻")
                    
                    st.markdown(styled_html, unsafe_allow_html=True)

                    st.write(" ")
                    st.write(" ")
                    st.write(" ")

                    
        # -- for role District User --

        if role == 'District User':
            tab1, tab2 = st.tabs(["📈 Aggregate Report", "🗃 Report per Branch"])
            with tab1:
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
                    title='Target vs Actual YTD (<span style="color: #00adef;">Year-To-Date </span>)',
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
                    
                    unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='outer')

                    unique_customer_df['Percentage(%)'] = (
                        (unique_customer_df['Actual Unique Customer'] / unique_customer_df['Target Unique Customer']) * 100).round(0)
                    unique_customer_df['Metric'] = 'Unique Customer'

                    account_df = df_target_unique.groupby(['District']).agg(
                        {'Target Number Of Account': 'sum'}).reset_index()
                    actual_account_df = df_actual_unique.groupby(['District']).agg(
                        {'Actual Number Of Account': 'sum'}).reset_index()
                    account_df['Target Number Of Account'] = convert_to_float(account_df['Target Number Of Account'])
                    actual_account_df['Actual Number Of Account'] = convert_to_float(actual_account_df['Actual Number Of Account'])
                    account_df = account_df.merge(actual_account_df, on=['District'], how='outer')
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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                else:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                col1, col2 = st.columns([0.1, 0.9])
                # Display combined data in a table
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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                elif percentage_value >= 120:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(":orange[Unique Customer]  👇🏻")
                    st.write(styled_df)



                with col2:
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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                elif percentage_value >= 120:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(":orange[Number Of Account]  👇🏻")
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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                elif percentage_value >= 120:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(":orange[Disbursed Amount]  👇🏻")
                    st.write(styled_df)
            

            with tab1:
                # Get the current date
                current_date = datetime.now().date()

                # Calculate the start and end date of the current month
                start_of_month = current_date.replace(day=1)
                end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

                # Ensure 'start_period' and 'end_period' are of Period type
                start_period = pd.Period(start_of_month, freq='M')
                end_period = pd.Period(end_of_month, freq='M')

                # Filter the dataframe based on the selected periods
                df_filtered = df_merged[
                    (df_merged["Target Year-Month"] >= start_period) & (df_merged["Target Year-Month"] <= end_period)
                ].copy()

                df_filtered_actual = df_merged[
                    (df_merged["Actual Year-Month"] >= start_period) & (df_merged["Actual Year-Month"] <= end_period)
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
                    title=f'Target vs Actual, Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
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
                    
                    unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District'], how='outer')

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
                    account_df = account_df.merge(actual_account_df, on=['District'], how='outer')

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
                    
                    disbursed_amount_df = disbursed_amount_df.merge(actual_disbursed_amount_df, on=['District'], how='outer')

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
                                    colors.append('background-color: #800020')  # dark color for values below 50%
                                elif 50 <= percentage_value < 75:
                                    colors.append('background-color: #FF0000')
                                elif 75 <= percentage_value < 100:
                                    colors.append('background-color: #e38524')
                                elif 100 <= percentage_value < 120:
                                    colors.append('background-color: #3CB371')
                                else:
                                    colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                    st.write(f":orange[Target vs Actual, Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                    st.write(styled_html, unsafe_allow_html=True)



                    st.write("")
                    st.write("")

        if role == 'Branch User':
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
                title='Target vs Actual YTD(<span style="color: #00adef;">Year-To-Date </span>)',
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

                account_df = df_target_unique.groupby(['District', 'Branch']).agg(
                    {'Target Number Of Account': 'sum'}).reset_index()
                actual_account_df = df_actual_unique.groupby(['District', 'Branch']).agg(
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

                disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                    {'Target Disbursed Amount': 'sum'}).reset_index()
                actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
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
                                colors.append('background-color: #800020')  # dark color for values below 50%
                            elif 50 <= percentage_value < 75:
                                colors.append('background-color: #FF0000')
                            elif 75 <= percentage_value < 100:
                                colors.append('background-color: #e38524')
                            elif 100 <= percentage_value < 120:
                                colors.append('background-color: #3CB371')
                            elif percentage_value >= 120:
                                colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                st.write(styled_html, unsafe_allow_html=True)

                st.write(" ")
                st.write(" ")
                st.write(" ")
            

            # Get the current date
            # current_date = datetime.now().date()

            # Get the current date
            current_date = datetime.now().date()

            # Calculate the start and end date of the current month
            start_of_month = current_date.replace(day=1)
            end_of_month = (start_of_month + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()

            # Ensure 'start_period' and 'end_period' are of Period type
            start_period = pd.Period(start_of_month, freq='M')
            end_period = pd.Period(end_of_month, freq='M')

            # Filter the dataframe based on the selected periods
            df_filtered = df_merged[
                (df_merged["Target Year-Month"] >= start_period) & (df_merged["Target Year-Month"] <= end_period)
            ].copy()

            df_filtered_actual = df_merged[
                (df_merged["Actual Year-Month"] >= start_period) & (df_merged["Actual Year-Month"] <= end_period)
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
                title=f'Target vs Actual, Month-To-Date (<span style="color: #00adef;">{current_month_name} </span>)',
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

                unique_customer_df = unique_customer_df.merge(actual_unique_customer_df, on=['District', 'Branch'], how='outer')
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

                disbursed_amount_df = df_target_unique.groupby(['District', 'Branch']).agg(
                    {'Target Disbursed Amount': 'sum'}).reset_index()
                actual_disbursed_amount_df = df_actual_unique.groupby(['District', 'Branch']).agg(
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
                                colors.append('background-color: #800020')  # dark color for values below 50%
                            elif 50 <= percentage_value < 75:
                                colors.append('background-color: #FF0000')
                            elif 75 <= percentage_value < 100:
                                colors.append('background-color: #e38524')
                            elif 100 <= percentage_value < 120:
                                colors.append('background-color: #3CB371')
                            elif percentage_value >= 120:
                                colors.append('background-color: #00adef')  # blue color for values 50% and above
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
                st.write(f":orange[Target vs Actual, Month-To-Date] (:blue[{current_month_name}]) 👇🏻")
                # st.title='Target vs Actual (<span style="color: #00adef;">Year to Date </span>)'
                st.write(styled_html, unsafe_allow_html=True)

                st.write(" ")
                st.write(" ")
                st.write(" ")


    except Exception as e:
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
