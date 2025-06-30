import streamlit as st
from navigation import make_sidebar
from dependence import allget_recommendations

import os
import streamlit as st
import pandas as pd
from pathlib import Path
from navigation import make_sidebar1
import traceback
import uuid
from typing import Tuple
import time
from PIL import Image
import base64
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()
           
# Main function to handle user sign-up
def register():
    # Custom CSS to change button hover color to cyan blue
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide")
    custom_cs = """
    <style>
        div.block-container {
            # padding-top: 2.5rem; /* Adjust this value to reduce padding-top */
        }
        #MainMenu { visibility: hidden; }
        .stDeployButton { visibility: hidden; }
        .stAppHeader { visibility: hidden; }
        /* Hide the entire header bar */
        header.stAppHeader {
            display: none;
        }
        .stButton button {
            background-color: #000000;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 16px;
            cursor: pointer;
        }
        .css-1vbd788.e1tzin5v1 {
            display: none;
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    
    
    custom_css = """
    <style>
        div.block-container {
            padding-top: 1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    update_activity()
    

    col1, col2, col3 = st.columns([0.1,0.7,0.1])
   
    with col1:
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash{
        font-weight:bold;
        padding:1px;
        border-radius:6px
        }
        </style>
        <center> <h3 class = "title_dash"> Michu Recomandation Letter Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    
    
    
    # st.balloons()

    hide_streamlit_style = """
    <style>
    #MainMenu{visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # back_image = Image.open('pages/kiyya.jpg')
    st.logo('pages/michu.png')
    # st.sidebar.image('pages/michu.png')
    # username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)

    make_sidebar()
   
    st.markdown(custom_cs, unsafe_allow_html=True)
    st.subheader("Loan Recommendations (today's date)")
            
    
    
    try:
        recommendations = allget_recommendations()
        
        if not recommendations:
            st.info("No pending recommendations found.")
        else:
            # Convert to DataFrame
            df = pd.DataFrame(recommendations)
            
            # Rename columns
            df = df.rename(columns={
                'district': 'District',
                'full_Name': 'Branch',
                'customer_phone': 'Phone',
                'customer_account': 'Account',
                'reason': 'Reason',
                'register_date': 'Submission Date',
                'status': 'Status',
                'document_path': 'Document Path',
                'filename': 'Filename',
                'file_type': 'Document Type',
            })

            # # Display the DataFrame
            # st.dataframe(
            #     df[['District', 'Branch', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
            #     use_container_width=True,
            #     hide_index=True
            # )

            # Create a column for view buttons
            df['View'] = False

            # Display the table with interactive buttons
            edited_df = st.data_editor(
                df[['District', 'Branch', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'View']],
            use_container_width=True,
                hide_index=True,
                column_config={
                    "View": st.column_config.CheckboxColumn(
                        "View Document",
                        help="Check to view the document",
                        default=False,
                        width="small"
                    )
                }
            )

            # Check if any view checkbox was selected
            if edited_df['View'].any():
                selected_index = edited_df[edited_df['View']].index[0]
                selected_row = df.iloc[selected_index]
                file_path = selected_row['Document Path']
                file_type = selected_row['Document Type']
                filename = selected_row['Filename']
                
                st.subheader(f"Document Preview: {filename}")
                
                if not os.path.exists(file_path):
                    st.warning(f"File not found: {filename}")
                else:
                    if file_type == 'application/pdf':
                        with open(file_path, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                            st.markdown(pdf_display, unsafe_allow_html=True)
                            
                    elif file_type in ['image/png', 'image/jpeg']:
                        image = Image.open(file_path)
                        st.image(image, caption=filename, use_container_width=True)
                        
                    else:
                        st.warning("Unsupported file type for preview")




            # Phone number search
            st.subheader("Search by Phone Number")
            search_phone = st.text_input("Enter customer phone number (e.g., 0912345678)")
            
            if search_phone:
                # Filter by phone number
                result = df[df['Phone'] == search_phone]
                
                if len(result) == 0:
                    st.warning("No documents found for this phone number")
                else:
                    # Display basic info
                    st.write(f"Found {len(result)} document(s) for phone: {search_phone}")
                    st.dataframe(
                        result[['District', 'Branch', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Display each document found
                    for _, row in result.iterrows():
                        file_path = row['Document Path']
                        
                        if not os.path.exists(file_path):
                            st.warning(f"File not found: {row['Filename']}")
                            continue
                            
                        st.subheader(f"Document: {row['Filename']}")
                        
                        if row['Document Type'] == 'application/pdf':
                            with open(file_path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        
                        elif row['Document Type'] in ['image/png', 'image/jpeg']:
                            image = Image.open(file_path)
                            st.image(image, caption=row['Filename'], width=400)
                        
                        else:
                            st.warning("Unsupported file type for preview")
            
            # Show all recommendations if no search
            else:
                st.info("Enter a phone number above to view specific documents")
            
    except Exception as e:
        st.error(f"Failed to load recommendations: {str(e)}")
        traceback.print_exc()
        

    # Footer implementation
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #000;
        color: #00adef;
        text-align: center;
        padding: 0.5rem 0;
    }
    </style>
    <div class='footer'>
    <p>Copyright Â© 2025 Michu Platform</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)
    
if __name__ == '__main__':
    # make_sidebar()
    register()