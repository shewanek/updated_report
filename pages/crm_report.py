import streamlit as st
from dependence import load_crmdata
from navigation import  home_sidebar
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from decimal import Decimal
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
        <center> <h3 class = "title_dash"> Kiyya Target Performance Report </h3> </center>
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
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    
    try:
        df_actual, df_target, combined = load_crmdata(username)
        # st.write(combined)
        df_mergedd = pd.merge(df_target, df_actual, on='branch_code',  how='left')

        df_merged = pd.merge(combined, df_mergedd, on='branch_code',  how='outer')
       
        # st.write(df_mergedd)
        # st.write(df_merged)
        # Sidebar filters
        st.sidebar.image("pages/michu.png")
        # username = st.session_state.get("username", "")
        full_name = st.session_state.get("full_name", "")
        role = st.session_state.get("role", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
        #     st.sidebar.header("Please filter")
        home_sidebar()
        role = st.session_state.get("role", "")

        col11, col12 = st.columns([0.4, 0.6])
        with col11:

            # Drop duplicates based on unique identifiers
            df_target_unique = df_merged.drop_duplicates(subset='target_id').copy()
            df_actual_unique = df_merged.dropna(subset=['Saving Account']).drop_duplicates(subset='Saving Account').copy()

            # Group by userId and aggregate target/actual data
            target_grouped = df_target_unique.groupby('branch_code').agg({
                'Target Customer': 'sum'  # Sum of target customers
            }).sum()

            actual_grouped = df_actual_unique.groupby('branch_code').agg({
                'Saving Account': 'count'  # Count of saving accounts for actual
            }).sum()

            # Aggregate the data to get total values
            totals = {
                'Target Customer': target_grouped['Target Customer'],
                'Actual Customer': actual_grouped['Saving Account']  # Renamed Saving Account to Actual Customer
            }

            # Create the bar chart
            fig = go.Figure()

            # Add bar for Target Customer (Target)
            def format_num(num):
                return f"{num:,.0f}"

            fig.add_trace(go.Bar(
                x=['Target Customer'],  # Target Customer for Target
                y=[totals['Target Customer']],
                name='Target',
                marker_color='#00adef',
                text=[format_num(totals['Target Customer'])],
                textposition='outside'
            ))

            # Add bar for Actual Customer (Actual)
            fig.add_trace(go.Bar(
                x=['Actual Customer'],  # Changed label to Actual Customer
                y=[totals['Actual Customer']],
                name='Actual',
                marker_color='#e38524',
                text=[format_num(totals['Actual Customer'])],
                textposition='outside'
            ))

            # Update layout for better visualization
            fig.update_layout(
                title='Target Customer vs Actual Customer',
                xaxis=dict(title='Metrics'),
                yaxis=dict(
                    title='Count',
                    titlefont=dict(color='black'),
                    tickfont=dict(color='black'),
                ),
                barmode='group',  # Group the bars side by side
                bargap=0.2,  # Gap between bars of adjacent location coordinates
                bargroupgap=0.1,  # Gap between bars of the same location coordinate
                margin=dict(t=80)
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col12:
            col1, col2 = st.columns([0.1, 0.9])
            with col2:
                
                st.write(" ")
                st.write(" ")
                st.write(" ")
                st.write(" ")
                st.write(" ")
                st.write(" ")
                st.write(" ")
                def convert_to_float(value):
                    if isinstance(value, Decimal):
                        return float(value)
                    return value
                    
                df_target_unique = df_merged.drop_duplicates(subset='target_id').copy()
                df_actual_unique = df_merged.drop_duplicates(subset='Saving Account').copy()

                # Group by userId and aggregate target/actual data
                target_grouped = df_target_unique.groupby('branch_code').agg({
                    'Target Customer': 'sum'  # Sum of target customers
                }).sum()

                actual_grouped = df_actual_unique.groupby('branch_code').agg({
                    'Saving Account': 'count'  # Count of saving accounts for actual
                }).sum()
                target_grouped = convert_to_float(target_grouped)
                actual_grouped = convert_to_float(actual_grouped)

                # Aggregate the data to get total values
                totals = {
                    'Target Customer': target_grouped['Target Customer'],
                    'Actual Customer': actual_grouped['Saving Account'],  # Renamed Saving Account to Actual Customer
                    'Percentage(%)': (actual_grouped['Saving Account'] / target_grouped['Target Customer'] * 100) if target_grouped['Target Customer'] != 0 else 0
                }

                # Create a DataFrame for display with Target, Actual, and Metrics (Kiyya Customer)
                final_df = pd.DataFrame({
                    'Target': [totals['Target Customer']if totals['Target Customer'] is not None else 0],
                    'Actual': [totals['Actual Customer']if totals['Actual Customer'] is not None else 0],
                    'Percentage(%)': [totals['Percentage(%)']],
                    'Metric': ['Kiyya Customer']
                })
                # final_df['Actual'] = final_df['Actual'].apply(convert_decimal)

                # Round the 'Target', 'Actual', and 'Percentage(%)' columns
                final_df.loc[:,'Target'] = final_df['Target'].map(lambda x: f"{x:,.0f}")
                final_df['Actual'] = final_df['Actual'].map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
                final_df.loc[:,'Percentage(%)'] = final_df['Percentage(%)'].map(lambda x: f"{x:.2f}%")

                # Reset the index and rename it to start from 1
                grouped_df_reset = final_df.reset_index(drop=True)
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
                                                    dict(selector='th', props=[('text-align', 'center'), ('background-color', '#00adef'), ('color', 'white'), ('font-size', '25px'), ('font-weight', 'bold')])
                                                ])

                # Convert styled DataFrame to HTML
                styled_html = styled_df.to_html()

                # Display the result with custom CSS in Streamlit
                # st.write(":orange[Target vs Actual Kiyya Customer Data] 👇🏻")
                st.write(" ")
                st.write(" ")
                st.write(" ")
                st.markdown(styled_html, unsafe_allow_html=True)
   
            

            

    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
            
    # # Auto-refresh interval (in seconds)
    # refresh_interval = 600  # 5 minutes
    # st_autorefresh(interval=refresh_interval * 1000, key="Michu report dash")       


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
