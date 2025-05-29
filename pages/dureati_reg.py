import streamlit as st
          
# Main function to handle user sign-up
@st.dialog("Add Kiyya Formal Customer")
def registerr():
    # username = st.session_state.get("username", "")
    # full_name = st.session_state.get("full_name", "")
    
    with st.form(key = 'Create Account', clear_on_submit=True):
        # st.subheader('Add Customer')
        name_key = 'name_input'
        phone_key = 'phone_input'
        account_key = 'account_input'
        disbursed_key = 'collect_input'
        
        remark_key = 'remark_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name').strip()
        # product_type_options = ['Select Product', 'Guya', 'Wabi']
        # product_type = st.selectbox('Product Type', options=product_type_options, key=product_key, index=0)

        phone_nmuber = st.text_input('Phone Number', key=phone_key, placeholder='Enter phone number').strip()
        Saving_Account = st.text_input('Saving Account', key=account_key, placeholder='Enter Saving Account').strip()
        # tin_number = st.text_input('TIN Number', key = tin_key, placeholder='Enter tin number')
        disbursed_Amount = st.number_input('Disbursed Amount', key = disbursed_key, value=None, step=1.0, placeholder='Enter disbursed amount')
        
        
   
  
        
        remark = st.text_area('Remark', key = remark_key, placeholder='write remarks')
        # password2 = st.text_input('Confirm Password', key=confirm_password_key, placeholder='Confirm Your Password', type='password')
        # form_status = st.empty()

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':blue[Register]'):
                from dependence import validate_phone, womenCustomer, validate_full_name, get_unquiedureatphone, validate_saving_account, check_durationunique_account, get_unquiedkiyyaphone
                if not validate_full_name(name):
                    st.error('Please enter valid name (First name and father name)') 
                elif not validate_phone(phone_nmuber):
                    st.error('Please enter a valid phone number (use this format 09... or 07...)')
                elif not validate_saving_account(Saving_Account):
                    st.error('The saving account is not correct please try again')
                elif phone_nmuber in get_unquiedureatphone():
                    st.error('The phone number already exist, please enter correct phone number(new)')
                elif phone_nmuber in get_unquiedkiyyaphone():
                    st.error('The phone number already exist, please enter correct phone number(new)')
                # elif Saving_Account in get_unquieaccount(cursor):
                #     st.error('The saving account already exist, please enter correct account (new)')
                # elif Saving_Account in get_conversionaccount(cursor):
                #     st.error('The saving account is already exist in the conversion table, indicating that the customer has already used the product (it is not new or unique).')
                elif check_durationunique_account(Saving_Account):
                    st.error('The saving account is already exist, indicating that the customer has already used the product (it is not new or unique).')
                elif disbursed_Amount is None:
                    st.error('Please enter the disbursed amount')

                else:
                    
                    if womenCustomer(name, phone_nmuber, Saving_Account, disbursed_Amount, remark):
                        st.success(f" {name} has been successfully registered!")
                    else:
                        st.error("Error, the entered data is not registered; please contact the administrator.")
                   
       