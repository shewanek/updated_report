import streamlit as st


# Main function to handle user sign-up
# @st.dialog("Send us the following information to reset you password")
def registertion():

    col1, col2 = st.columns([0.1,0.9])

    username = st.session_state.get('username', '')
    # st.write(username)
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("No user found with the given username.")
        st.switch_page("main.py")
    # login_bar()   
    with st.form(key = 'Create forget password', clear_on_submit=True):
        # st.write('Send us the following information to reset you password')
        # st.markdown('<h3 style="color: #e38524;">Send us the following information to reset you password 👇🏻</h3>', unsafe_allow_html=True)
        name_key = 'name_input'
        email = 'email_input'
        branch = 'region_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name')
        outlook_email = st.text_input('Outlook Email', key=email, placeholder='Enter your outlook email')
        branch_name = st.text_input('District/Branch', key = branch, placeholder='Enter your district or branch')
        

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':orange[Send]'):
                from dependence import insert_resetpuser, validate_full_name, validate_email, has_user_sent_request_today
                try:
                    if not validate_full_name(name):
                        st.warning('Please enter valid name (First name and father name)') 
                    elif not validate_email(outlook_email):
                        st.warning('Please enter a valid email address (Your Outlook email)')
                    elif not branch_name.strip():
                        st.warning('Please provide your district name if you are from CBO district, or your branch name if you are from CBO branch.')
                    else:
                        # Check if user has already sent a request today
                        if has_user_sent_request_today(username):
                            st.warning('You have already submitted a reset request. Please check your Outlook email; we will send it to you; please wait patiently.')
                    
                        else:  
                            if insert_resetpuser(username, name, outlook_email, branch_name):
                                st.success(f"Your password reset request (for {username} user name) was received successfully!. We sent you the reset password via Outlook email; check your inbox after an hour.")
                                # sleep(5)
                                # st.switch_page("main.py")
                except Exception as e:
                    st.error(f"An error occurred while loading data: {e}")
        # with col3:
        #     if st.form_submit_button(':orange[Log In]'):
        #         sleep(0.5)
        #         st.switch_page("main.py")
       
        

# if __name__ == '__main__':
    
#     register()