import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
from navigation import home_sidebar
from dependence import get_officerreject, get_officerclosed, get_officerprospect
from dependence import initialize_session, update_activity, check_session_timeout
import pandas as pd

# Check timeout on every interaction
check_session_timeout()

def main():
    # Set page configuration
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    
    # Custom CSS styles
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem;
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
            background-color: #00bfff;
            color: white;
        }
        .app-header {
            display: none;
        }
        .dataframe {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section-title {
            color: #00adef;
            border-bottom: 2px solid #00adef;
            padding-bottom: 5px;
            margin-top: 20px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    update_activity()
    home_sidebar()

    # Auto-refresh interval (in seconds)
    refresh_interval = 6600
    st_autorefresh(interval=refresh_interval * 1000, key="Michu Bot dash")

    # Header with logo and title
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/michu.png', width=80)
    with col2:
        st.markdown("""
        <h2 style='color: #00adef; margin-top: 0;'>Michu Officer Dashboard </h2>
        """, unsafe_allow_html=True)
    
    # Check session
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    if not role or not username:
        st.error("Session expired. Please log in again.")
        return
    
    try:
        # Rejected Customers Section
        st.markdown("<h3 class='section-title'>Rejected Customer Report</h3>", unsafe_allow_html=True)
        rejected_data = get_officerreject()
        if not rejected_data:
            st.warning("No rejected customer data available.")
        else:
            rejected_df = pd.DataFrame(rejected_data).sort_values(by='Active %', ascending=False)
            st.dataframe(
                rejected_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Officer": st.column_config.TextColumn("Officer", width="medium"),
                    "Total Rejected": st.column_config.NumberColumn("Total Rejected"),
                    "Total Active": st.column_config.NumberColumn("Total Active"),
                    "Active %": st.column_config.ProgressColumn(
                        "Active %"
                    )
                }
            )
        
        # Closed Customers Section
        st.markdown("<h3 class='section-title'>Closed Customer Report</h3>", unsafe_allow_html=True)
        closed_data = get_officerclosed()
        if not closed_data:
            st.warning("No closed customer data available.")
        else:
            closed_df = pd.DataFrame(closed_data).sort_values(by='Active %', ascending=False)
            st.dataframe(
                closed_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Officer": st.column_config.TextColumn("Officer", width="medium"),
                    "Total Closed": st.column_config.NumberColumn("Total Closed"),
                    "Total Active": st.column_config.NumberColumn("Total Active"),
                    "Active %": st.column_config.ProgressColumn(
                        "Active %"
                    )
                }
            )
        
        # Prospect Customers Section
        st.markdown("<h3 class='section-title'>Prospect Customer Report</h3>", unsafe_allow_html=True)
        prospect_data = get_officerprospect()
        if not prospect_data:
            st.warning("No prospect customer data available.")
        else:
            prospect_df = pd.DataFrame(prospect_data).sort_values(by='Active %', ascending=False)
            st.dataframe(
                prospect_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Officer": st.column_config.TextColumn("Officer", width="medium"),
                    "Total Prospect": st.column_config.NumberColumn("Total Prospect"),
                    "Total Active": st.column_config.NumberColumn("Total Active"),
                    "Active %": st.column_config.ProgressColumn(
                        "Active %",
                    )
                }
            )
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return

if __name__ == "__main__":
    main()
    
    # Footer
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
        z-index: 1000;
    }
    </style>
    <div class='footer'>
    <p>Copyright © 2025 Michu Platform</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)