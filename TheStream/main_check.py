
import streamlit as st

from CollectedData import collectionData

from AddingCollection import InArrearsData, arrears_acess

st.set_page_config(layout="wide")

def initialize_session():
    if "selectedRow" in st.session_state:
        st.session_state.selectedRow=None
    if "collectionDatas" in st.session_state:
        st.session_state.collectionDatas=[]

    if "collectionSelection" in st.session_state:
        st.session_state.collectionSelection=None

def main():

    initialize_session()

    def reset_selected_row():
        st.session_state.selectedRow = None
        st.session_state.collectionSelection = None
    
    
    tab1, tab2 = st.tabs(["In Arrears Loan", "Collection Status"])

    with tab1:
        arrears_acess()
    with tab2:
        collectionData()




# if __name__=="__main__":
#     main()