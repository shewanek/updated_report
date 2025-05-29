
import streamlit as st
import pandas as pd
import requests

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, AgGridTheme
from dependence import connect_to_database, get_branch_code, get_dis_and_branch
import time

# branch_user = True
# user = branch_user 

mydb = connect_to_database()
def role_fetch():
    if mydb is not None:
        # cursor = mydb.cursor()
        if get_branch_code(mydb) is not None: 
            branch_code, role = get_branch_code(mydb)
        # print(role, "role of mydb")

        # list_branchcode= branch_code
            return branch_code, role
        else:
            return None

dis_branch = get_dis_and_branch(mydb)

# branch_code, role = role_fetch()
# list_branchcode = branch_code


# # branch=True
# if role == 'Branch User':
#     user = True
#     # st.write(f"under if of collection data, {role}")
# else:
#     user = False
    # st.write(f"under else of collection data, {role}")
    

# user=branch

def initialize_session():
    if "selectedRow" not in st.session_state:
        st.session_state.selectedRow=None
    if "collectionDatas" not in st.session_state:
        st.session_state.collectionDatas=[]

    if "collectionSelection" not in st.session_state:
        st.session_state.collectionSelection=None

def fetchCollectionData(branchCodes):
    try:
        response=requests.post("http://127.0.0.1:8000/loan/collectionDatas", json=branchCodes)
        response.raise_for_status()
        st.session_state.collectionDatas=response.json()
    except requests.exceptions.HTTPError as ero:
        print(f"Http error occurred: {ero}")
        st.error("Unable to load data")
    except Exception as err:
        print("The Error__---",err)
        st.error("Something went wrong:")
def confirmationRequest(updatingData):
    try:
        result=requests.patch("http://127.0.0.1:8000/loan/collectionConfirmation", 
                            json=updatingData)
        result.raise_for_status()
        st.success("Collection status is change successfully")
        time.sleep(2)
        st.rerun()
    except requests.exceptions.HTTPError as error:
        print("An error", error)
        st.error(f"Un able to change collection status")
    except Exception as err:
        print("An error",err)
        st.error("Something went wrong")

def collectionManagement():
    if st.session_state.collectionDatas:
        st.subheader("Your Branch Loan Collection Status")
        datas = st.session_state.collectionDatas
        # if st.session_state.district:

        df = pd.DataFrame(datas)
        df_merged = pd.merge(df, dis_branch, on='branch_code', how='inner')

        columns_to_display = ["cust_id", "District", "Branch", "customer_name","phone_number","saving_account","approved_amount", "oustanding_total","paid_amount",
                            "application_status","loan_status","collectionStatus", "remark","approved_date","expiry_date"]
        selectedDataFrame = df_merged[columns_to_display]
        gb = GridOptionsBuilder.from_dataframe(selectedDataFrame)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_default_column(editable=False)
        gb.configure_grid_options(rowHeight=40)
        cell_styles={"font-size":"14px", "padding":"8px"}
        gb.configure_default_column(cellStyle=cell_styles)
        gb.configure_selection("single")
        gb.configure_grid_options(enableSorting=True, enableFilter=True, enableColResize=True)
        grid_options = gb.build()

        collectionResponse = AgGrid(df_merged, 
                                    gridOptions=grid_options, 
                                    update_mode=GridUpdateMode.SELECTION_CHANGED, 
                                    enable_enterprise_modules=True, 
                                    theme=AgGridTheme.STREAMLIT)
        
        collectionRow = collectionResponse.get("selected_rows", None)
        if collectionRow is not None and len(collectionRow)>0:
            collectionRows = collectionRow.iloc[0] 
            collectionRows_dict = collectionRows.to_dict() if isinstance(collectionRows, pd.Series) else collectionRows
            st.session_state.collectionSelection = collectionRows_dict
            collectedInfo()

def collectionHistory():
    if st.session_state.collectionDatas:
        st.subheader("Your Branch Loan Collection Status")

        datas = st.session_state.collectionDatas
        
        df = pd.DataFrame(datas)
        
        # st.write(df)
        df_merged = pd.merge(df, dis_branch, on='branch_code', how='inner')

        columns_to_display = ["cust_id","District", "Branch", "customer_name","phone_number","saving_account","approved_amount", "oustanding_total","paid_amount",
                            "application_status","loan_status","collectionStatus", "remark","approved_date","expiry_date"]
        selectedDataFrame = df_merged[columns_to_display]



        st.dataframe(selectedDataFrame, use_container_width=True)

def update_collectionStatus():
    st.session_state.collectionSelection["collectionStatus"]=st.session_state.collectionStatus

def update_remark():
    st.session_state.collectionSelection["remark"]=st.session_state.remark

def update_loanStatus():
    st.session_state.collectionSelection["loan_status"]=st.session_state.loan_status

def update_outstanding():
    st.session_state.collectionSelection["oustanding_total"]=st.session_state.oustanding_total

# Collection Data Dialog
@st.dialog("You are Doing confermition to the collection ")
def collectedInfo():
    loanStatOption = ["Closed", "In Arrears"]
    collectionStatus = ["Confirmed", "Cancelled", "Pending"]
    st.subheader(f"__You are updating data of__ :blue[ {st.session_state.collectionSelection['customer_name']}]")
    st.markdown(f" *Saving Account =* ***{st.session_state.collectionSelection['saving_account']}***")
    st.markdown(f" *Phone number =* ***{st.session_state.collectionSelection['phone_number']}***")
    st.markdown(f" *Approved amount =* **{st.session_state.collectionSelection['approved_amount']}**")
    st.markdown(f" *Paid amount =* **{st.session_state.collectionSelection['paid_amount']}**")
    st.markdown(f" *outsanding_total=* **{st.session_state.collectionSelection['oustanding_total']}**")

    prevLoanStatus = loanStatOption.index(st.session_state.collectionSelection["loan_status"])
    prevCollStatus = collectionStatus.index(st.session_state.collectionSelection["collectionStatus"])
    st.number_input("Outstanding_total", value=float(st.session_state.collectionSelection["oustanding_total"]),on_change=update_outstanding, key="oustanding_total" )
    st.selectbox("Loan status", options=loanStatOption, on_change=update_loanStatus ,index= prevLoanStatus ,key="loan_status")

    st.selectbox("CollectionStatus", options=collectionStatus, on_change=update_collectionStatus, index=prevCollStatus, key="collectionStatus")
    st.text_input("Remark", value= st.session_state.collectionSelection['remark'], key="remark", on_change= update_remark )

    if st.button("Submit"):
        updatingData={"collectionID":st.session_state.collectionSelection["collectionID"],
                    "oustanding_total":st.session_state.collectionSelection["oustanding_total"],
                    "collectionStatus":st.session_state.collectionSelection["collectionStatus"],
                    "remark":st.session_state.collectionSelection["remark"],
                    "loan_status":st.session_state.collectionSelection["loan_status"],
                    "cust_id":st.session_state.collectionSelection["cust_id"]
                    }
        confirmationRequest(updatingData)


# listOfbranchCode=list_branchcode #List of branch code to be accessed
def collectionData(branch_code, role):
    # branch=True
    if role == 'Branch User':
        user = True
        # st.write(f"under if of collection data, {role}")
    else:
        user = False
    initialize_session()
    
    fetchCollectionData(branch_code)
    if user:
        collectionHistory()
        # st.write("The user is branch collectionHistory() not clickable")
    else:
        
        collectionManagement()
        # collectionHistory()
        # st.write("The user is not branch collectionManagement() is clickable")

    



