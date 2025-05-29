import streamlit as st
from pages.forgetpassword import registertion
from dependence import get_usernames, get_crmusernames


# Main function to handle user sign-up
@st.fragment
@st.dialog("Please write your username to proceed 👇🏻")
def register():
    """
    Handles the username input for resetting the password. 
    Verifies if the username exists in the system and then proceeds to the form for additional details.
    """
    
    # Initialize the user_name from session state
    user_name = st.session_state.get('username', '')
    
    # Display input for username first
    # st.markdown('<h3 style="color: #e38524;">Please write your username to proceed 👇🏻</h3>', unsafe_allow_html=True)
    
    username_key = 'username_input'
    user_name = st.text_input('User Name ✍️', key=username_key, placeholder='Enter your username')

    if st.button('Proceed'):
        
        try:
            # Clear session state for username before validation
            # st.session_state['username'] = None
            # Validation for empty input
            if not user_name.strip():
                st.warning('Please enter your username to proceed.')
            # Check if the username exists in either of the databases
            elif user_name not in get_usernames() and user_name not in get_crmusernames():
                st.warning('We do not have your username in our database. If you are new or can’t remember your username, please contact the administrator.')
    
            else:
                # Store the valid username in session state and proceed to the next step
                st.session_state['username'] = user_name
                st.success('Username verified! Please proceed to the next step.')
                
        except Exception as e:
            st.error(f"An error occurred while loading data: {e}")

    # Only show the form for reset details if the username has been verified
    if 'username' in st.session_state and st.session_state['username']:
        st.write('---')
        st.markdown('<h3 style="color: #e38524;">Fill out the following details to reset your password 👇🏻</h3>', unsafe_allow_html=True)
        registertion()  # Call the reset form
