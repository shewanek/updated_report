import streamlit as st
from dependence import connect_to_database, validate_phone, insert_customer, validate_full_name, get_duretiphone, get_duretiacount, validate_saving_account
from PIL import Image
from navigation import login_bar
from navigation import make_sidebar1
           
# Main function to handle user sign-up
def register():
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
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    login_bar()
    st.markdown(custom_cs, unsafe_allow_html=True)
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
        <center> <h3 class = "title_dash">Michu Women Targeted Registration Form </h3> </center>
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
    with st.form(key = 'Create Account', clear_on_submit=True):
        st.subheader('Add Customer')
        name_key = 'name_input'
        product_key = 'product_input'
        phone_key = 'phone_input'
        account_key = 'account_input'
        region = 'region_input'
        Woreda = 'woreda_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name')
        product_type_options = ['Select Product', 'Women-Informal (Guya)', 'Women-Formal (Wabi)']
        product_type = st.selectbox('Product Type', options=product_type_options, key=product_key, index=0)
        phone_nmuber = st.text_input('Phone Number', key=phone_key, placeholder='Enter phone number')
        Saving_Account = st.text_input('Saving Account', key=account_key, placeholder='Enter Saving Account')
        Region = st.text_input('Region', key = region, placeholder='Enter region')
        Woreda = st.text_input('Zone/sub city/ Woreda', key = Woreda, placeholder='Enter Zone/sub city/Woreda')
        # password2 = st.text_input('Confirm Password', key=confirm_password_key, placeholder='Confirm Your Password', type='password')
        # form_status = st.empty()

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':blue[Register]'):
                mydb = connect_to_database()
                if mydb is not None:
                    cursor = mydb.cursor()
                    
                    # Validate inputs and close resources early if invalid
                    if not validate_full_name(name):
                        st.warning('Error, Please enter valid name (First name and father name)') 
                        cursor.close()
                        mydb.close()
                    
                    elif product_type == 'Select Product':
                        st.warning('Please select a Product.')
                        cursor.close()
                        mydb.close()
                    
                    elif not validate_phone(phone_nmuber):
                        st.warning('Error, Please enter a valid phone number (use this format 09... or 07...)')
                        cursor.close()
                        mydb.close()
                    
                    elif not validate_saving_account(Saving_Account):
                        st.warning('Error, The saving account is not correct please try again')
                        cursor.close()
                        mydb.close()
                    
                    elif phone_nmuber in get_duretiphone(cursor):
                        st.warning('Error, The phone number already exists, please enter a correct phone number (new)')
                        cursor.close()
                        mydb.close()
                    
                    elif Saving_Account in get_duretiacount(cursor):
                        st.warning('Error, The saving account already exists, please enter a correct account (new)')
                        cursor.close()
                        mydb.close()
                    
                    elif not Region.strip():
                        st.warning('Error, Please enter the region')
                        cursor.close()
                        mydb.close()
                    
                    elif not Woreda.strip():
                        st.warning('Error, Please enter Zone/sub city/ Woreda')
                        cursor.close()
                        mydb.close()
                    
                    # If all validations pass, insert the customer
                    else:
                        if insert_customer(mydb, cursor, username, name, product_type, phone_nmuber, Saving_Account, Region, Woreda):
                            st.success(f"{name} has been successfully registered!")
                    
                    # Close resources after successful registration
                    cursor.close()
                    mydb.close()

       
        # with col3:
        #     if st.form_submit_button("LogOut"):
        #         sleep(0.5)
        #         st.switch_page('main.py')
        

if __name__ == '__main__':
    # make_sidebar()
    register()