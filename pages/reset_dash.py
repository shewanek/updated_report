import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from PIL import Image
from dependence import load_resetpassword, update_password
from navigation import home_sidebar

def filter_by_date(df, date_col, label):
    """
    Function to filter dataframe by date range.
    Args:
        df (pd.DataFrame): Dataframe to filter.
        date_col (str): Name of the date column to filter on.
        label (str): Label for the date input.

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    col1, col2,col3,col4 = st.columns([0.2, 0.4, 0.2, 0.2])
    start_date = df[date_col].min()
    end_date = df[date_col].max()

    with col1:
        start_date_input = st.date_input(f"Start Date", start_date, key=f"start_{label}")
    with col3:
        end_date_input = st.date_input(f"End Date", end_date, key=f"end_{label}")

    filtered_df = df[(df[date_col] >= start_date_input) & (df[date_col] <= end_date_input)].copy()
    return filtered_df

def main():
    # Custom CSS to change button hover color to cyan blue
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
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    with open('custom.css') as f:
        st.write(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Auto-refresh interval (in seconds)
    refresh_interval = 600  # Adjust as needed (e.g., 10 minutes for real-time)
    st_autorefresh(interval=refresh_interval * 1000, key="Michu Bot dash")

    image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image)
    html_title = """
        <style>
        .title_dash {
            font-weight:bold;
            padding:1px;
            border-radius:6px
        }
        </style>
        <center> <h3 class="title_dash"> Michu Reset Password Report </h3> </center>
    """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)

    st.balloons()

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
        
    try:
        df = load_resetpassword()

        # Sidebar
        st.sidebar.image("pages/michu.png")
        username = st.session_state.get("username", "")
        full_name = st.session_state.get("full_name", "")
        # st.sidebar.write(f'Welcome, :orange[{full_name}]')
        st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

        # Hide the sidebar by default with custom CSS
        hide_sidebar_style = """
            <style>
                #MainMenu {visibility: hidden;}
            </style>
        """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)
        home_sidebar()
        st.markdown(custom_cs, unsafe_allow_html=True)
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

        # col1, col2, col3 = st.columns(3)
        # col1.metric(label="***Total Targeted Women***", value=dureti_customer['customerId'].nunique(), delta="Registered Customer")
        # col2.metric(label="***Total New/Unique Customer***", value=unique_customer['uniqueId'].nunique(), delta="Registered Customer")
        # col3.metric(label="***Total Conversion Customer***", value=conversion_customer['ConversionId'].nunique(), delta="Registered Customer")
        # style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

        st.markdown("""
        <style>
            [data-testid="stElementToolbar"] {
            display: none;
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<p style="color: #00adef;">List of Users Requesting Password Resets 👇🏻</p>', unsafe_allow_html=True)
        # Filtering conversion_customer
        # Convert date_column to datetime format
        # df['Asked Date'] = pd.to_datetime(df['Asked Date'])
        

        # Calculate the date three days ago from today
        three_days_ago = datetime.now().date() - timedelta(days=3)

        # Filter the DataFrame to keep only rows with dates within the last three days
        df = df[df['Asked Date'] > three_days_ago]
        columns=['full Name', 'user name', 'outlook email','District/Branch','Asked Date']
        
        if df is not None and not df.empty:
            df = filter_by_date(df, "Asked Date", "Conversion Customer")
            # st.write(conversion_customer[conversion_columns])
            st.write(df[columns].reset_index(drop=True).rename(lambda x: x + 1))
            usernames = df['user name'].tolist()
            # if st.button(':orange[Click here to reset the user password]'):
            with st.form(key='change_password', clear_on_submit=True):
                st.subheader(':orange[Reset user password]')
                user_name = st.text_input('User\'s username', placeholder='Enter user\'s Username')
                new_password = st.text_input('New Password', placeholder= f'Enter a new password for the requested user.', type='password')
                confirm_password = st.text_input('Confirm New Password', placeholder='Enter a new password for the requested user', type='password')

                col1,col2 = st.columns([0.7, 0.3])
                with col1:
                    if st.form_submit_button(':orange[Reset Password]'):
                        # conn = connect_to_database()
                        try:
                            if not user_name.strip():
                                st.error('Please enter the user\'s username')
                            elif user_name in usernames:
                                # st.write(user_name)
                                if not new_password.strip():
                                    st.error('Please enter the new Password')
                                elif new_password == confirm_password:
                                    update_password(user_name, new_password)
                                    st.success('Password was successfully reseted!')
                                    # info_message = '''
                                    # NB: Don't forget to send the reset password for the user using your Outlook email to his corresponding email address on the above table. 
                                    # [Click here to open Outlook](https://mail.coopbankoromiasc.com/)
                                    # '''
                                    # st.info(info_message)
                                    info_message = '''
                                    <p style = " color:#00adef;"> NB: Don't forget to send the reset password for the user using your Outlook email to his corresponding email address on the above table.</p> 
                                    <a href="https://mail.coopbankoromiasc.com/" style="color: orange;">Click here to open Outlook</a>
                                    '''

                                    st.markdown(info_message, unsafe_allow_html=True)
                                    # st.info('NB: Don\'t forget to send the reset password for the user using your Outlook email to his corresponding email address on the above table.')
                                else:
                                    st.error('New password and confirmation do not match.')
                            else:
                                st.error('User not present in the table above. The requested user\'s username must to exist in the above table in order for the password to be reset.')
                        except Exception as e:
                            st.error(f"An error occurred while loading data: {e}")
        else:
            st.write(':orange[No user requested a password reset for this consecutive three-day]')
            st.info('NB: This portal only displays users who have made requests during the last three days. If a user made a request before three days, he or she must make another request to reset')
        
        
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        # sleep(3)

if __name__ == "__main__":
    main()
