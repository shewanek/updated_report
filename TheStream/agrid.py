from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, AgGridTheme
import streamlit as st
import pandas as pd

def collectionData():
    # initialize_session()
    # fetchCollectionData()
    
    if st.session_state.collectionDatas:
        st.subheader("Your Branch Loan Collection Status")
        datas = st.session_state.collectionDatas
        df = pd.DataFrame(datas)
        columns_to_display = ["oustanding_total", "approved_amount", "approved_date",
                              "phone_number", "michu_loan_product", "expiry_date", "created_date", "customer_name",
                              "saving_account", "application_status", "paid_amount", "branch_code", "loan_status", 
                              "collectionStatus", "remark"]
        selectedDataFrame = df[columns_to_display]
        
        # Initialize GridOptionsBuilder
        gb = GridOptionsBuilder.from_dataframe(selectedDataFrame)
        
        # Configure pagination
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        
        # Configure default column settings
        gb.configure_default_column(editable=True)
        
        # Set row height
        gb.configure_grid_options(rowHeight=40)
        
        # Apply custom styles to cells
        cell_styles = {"font-size": "16px", "padding": "10px"}
        gb.configure_default_column(cellStyle=cell_styles)
        
        # Enable single row selection
        gb.configure_selection("single")
        
        # Enable sorting, filtering, and column resizing
        gb.configure_grid_options(enableSorting=True, enableFilter=True, enableColResize=True)
        
        # Enable filtering options
        for col in columns_to_display:
            gb.configure_column(col, filter="agTextColumnFilter", filter_params={"filterOptions": ["contains"]})
        
        # Build grid options
        grid_options = gb.build()
        
        # Render the grid
        collectionResponse = AgGrid(df, 
                                    gridOptions=grid_options, 
                                    update_mode=GridUpdateMode.SELECTION_CHANGED, 
                                    enable_enterprise_modules=True, 
                                    theme=AgGridTheme.STREAMLIT)
        
        # Handle row selection
        collectionRow = collectionResponse.get("selected_rows", None)
        if collectionRow is not None and len(collectionRow) > 0:
            collectionRows = pd.DataFrame(collectionRow).iloc[0]
            collectionRows_dict = collectionRows.to_dict() if isinstance(collectionRows, pd.Series) else collectionRows
            st.session_state.collectionSelection = collectionRows_dict
            # collectedInfo()

