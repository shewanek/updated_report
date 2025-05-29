import streamlit as st


# Main function to handle user sign-up
@st.dialog("Change your Password")
def forget_password():
   
    with st.form(key='change_password'):
        # st.subheader('Change Password')
        current_password = st.text_input('Current Password', type='password')
        new_password = st.text_input('New Password', type='password')
        confirm_password = st.text_input('Confirm New Password', type='password')

        col1, col2 = st.columns([0.9, 0.1])
        username = st.session_state.get("username", "")
        # st.write(username)
        password = st.session_state.get("password", "")
    

        with col1:
            if st.form_submit_button('Change Password'):
                try:
                    from dependence import update_password
                    if not current_password.strip():
                        st.error('Please enter your current password')
                    elif current_password == password:
                        if not new_password.strip():
                            st.error('Please enter new password')
                        elif len(new_password) < 6:
                            st.error('Password must be at least 6 characters long.')
                        elif new_password == confirm_password:
                            update_password(username, new_password)
                            st.success('Password was successfully changed! Click the Login button to login again.')
                        else:
                            st.error('New password and confirmation do not match.')
                    else:
                        st.error('Incorrect current password.')
                
                except Exception as e:
                    st.error(f"An error occurred while loading data: {e}")
        

# if __name__ == '__main__':
#     # make_sidebar()
#     forget_password()