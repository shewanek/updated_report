import streamlit as st
from datetime import datetime, timedelta
# from navigation import home_sidebar

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
@st.dialog("Please Reset the following request 👇🏻")
def resetpassword():

        
    try:
        from dependence import load_resetpassword
        df = load_resetpassword()


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
                        from dependence import update_password
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

# if __name__ == "__main__":
#     main()
