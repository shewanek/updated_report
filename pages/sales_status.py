import streamlit as st
# from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
from navigation import home_sidebar
import plotly.graph_objects as go
import pandas as pd
from dependence import load_sales_detail, update_rejected_customers
from dependence import update_activity, check_session_timeout


# Check timeout on every interaction
check_session_timeout()
pd.set_option('future.no_silent_downcasting', True)


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
        <center> <h3 class = "title_dash"> Michu Retention Detail Report </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)


    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    try:
        if role == 'Admin' or role == 'under_admin':
            df_combine_prospect, df_combine_rejected, df_merged_closed, df_merged_emegancce, df_merged_marchent, df_agents = load_sales_detail(role, username)
        else:
            df_combine_prospect, df_combine_rejected, df_merged_closed = load_sales_detail(role, username)
       
        home_sidebar()

        


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
            total_agents = df_agents['inactive_sum'].values[0] if not df_agents.empty else 0
            total_agents_active = df_agents['active_sum'].values[0] if not df_agents.empty else 0



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
        
        col2, col3, col4, col5, col6, col7 = st.columns(6)
        # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col2.metric(label="**Active / Rejected**", value=f"{total_rejected_active}/{Total_rejected_notactive}")
        col3.metric(label="**Active / Closed**", value=f"{total_closed_active}/{total_closed}")
        col4.metric(label="**Active / Prospective**", value=f"{total_prospective_active}/{total_prospective}")
        if role == 'Admin' or role == 'under_admin':
            col5.metric(label="**Active / emrgance**", value=f"{total_emrgance_active}/{total_emrgance}")
            col6.metric(label="**Active / marchent**", value=f"{total_marchent_active}/{total_marchent}")
            col7.metric(label="**Active / Agents**", value=f"{total_agents_active}/{total_agents}")
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



