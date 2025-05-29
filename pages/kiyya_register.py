import streamlit as st
from datetime import date
import requests
import traceback
import json



# Main function to handle user sign-up
@st.dialog("Add Kiyya Informal Customer")
def kiyya_register():
    username = st.session_state.get("username", "")
    # full_name = st.session_state.get("full_name", "")



    with st.form(key='customer_form', clear_on_submit= True):
        name_key = 'name_input'
        phone_key = 'phone_input'
        account_key = 'account_input'
        id_key = 'id_input'
        gender_key = 'gender_input'
        marital_key = 'marital_input'
        birth_key = 'birth_input'
        region_key = 'region_input'
        zone_key = 'zone_input'
        woreda_key = 'woreda_input'
        educational_key = 'educational_input'
        economic_key = 'economic_input'
        line_key = 'line_input'
        initial_key = 'initial_input'
        source_key = 'source_input'
        daily_key = 'daily_input'
        purpose_key = 'purpose_input'
        # recu_key = 'recu_input'



        name = st.text_input('Full Name', key=name_key, placeholder='Enter  Full Name').strip()
        phone_nmuber = st.text_input('Phone Number', key=phone_key, placeholder='Enter phone number').strip()
        Saving_Account = st.text_input('Saving Account', key=account_key, placeholder='Enter Saving Account').strip()

        # Customer Identification Type
        customer_id_type = st.selectbox("Customer Identification Type", ["Select Id Type", "Kebele ID", "National ID", "Passport", "Driver's License"], key=id_key).strip()

        # Gender
        gender = st.selectbox("Gender", ["Female"], key=gender_key).strip()

        # Marital Status
        marital_status = st.selectbox("Marital Status", ["Select Marital Status", "Unmarried", "Married", "Divorced", "Widowed"], key=marital_key).strip()

        # Date of Birth
        date_of_birth = st.date_input(
        "Date of Birth",
        value=None,  # No default date selected
        min_value=date(1900, 1, 1),  # Earliest date selectable
        max_value=date.today(),  # Latest date selectable
        key=birth_key
        )
        # Customer Address
        region = st.selectbox("Region", ["Select region", 'ADDIS_ABABA', 'AFAR', 'AMHARA', 'TIGRAY', 'BENISHANGUL_GUMUZ', 'GAMBELA', 'OROMIA', 'SIDAMA', 'SOMALI', 'SNNP', 'SWEP', 'HARAR', 'DIRE_DAWA'], key=region_key).strip()
        zone_subcity = st.text_input("Zone/Subcity", placeholder="Enter Zone/Subcity", key=zone_key).strip()
        woreda = st.text_input("Woreda", placeholder="Enter Woreda", key=woreda_key).strip()

        # Educational Level
        educational_level = st.selectbox("Educational Level",["Select Educational Level", "Primary", "Diploma", "Bachelors Degree", "Masters Degree", "PHD and above"], key=educational_key).strip()

        # Economic Sector
        economic_sector = st.selectbox("Business Sector", ["Select Business Sector", "Agriculture", "Manufacturing", "Domestic Trade Service", "Building and Construction"], index=0, key=economic_key).strip()

        # Line of Business
        line_of_business = st.text_input("Line of Business", placeholder=" Enter Line of Business", key=line_key).strip()

        # Initial Working Capital
        initial_working_capital = st.number_input("Initial Working Capital", key = initial_key, value=None, min_value=2000.0, max_value=100000.0, step=1.0, placeholder='Enter Initial Working Capital')

        # Source of Initial Capital
        source_of_initial_capital = st.selectbox("Source of Initial Capital", ["Select Source of Initial Capital", "Family", "Own", "Fund", "Loan"], key=source_key).strip()

        # Daily Sales
        monthly_income = st.number_input("Monthly Income", key = daily_key, value=None, step=1.0, placeholder='Enter Monthly Income')

        # Purpose of the Loan
        purpose_of_loan = st.text_area("Purpose of the Loan", placeholder="Write purpose of the loan", key=purpose_key).strip()
        # Recruited_by = st.text_area("Recuited by", placeholder="Write recuited person", key=recu_key).strip()
       
    
        def set_session_state(account_number, eligible, phone_number, total_score):
            st.session_state['accountNumber'] = account_number
            st.session_state['eligible'] = eligible
            st.session_state['phoneNumber'] = phone_number
            st.session_state['total_score'] = total_score

        if isinstance(date_of_birth, date):
            date_of_birth = date_of_birth.strftime('%Y-%m-%d')

        col1, _ = st.columns([0.8, 0.2])
        
        with col1:
            if st.form_submit_button(':blue[Register]'):
                from dependence import validate_phone, validate_full_name, get_unquiedureatphone, validate_saving_account, check_durationunique_account, kiyya_customer, get_unquiedkiyyaphone # kiyya_customer_notegible
                # Validate form inputs
                if customer_id_type == "Select Id Type":
                    st.error("Please select a valid Customer Identification Type.")
                elif marital_status == "Select Marital Status":
                    st.error("Please select a valid Marital Status.")
                elif region == "Select region":
                    st.error("Please select a valid Region.")
                elif educational_level == "Select Educational Level":
                    st.error("Please select a valid Educational Level.")
                elif economic_sector == "Select Business Sector":
                    st.error("Please select a valid Business Sector.")
                elif source_of_initial_capital == "Select Source of Initial Capital":
                    st.error("Please select a valid Source of Initial Capital.")
                # Check if the user has entered a value for Daily Sales
                elif initial_working_capital is None or initial_working_capital == 0.00:
                    st.error("Please enter a valid initial working capital amount.")
                elif monthly_income is None or monthly_income == 0.00:
                    st.error("Please enter a valid Daily Sales amount.")
                # Check if the date is selected (mandatory check)
                elif not date_of_birth:
                    st.error("Please select your Date of Birth.")

                elif not validate_full_name(name):
                    st.error('Please enter valid name (First name and father name)') 
                elif not validate_phone(phone_nmuber):
                    st.error('Please enter a valid phone number (use this format 09... or 07...)')
                elif not validate_saving_account(Saving_Account):
                    st.error('The saving account is not correct please try again')
                elif phone_nmuber in get_unquiedureatphone():
                    st.error('The phone number already exist, please enter correct phone number(new)')
                elif phone_nmuber in get_unquiedkiyyaphone():
                    st.error('The phone number already exist, please enter correct phone number(new)')
                elif check_durationunique_account(Saving_Account):
                    st.error('The saving account is already exist, indicating that the customer has already used the product (it is not new or unique).')
                elif not region or not zone_subcity or not woreda or not educational_level or not economic_sector or not line_of_business or not purpose_of_loan:
                    st.error("All fields are required. Please fill in all the fields.")

                else:
                    # # Prepare API payload
                    # payload = {
                    #     "account_number": Saving_Account,
                    #     "phone_number": phone_nmuber,
                    #     "gender": gender,
                    #     "marital_status": marital_status,
                    #     "date_of_birth": date_of_birth,
                    #     "educational_level": educational_level,
                    #     "economic_sector": economic_sector,
                    #     "initial_working_capital": initial_working_capital,
                    #     "source_of_initial_capital": source_of_initial_capital,
                    #     "daily_sales": monthly_income
                    # }

                    # headers = {"Content-Type": "application/json"}


                    # try:
                    #     response = requests.post(
                    #         "http://10.12.53.30:6060/michu_kiya_scorecard/V1.0.0",
                    #         headers=headers,
                    #         json=payload
                    #     )

                    #     if response.status_code == 200:
                    #         data = response.json()
                    #         if data.get("status") == "success":
                    #             set_session_state(
                    #                 account_number=data.get("accountNumber"),
                    #                 eligible=data.get("eligible"),
                    #                 phone_number=data.get("phoneNumber"),
                    #                 total_score=data.get("total_score")
                    #             )

                    #             if data.get("eligible"):
                    if kiyya_customer(username, name, phone_nmuber, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan):
                        st.success(f"{name} has been successfully registered!")
                    else:
                        st.error("Error: The entered data is not registered. Please contact the administrator.")
                    #             else:
                    #                 if kiyya_customer_notegible(username, name, phone_nmuber, Saving_Account, customer_id_type, gender, marital_status, date_of_birth, region, zone_subcity, woreda, educational_level, economic_sector, line_of_business, initial_working_capital, source_of_initial_capital, monthly_income, purpose_of_loan, data.get("phoneNumber"), data.get("accountNumber"), data.get("total_score"), False):
                    #                     st.error(f"{name} Customer is uneligible for the product due to insufficient customer history.")
                    #                 else:
                    #                     st.error("Error: The entered data is not registered. Please contact the administrator.")
                    #         else:
                    #             st.error(data.get("error", "An unexpected error occurred."))
                    #     elif response.status_code == 400:
                    #         data = response.json()
                    #         error_message = f"{data.get('error', 'Bad request.')}. Please enter the correct account number."
                    #         st.error(error_message)
                    #     else:
                    #         st.error(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
                    # except requests.exceptions.RequestException as e:
                    #     st.error("An error occurred while connecting to the API. Please try again later.")
                    #     traceback.print_exc()

                        