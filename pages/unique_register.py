import streamlit as st
           
# Main function to handle user sign-up
@st.dialog("Add Unique Customer")
def unique_register():
   
    username = st.session_state.get('username', 'username')
    with st.form(key = 'Create Account', clear_on_submit=True):
        # st.subheader('Add Customer')
        name_key = 'name_input'
        phone_key = 'phone_input'
        account_key = 'account_input'
        disbursed_key = 'collect_input'
        tin_key = 'tin_input'
        product_key = 'product_input'
        
        remark_key = 'remark_input'
        region_key = 'region_input'
        zone_key = 'zone_input'
        woreda_key = 'woreda_input'
        area_key = 'area_input'
        line_key = 'line_input'
        purpose_key = 'purpose_input'
        staff_key = 'staff_input'

        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name')
        product_type_options = ['Select Product', 'Guya', 'Wabi']
        product_type = st.selectbox('Product Type', options=product_type_options, key=product_key, index=0)

        phone_nmuber = st.text_input('Phone Number', key=phone_key, placeholder='Enter phone number')
        Saving_Account = st.text_input('Saving Account', key=account_key, placeholder='Enter Saving Account')
        tin_number = st.text_input('TIN Number', key = tin_key, placeholder='Enter tin number')
        disbursed_Amount = st.number_input('Disbursed Amount', key = disbursed_key, value=None, step=1.0, placeholder='Enter disbursed amount')
        region = st.text_input('Region', key = region_key, placeholder= 'Enter region of the business')
        zone = st.text_input('Zone/Sub-city', key = zone_key, placeholder= 'Enter Zone/Sub-city of the Business')
        woreda = st.text_input('Woreda', key = woreda_key, placeholder= 'Enter woreda of the business')
        specific_area = st.text_input('Specific Area', key = area_key, placeholder= 'Enter Specific Area of the business')
        line_of_business = st.text_input('Line of Business', key = line_key, placeholder= 'Enter Line of Business')
        purpose_of_loan = st.text_input('Purpose of Loan', key = purpose_key, placeholder= 'Enter Purpose of Loan')
        staff_name = st.text_input('Staff Name/recruiter', key = staff_key, placeholder= "Enter the Staff Name(recruiter)")
   
  
        
        remark = st.text_area('Remark', key = remark_key, placeholder='write remarks')
        # password2 = st.text_input('Confirm Password', key=confirm_password_key, placeholder='Confirm Your Password', type='password')
        # form_status = st.empty()

        col1,col3 = st.columns([0.8, 0.2])

        with col1:
            if st.form_submit_button(':blue[Register]'):
                from dependence import validate_phone, branchCustomer, validate_full_name, get_unquiephone, get_unquieaccount, validate_saving_account, get_conversionphone, get_conversionaccount, check_unique_phone, check_unique_account
                
                if product_type == 'Select Product':
                    st.error('Please select a Product.')
                elif not validate_full_name(name):
                    st.error('Please enter valid name (First name and father name)') 
                elif not validate_phone(phone_nmuber):
                    st.error('Please enter a valid phone number (use this format 09... or 07...)')
                elif not validate_saving_account(Saving_Account):
                    st.error('The saving account is not correct please try again')
                elif product_type == 'Wabi' and (not tin_number.strip() or len(tin_number) != 10 or not tin_number.isdigit()):
                    if not tin_number.strip():
                        st.error('Please enter a TIN number for Wabi product type.')
                    else:
                        st.error('The TIN number is incorrect; please enter again.')
                elif disbursed_Amount is None:
                    st.error('Please enter the disbursed amount')
                elif not region or not zone or not woreda or not specific_area or not line_of_business or not purpose_of_loan or not staff_name:
                    st.error("All fields are required. Please fill in all the fields.")
                elif phone_nmuber in get_unquiephone():
                    st.error('The phone number already exist, please enter correct phone number(new)')
                elif phone_nmuber in get_conversionphone():
                    st.error('The phone number is already listed in the conversion table, indicating that the customer has already used the product (it is not new or unique).')  
                elif check_unique_phone(phone_nmuber):
                    st.error("Phone number already exists in the database.")
                elif Saving_Account in get_unquieaccount():
                    st.error('The saving account already exist, please enter correct account (new)')
                elif Saving_Account in get_conversionaccount():
                    st.error('The saving account is already exist in the conversion table, indicating that the customer has already used the product (it is not new or unique).')
                elif check_unique_account(Saving_Account):
                    st.error("Saving Account already exists in the database.")

                else:
                    if branchCustomer(username, name, product_type, phone_nmuber, tin_number, Saving_Account, disbursed_Amount, region, zone, woreda, specific_area, line_of_business, purpose_of_loan, staff_name,  remark ):
                        st.success(f" {name} has been successfully registered!")
                    else:
                        st.error("Error, the entered data is not registered; please contact the administrator.")
                
