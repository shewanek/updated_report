import streamlit as st
import pandas as pd
import requests

import time
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, AgGridTheme
from dependence import connect_to_database, get_branch_code, get_dis_and_branch
# branch_user=False
# user=branch_user
mydb = connect_to_database()
def role_fetch():
    mydb = connect_to_database()
    if mydb is not None:
        # cursor = mydb.cursor()
        branch_code, role = get_branch_code(mydb)
        # st.write("the erro", get_branch_code(mydb))
        # print(role, "role of mydb")

        # list_branchcode= branch_code
        return branch_code, role
dis_branch = get_dis_and_branch(mydb)


# branch_code, role = role_fetch()
# list_branchcode = branch_code

def initialize_session():
    if 'data' not in st.session_state:
        st.session_state.data = []
    if 'edit_row' not in st.session_state:
        st.session_state.edit_row = None
    if "selectedRow" not in st.session_state:
        st.session_state.selectedRow=None
# branch=True

# if role == 'Branch User':
#     user=True
#     # st.write(f"under if of add collection data, {role}")
# else:
#     user = False
#     # st.write(f"under else of add collection data, {role}")

def fetch_data():
    try:
        response = requests.get("http://127.0.0.1:8000/loan/branchCustomer", params={"branch_code": "ET0010328"})
        response.raise_for_status()
        st.session_state.data = response.json()
    except requests.exceptions.HTTPError as http_err:
        print("An error", http_err)
        st.error("Unable to load data")
    except Exception as err:
        print("An error",  err)
        st.error("Something went wrong")

def update_data(record):
    try:
        response = requests.post("http://127.0.0.1:8000/loan/collection", json=record)
        response.raise_for_status()
        st.success("Data updated successfully!")
        st.session_state.selectedRow=None
        time.sleep(2)
        st.rerun()
    except requests.exceptions.HTTPError as http_err:
        print("An error", http_err)
        st.error("Unable to update data")
    except Exception as err:
        print("An error", err)
        st.error("Something went wrong")


def fetchActiveData(data):
    try:
        result=requests.post("http://127.0.0.1:8000/loan/activeBranchCustomer", json=data)  
        result.raise_for_status()
        st.session_state.data=result.json()
    except requests.exceptions.HTTPError as errors:
        print("An error", errors)
        st.error("Unable to load data")
    except Exception as excep:
        print("An error", excep)
        st.error("Something went wrong")


def updatePaidAmount():
    st.session_state.selectedRow["paid_amount"] = st.session_state.paid_amount


# Customer Data Dialog
@st.dialog("You are updating the customer loan")
def customerData():
    loanStatOption = ["Closed", "Active", "In Arrears"]
    applicationStatus = ["ACTIVE", "CLOSED"]

    st.subheader(f"__You are updating data of__ :blue[ {st.session_state.selectedRow['customer_name']}]")
    st.markdown(f" *Saving Account =* ***{st.session_state.selectedRow['saving_account']}***")
    st.markdown(f" *Phone number =* ***{st.session_state.selectedRow['phone_number']}***")
    st.markdown(f" *Approved amount =* **{st.session_state.selectedRow['approved_amount']}**")

    st.markdown(f" *Application status=* **{st.session_state.selectedRow['application_status']}**")
    st.markdown(f" *Loan status=* **{st.session_state.selectedRow['loan_status']}**")
    st.markdown(f" *Outstanding_total=* **{st.session_state.selectedRow['oustanding_total']}**")

    st.number_input("Paid Amount", value= float(st.session_state.selectedRow["paid_amount"]), on_change=updatePaidAmount, key="paid_amount")

    if st.button("Save"):
        update_data(st.session_state.selectedRow)



#List of branch code and loan status to be accessed
# Display Logic Based on Selected Tab
def InArrearsData(list_branchcode):
    branchCodeLoanStatus={"branch_code": list_branchcode,"loan_status": "In Arrears"} 
    initialize_session()
    fetchActiveData(branchCodeLoanStatus)
    if st.session_state.data:
        st.subheader("Your Branch Loan Detail")
        datas = st.session_state.data
        df = pd.DataFrame(datas)
        df_merged = pd.merge(df, dis_branch, on='branch_code', how='inner')
        # st.write(df_merged)
        columns_to_display = ["cust_id", "District", "Branch", "customer_name","phone_number","saving_account","approved_amount", "oustanding_total",
                            "application_status","loan_status","approved_date","expiry_date"]
        
        selectedDataFrame = df_merged[columns_to_display]
        # st.write(selectedDataFrame)

        gb = GridOptionsBuilder.from_dataframe(selectedDataFrame)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_default_column(editable=True)
        gb.configure_grid_options(rowHeight=40)
        cell_style = {'font-size': '16px', 'padding': '10px'}
        gb.configure_default_column(cellStyle=cell_style)
        gb.configure_selection("single")
        gb.configure_grid_options(enableSorting=True, enableFilter=True, enableColResize=True)
        grid_options = gb.build()

        response = AgGrid(df_merged, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=True, theme=AgGridTheme.STREAMLIT)


        selected_rows = response.get("selected_rows", None)
        # if user:
        if selected_rows is not None and len(selected_rows)>0:
            selected_row = selected_rows.iloc[0] 
            selected_row_dict = selected_row.to_dict() if isinstance(selected_row, pd.Series) else selected_row
            selected_row_dict["paid_amount"]=0
            selected_row_dict["remark"]="Not given"
            selected_row_dict["collectionStatus"]="Pending"
            st.session_state.selectedRow = selected_row_dict
            customerData()


def InArrearsData_col(branch_code):
    initialize_session()
    branchCodeLoanStatus={"branch_code": branch_code,"loan_status": "In Arrears"} 
    fetchActiveData(branchCodeLoanStatus)
    if st.session_state.data:
        st.subheader("Your Branch Loan Detail")
        datas = st.session_state.data
        # df_merged = pd.merge(df, dis_branch, on='branch_code', how='inner')

        df = pd.DataFrame(datas)
        df_merged = pd.merge(df, dis_branch, on='branch_code', how='inner')
        # st.write(df)
        columns_to_display = ["cust_id","District", "Branch", "customer_name","phone_number","saving_account","approved_amount", "oustanding_total",
                            "application_status","loan_status","approved_date","expiry_date"]
        selectedDataFrame = df_merged[columns_to_display]
        st.dataframe(selectedDataFrame, use_container_width=True)
        # gb = GridOptionsBuilder.from_dataframe(selectedDataFrame)
        # gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        # gb.configure_default_column(editable=True)
        # gb.configure_grid_options(rowHeight=40)
        # cell_style = {'font-size': '16px', 'padding': '10px'}
        # gb.configure_default_column(cellStyle=cell_style)
        # gb.configure_selection("single")
        # gb.configure_grid_options(enableSorting=True, enableFilter=True, enableColResize=True)
        # grid_options = gb.build()

        # response = AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=True, theme=AgGridTheme.STREAMLIT)


        # selected_rows = response.get("selected_rows", None)
        # if user:
        #     if selected_rows is not None and len(selected_rows)>0:
        #         selected_row = selected_rows.iloc[0] 
        #         selected_row_dict = selected_row.to_dict() if isinstance(selected_row, pd.Series) else selected_row
        #         selected_row_dict["paid_amount"]=0
        #         selected_row_dict["remark"]="Not given"
        #         selected_row_dict["collectionStatus"]="Pending"
        #         st.session_state.selectedRow = selected_row_dict
        #         customerData()

def arrears_acess(branch_code, role):
    if role == 'Branch User':
        user = True
        # st.write(f"under if of collection data, {role}")
    else:
        user = False
    if user:
        InArrearsData(branch_code)
        # st.write("The user is branch InArrearsData() so arreadr si clickable")
        # st.write(role)
    else:
        InArrearsData_col(branch_code)
        # st.write ("the user is not branch  InArrearsData_col()  not clickable")
        # st.write(role)