import streamlit as st
from dependence import connect_to_database, validate_phone, conversion_customer, validate_full_name, validate_saving_account
from PIL import Image
from navigation import login_bar
from navigation import make_sidebar1
           
# Main function to handle user sign-up
def register():
    """
    Handles user sign-up process and form interactions.
    Resets input fields upon successful registration.
    """
    st.set_page_config(page_title="Michu form", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
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
    st.markdown(custom_cs, unsafe_allow_html=True)
    login_bar()
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
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
        <center> <h3 class = "title_dash">Michu Collection & Conversion Report Form </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    # if st.sidebar.button("GetData"):
    #     st.switch_page("pages/branch_dash.py")
                        
    make_sidebar1()
    username = st.session_state.get('username', 'username')
    with st.form(key = 'Create Account', clear_on_submit=True,  border=True):
        st.subheader('Add Customer')
        name_key = 'name_input'
        product_key = 'product_input'
        phone_key = 'phone_input'
        account_key = 'account_input'
        collect_key = 'collect_input'
        borrowed_key = 'borrowed_input'
        remark_key = 'remark_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name')
        product_type_options = ['Select Product', 'Guya', 'Wabi', 'Women-Informal (Guya)', 'Women-Formal (Wabi)']
        product_type = st.selectbox('Product Type', options=product_type_options, key=product_key, index=0)
        phone_nmuber = st.text_input('Phone Number', key=phone_key, placeholder='Enter phone number')
        Saving_Account = st.text_input('Saving Account', key=account_key, placeholder='Enter Saving Account')
        collected_Amount = st.number_input('Collected Amount', key = collect_key, value=None, step=1.0, placeholder='Enter collected amount')
        amount_borrowed_again = st.number_input('Amount Borrowed Again', key = borrowed_key, value=None, step=1.0, placeholder='Enter amount borrowed again')
        remark = st.text_area('Remark', key = remark_key, placeholder='write remarks')
        # password2 = st.text_input('Confirm Password', key=confirm_password_key, placeholder='Confirm Your Password', type='password')
        # form_status = st.empty()

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':blue[Register]', help="Click to register"):
                mydb = connect_to_database()
                if mydb is not None:
                    cursor = mydb.cursor()
                    if product_type == 'Select Product':
                        st.warning('Please select a Product.')
                    elif not validate_phone(phone_nmuber):
                        st.error('Please enter a valid phone number (use this format 09... or 07...)')
                    elif not validate_full_name(name):
                        st.error('Please enter valid name (First name and father name)') 
                    elif not validate_saving_account(Saving_Account):
                        st.error('The saving account is not correct please try again')
                    elif collected_Amount is None:
                        st.warning('Please enter the collected amount')
                    elif amount_borrowed_again is None:
                        st.warning('Please enter the amount borrowed again')
                    
                    else:
                        if conversion_customer(mydb, cursor, username, name, product_type, phone_nmuber, Saving_Account, collected_Amount, amount_borrowed_again,remark ):
                            st.success(f" {name} has been successfully registered!")
                        else:
                            st.error("Failed to register the customer. Please try again.")
                    cursor.close()
                    mydb.close()
       
        # with col3:
        #     if st.form_submit_button("LogOut"):
        #         sleep(0.5)
        #         st.switch_page('main.py')
        

if __name__ == '__main__':
    # make_sidebar()
    register()