import os
import streamlit as st
import pandas as pd
# from pathlib import Path
from navigation import make_sidebar1, make_sidebar 
from streamlit_extras.metric_cards import style_metric_cards
import traceback
import uuid
from typing import Tuple
import time
from PIL import Image
import base64
from datetime import datetime
# from datetime import datetime, timedelta
from dependence import get_recommendations, apr_get_recommendations, rej_get_recommendations, delete_rejected, check_rejected, validate_full_name, block_get_recommendations, total_recommendations, total_recommendations_branch
from dependence import update_activity, check_session_timeout, get_by_user_id, get_overdue_pending, delete_rejectedabove8




def delete_recommendationabove8() -> bool:
    """
    Process all overdue recommendations (keeps your original logic).
    Returns True if all deletions succeeded, False otherwise.
    """
    try:
        overdue_records = get_overdue_pending()
        if not overdue_records:
            st.info("No overdue recommendations found")
            return True
            
        all_success = True
        for rec_id, file_path in overdue_records:
            # Delete associated file if exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    st.error(f"Failed to delete file {file_path}: {str(e)}")
                    all_success = False
            
            # Delete database records
            if not delete_rejectedabove8(rec_id):
                all_success = False
                
        return all_success
        
    except Exception as e:
        st.error(f"Unexpected error during cleanup: {str(e)}")
        return False

def run_daily_cleanup():
    """Execute cleanup once per day"""
    if 'last_cleanup_date' not in st.session_state:
        st.session_state.last_cleanup_date = None
    
    today = datetime.now().date()
    
    if st.session_state.last_cleanup_date != today:
        with st.spinner("Running daily cleanup..."):
            success = delete_recommendationabove8()
            if success:
                st.session_state.last_cleanup_date = today
                # st.success("Daily cleanup completed")
            else:
                pass
                    # st.warning("Cleanup completed with some errors")
    else:
        pass
        # st.info("Cleanup already ran today")
    




def delete_recommendation(rec_id: str, file_path: str, phone: str) -> bool:
    """
    Delete a recommendation record and its associated file.
    
    Args:
        rec_id: The recommendation record ID
        file_path: Path to the recommendation document
        phone: The customer's phone number (starting with '0')

    Returns:
        bool: True if both file and database records were deleted, False otherwise
    """
    try:
        # First delete the database records (child first, then parent)
        if not delete_rejected(rec_id, phone):
            return False

        # Then delete the file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                st.error(f"Failed to delete file: {str(e)}")
                # Still return True since DB records were deleted
                return True
        
        return True

    except Exception as e:
        st.error(f"Unexpected error during deletion: {str(e)}")
        return False
# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()

# Streamlit app
def main():
    # Add this at the beginning of your main function
    # check_session_timeout()
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0rem; /* Adjust this value to reduce padding-top */
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
            cursor: pointer.
        }
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    update_activity()




    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image('pages/coopbanck.gif')
    html_title = """
        <style>
        .title_dash {
            font-weight: bold;
            padding: 1px;
            border-radius: 6px;
        }
        </style>
        <center> <h3 class="title_dash"> Michu Recommendation Letter Upload/View Portal </h3> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    st.logo("pages/michu.png")
    full_name = st.session_state.get("full_name", "")
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    # update_user_activity(username)
    # st.write(role)
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    if role == "recomandation" or role == "CRM":
        make_sidebar()
    else:
        make_sidebar1()
    if role == "Branch User":
        tab_options = ["Upload Recommendation", "Submitted Recommendations"]
        # Add a div with a custom class around st.radio
        # st.markdown('<div class="custom-radio">', unsafe_allow_html=True)
        active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
        if active_tab == "Upload Recommendation":
            colll1, colll2, colll3 = st.columns([1,3,1])
            with colll2:
                def save_uploaded_file(uploaded_file, upload_dir: str = "recommendations") -> Tuple[str, str]:
                    """
                    Save uploaded file to specified directory with UUID filename
                    Returns tuple of (file_path, stored_filename)
                    """
                    try:
                        # Create directory if not exists
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Validate file type
                        allowed_types = ['application/pdf', 'image/png', 'image/jpeg']
                        if uploaded_file.type not in allowed_types:
                            raise ValueError("Invalid file type. Only PDF and images are allowed.")
                        
                        # Generate safe filename
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        unique_id = uuid.uuid4().hex  # Remove hyphens
                        filename = f"{unique_id}{file_ext}"
                        file_path = os.path.join(upload_dir, filename)
                        
                        # Save file
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        return file_path, filename
                        
                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")
                        return None, None

                # def branch_recommendation_form():
                # """Streamlit form for branch recommendations"""
                st.write("Submit Recommendation Letter")
                
                with st.form("recommendation_form", clear_on_submit=True):
                    MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB in bytes
                    # Form inputs
                    col1, col2 = st.columns(2)
                    # Reason options with better descriptions
                    reason_options = [ "Choose Reason",
                        "Business licenses are not registered online",
                        "Online registration has recently begun)",
                        "A recommendation letter is required for our branch customers",
                        "A recommendation is needed for blocked customers",
                        "Recommendations are required for other cases"
                    ]
                    
                    with col1:
                        name = st.text_input('Customer Name', placeholder='Enter  Full Name', help="Enter full name (First name and father name)")
                        customer_account = st.text_input(
                            "Customer Account*",
                            max_chars=13,
                            help="Must be 12 or 13 digits"
                        )
                        
                        
                    with col2:
                        customer_phone = st.text_input(
                            "Customer Phone* (09XXXXXXXX)", 
                            max_chars=10,
                            help="Must start with 09 and be 10 digits"
                        )
                        reason = st.selectbox(
                        'Reason for Recommendation*',
                        options=reason_options,
                        help="Select the primary reason for this recommendation"
                    )
                    
                    document = st.file_uploader(
                        "Upload Recommendation Letter* (PDF/PNG/JPEG)", 
                        type=['pdf', 'png', 'jpg', 'jpeg'],
                        accept_multiple_files=False
                    )
                    
                    submitted = st.form_submit_button("Submit Recommendation")
                    try:
                        if submitted:
                            # Validate inputs
                            if not all([customer_account.strip(), customer_phone.strip(),  document]):
                                st.error("Please fill all required fields (*)")
                                return
                            if document.size > MAX_FILE_SIZE:
                                # st.write(document.size)
                                st.error("File size should not exceed 1 MB. Please upload a smaller file.")
                                return
                            if reason == "Choose Reason":
                                st.error("Please select a reason for recommendation")
                                return
                            if not validate_full_name(name):
                                 st.error('Please enter valid name (First name and father name)') 
                                 return 
                            if not customer_phone.startswith('09') or len(customer_phone) != 10:
                                st.error("Invalid phone number format. Must start with 09 and be 10 digits.")
                                return
                            if not customer_account.isdigit() or len(customer_account) not in [12, 13]:
                                st.error("Invalid account number format. Must be 12 or 13 digits.")
                                return
                            result = check_rejected(customer_phone)
                            # st.write(result)
                            if result:
                                rec_id, file_pathh = result
                                delete_recommendation(rec_id, file_pathh, customer_phone)
                                

                            from dependence import check_rec_exist
                            if check_rec_exist(customer_phone, customer_account):
                                st.error("Recommendation already exists for this customer.")
                                return
                            from dependence import check_rec_acc_exist
                            if check_rec_acc_exist(customer_account):
                                st.error("No Need Recommendation for this customer")
                                return
                            from dependence import check_rec_register
                            if not check_rec_register(customer_phone, customer_account):
                                st.error("Action denied. You must be registered before submitting a recommendation letter.")
                                return

                                
                            # Save file and get metadata
                            file_path, filename = save_uploaded_file(document)
                            
                            if file_path and filename:
                                from dependence import recommendation
                                
                                if recommendation(username, name, customer_phone, customer_account, reason, file_path, filename, document.type):
                                    # TODO: Add database insert operation
                                    # st.success("Recommendation submitted successfully!")
                                    success_placeholder = st.empty()
                                    success_placeholder.success("Recommendation submitted successfully!")
                                    st.balloons()
                                    time.sleep(1.5)
                                    success_placeholder.empty()  # Removes the message after 10 seconds
                                    
                                else:
                                    st.error("Failed to submit recommendation. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred while processing the form: {e}")
                        traceback.print_exc()

                    
        if active_tab == "Submitted Recommendations":
            total_recommendation = total_recommendations_branch(username)
            total_df = pd.DataFrame(total_recommendation)
            col1, col2, col3, col4 = st.columns(4)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col1.metric(label="**Total Pending**", value=total_df['pending_count'], delta="Pending")
            col2.metric(label="**Total Approved**", value=total_df['approved_count'], delta="Approved")
            col3.metric(label="**Total Rejected**", value=total_df['rejected_count'], delta="Rejected")
            col4.metric(label="**Total Blocked**", value=total_df['blocked_count'], delta="Blocked")
            # col4.metric(label="***Total Blocked***", value=0, delta="unrecognized questions")
            # style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
            # st.subheader("Pending Loan Recommendations")
            st.markdown(
                "##### Today's Loan Recommendation Letters",
                unsafe_allow_html=True
            )
            # st.subheader("Today's Loan Recommendation Letters")
            option = ["Pending", "Approved", "Rejected", "Blocked"]
            act_tab = st.radio("Select a Tab", option, horizontal=True)
            if act_tab == "Pending":
            
                try:
                    recommendations = get_recommendations(username)
                    
                    if not recommendations:
                        st.info("No Pending recommendation letters found for today.")
                    else:
                        # Convert to DataFrame
                        df = pd.DataFrame(recommendations)
                        
                        # Rename columns
                        df = df.rename(columns={
                            'district': 'District',
                            'full_Name': 'Branch',
                            'full_name': 'Full Name',
                            'customer_phone': 'Phone',
                            'customer_account': 'Account',
                            'reason': 'Reason',
                            'register_date': 'Submission Date',
                            'status': 'Status',
                            'document_path': 'Document Path',
                            'filename': 'Filename',
                            'file_type': 'Document Type',
                        })

                        # Create a column for view buttons
                        df['View'] = False

                        # Display the table with interactive buttons
                        edited_df = st.data_editor(
                            df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'View']],
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
                            phone = selected_row['Phone']
                            
                            st.subheader(f"Document Preview: {phone}")

                            try:
                                if not os.path.exists(file_path):
                                    st.warning(f"File not found: {filename}")
                                else:
                                    if file_type == 'application/pdf':
                                        # Use context manager for file handling
                                        try:
                                            with open(file_path, "rb") as f:
                                                file_content = f.read()  # Read all content first
                                            base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                            st.markdown(pdf_display, unsafe_allow_html=True)
                                        except Exception as e:
                                            st.error(f"Failed to load PDF: {str(e)}")
                                            
                                    elif file_type in ['image/png', 'image/jpeg']:
                                        # Use context manager for PIL Image
                                        try:
                                            with Image.open(file_path) as img:
                                                st.image(img.copy(), caption=filename, use_container_width=True)  # .copy() ensures the image is loaded into memory
                                        except Exception as e:
                                            st.error(f"Failed to load image: {str(e)}")
                                            
                                    else:
                                        st.warning("Unsupported file type for preview")

                            except OSError as oe:
                                if "WinError 10055" in str(oe):
                                    st.error("System resource error: Please try again later or close other applications")
                                else:
                                    st.error(f"File access error: {str(oe)}")
                            except Exception as e:
                                st.error(f"Unexpected error: {str(e)}")
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
            if act_tab == "Approved":
                try:
                    recommendations = apr_get_recommendations(username)
                    
                    if not recommendations:
                        st.info("No Approved recommendation letters found for today.")
                    else:
                        # Convert to DataFrame
                        df = pd.DataFrame(recommendations)
                        
                        # Rename columns
                        df = df.rename(columns={
                            'district': 'District',
                            'full_Name': 'Branch',
                            'full_name': 'Full Name',
                            'customer_phone': 'Phone',
                            'customer_account': 'Account',
                            'reason': 'Reason',
                            'register_date': 'Submission Date',
                            'status': 'Status',
                            'document_path': 'Document Path',
                            'filename': 'Filename',
                            'file_type': 'Document Type'
                            
                        })

                        # # Create a column for view buttons
                        # df['View'] = False

                        # Display the table with interactive buttons
                        edited_df = st.data_editor(
                            df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                            use_container_width=True,
                            hide_index=True,
                            # column_config={
                            #     "View": st.column_config.CheckboxColumn(
                            #         "View Document",
                            #         help="Check to view the document",
                            #         default=False,
                            #         width="small"
                            #     )
                            # }
                        )

                        # # Check if any view checkbox was selected
                        # if edited_df['View'].any():
                        #     selected_index = edited_df[edited_df['View']].index[0]
                        #     selected_row = df.iloc[selected_index]
                        #     file_path = selected_row['Document Path']
                        #     file_type = selected_row['Document Type']
                        #     filename = selected_row['Filename']
                            
                        #     st.subheader(f"Document Preview: {filename}")
                            
                        #     if not os.path.exists(file_path):
                        #         st.warning(f"File not found: {filename}")
                        #     else:
                        #         if file_type == 'application/pdf':
                        #             with open(file_path, "rb") as f:
                        #                 base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                        #                 pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                        #                 st.markdown(pdf_display, unsafe_allow_html=True)
                                        
                        #         elif file_type in ['image/png', 'image/jpeg']:
                        #             image = Image.open(file_path)
                        #             st.image(image, caption=filename, use_column_width=True)
                                    
                        #         else:
                        #             st.warning("Unsupported file type for preview")
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
            if act_tab == "Rejected":
                try:
                    recommendations = rej_get_recommendations(username)
                    
                    if not recommendations:
                        st.info("No Rejected recommendation letters found for today.")
                    else:
                        # Convert to DataFrame
                        df = pd.DataFrame(recommendations)
                        
                        # Rename columns
                        df = df.rename(columns={
                            'district': 'District',
                            'full_Name': 'Branch',
                            'full_name': 'Full Name',
                            'customer_phone': 'Phone',
                            'customer_account': 'Account',
                            'reason': 'Reason',
                            'register_date': 'Submission Date',
                            'status': 'Status',
                            'document_path': 'Document Path',
                            'filename': 'Filename',
                            'file_type': 'Document Type',
                            'notes': 'Rejection Reason'
                        })

                        # Create a column for view buttons
                        df['View'] = False

                        # Display the table with interactive buttons
                        edited_df = st.data_editor(
                            df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'Rejection Reason', 'View']],
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
                            phone = selected_row['Phone']
                            
                            st.subheader(f"Document Preview: {phone}")

                            try:
                                if not os.path.exists(file_path):
                                    st.warning(f"File not found: {filename}")
                                else:
                                    if file_type == 'application/pdf':
                                        # Use context manager for file handling
                                        try:
                                            with open(file_path, "rb") as f:
                                                file_content = f.read()  # Read all content first
                                            base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                            st.markdown(pdf_display, unsafe_allow_html=True)
                                        except Exception as e:
                                            st.error(f"Failed to load PDF: {str(e)}")
                                            
                                    elif file_type in ['image/png', 'image/jpeg']:
                                        # Use context manager for PIL Image
                                        try:
                                            with Image.open(file_path) as img:
                                                st.image(img.copy(), caption=filename, use_container_width=True)  # .copy() ensures the image is loaded into memory
                                        except Exception as e:
                                            st.error(f"Failed to load image: {str(e)}")
                                            
                                    else:
                                        st.warning("Unsupported file type for preview")

                            except OSError as oe:
                                if "WinError 10055" in str(oe):
                                    st.error("System resource error: Please try again later or close other applications")
                                else:
                                    st.error(f"File access error: {str(oe)}")
                            except Exception as e:
                                st.error(f"Unexpected error: {str(e)}")
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
            if act_tab == "Blocked":
                try:
                    recommendations = block_get_recommendations(username)
                    
                    if not recommendations:
                        st.info("No Blocked recommendation letters found for today.")
                    else:
                        # Convert to DataFrame
                        df = pd.DataFrame(recommendations)
                        
                        # Rename columns
                        df = df.rename(columns={
                            'district': 'District',
                            'full_Name': 'Branch',
                            'full_name': 'Full Name',
                            'customer_phone': 'Phone',
                            'customer_account': 'Account',
                            'reason': 'Reason',
                            'register_date': 'Submission Date',
                            'status': 'Status',
                            'document_path': 'Document Path',
                            'filename': 'Filename',
                            'file_type': 'Document Type',
                            'notes': 'Rejection Reason'
                        })

                        # Create a column for view buttons
                        df['View'] = False

                        # Display the table with interactive buttons
                        edited_df = st.data_editor(
                            df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'Rejection Reason', 'View']],
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
                            phone = selected_row['Phone']
                            
                            st.subheader(f"Document Preview: {phone}")

                            try:
                                if not os.path.exists(file_path):
                                    st.warning(f"File not found: {filename}")
                                else:
                                    if file_type == 'application/pdf':
                                        # Use context manager for file handling
                                        try:
                                            with open(file_path, "rb") as f:
                                                file_content = f.read()  # Read all content first
                                            base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                            st.markdown(pdf_display, unsafe_allow_html=True)
                                        except Exception as e:
                                            st.error(f"Failed to load PDF: {str(e)}")
                                            
                                    elif file_type in ['image/png', 'image/jpeg']:
                                        # Use context manager for PIL Image
                                        try:
                                            with Image.open(file_path) as img:
                                                st.image(img.copy(), caption=filename, use_container_width=True)  # .copy() ensures the image is loaded into memory
                                        except Exception as e:
                                            st.error(f"Failed to load image: {str(e)}")
                                            
                                    else:
                                        st.warning("Unsupported file type for preview")

                            except OSError as oe:
                                if "WinError 10055" in str(oe):
                                    st.error("System resource error: Please try again later or close other applications")
                                else:
                                    st.error(f"File access error: {str(oe)}")
                            except Exception as e:
                                st.error(f"Unexpected error: {str(e)}")
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
                except Exception as e:
                    st.error(f"Failed to load recommendations: {str(e)}")
                    traceback.print_exc()
                    
            try:

                # Phone number search
                st.subheader("Search by Phone Number")
                search_phone = st.text_input("Enter customer phone number (e.g., 0912345678)")
                # if st.button("Search"):
                if search_phone.strip():
                    search_phone = search_phone.strip()
                    # Validate phone number format
                    if not (
                        (search_phone.startswith('09') and len(search_phone) == 10) or
                        (search_phone.startswith('+2519') and len(search_phone) == 13)
                    ) or not search_phone.replace('+', '').isdigit():
                        st.error("Invalid phone number format. Must start with '09' (10 digits) or '+2519' (13 characters).")
                        return
                    # Filter by phone number
                    from dependence import search_get_recommendations
                    # result = df[df['Phone'] == search_phone]
                    search, status = search_get_recommendations(username, search_phone)

                    # Convert to DataFrame
                    br_result = pd.DataFrame(search) if search else pd.DataFrame()
                    
                    if br_result.empty:
                        st.warning("No documents found for this phone number")
                    else:
                        if status == "Rejected":
                            # Rename columns
                            br_result = br_result.rename(columns={
                                'district': 'District',
                                'full_Name': 'Branch',
                                'full_name': 'Full Name',
                                'customer_phone': 'Phone',
                                'customer_account': 'Account',
                                'reason': 'Reason',
                                'register_date': 'Submission Date',
                                'status': 'Status',
                                'document_path': 'Document Path',
                                'filename': 'Filename',
                                'file_type': 'Document Type',
                                'notes': 'Rejection Reason'
                            })
                            
                            if len(br_result) == 0:
                                st.warning("No documents found for this phone number")
                            else:
                                # Display basic info
                                st.write(f"Found {len(br_result)} document(s) for phone: {search_phone}")
                                st.dataframe(
                                    br_result[['Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'Rejection Reason']],
                                    use_container_width=True,
                                    hide_index=True
                                )
                                
                                # Display each document found
                                for _, row in br_result.iterrows():
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
                        else:
                            br_result = br_result.rename(columns={
                                'district': 'District',
                                'full_Name': 'Branch',
                                'full_name': 'Full Name',
                                'customer_phone': 'Phone',
                                'customer_account': 'Account',
                                'reason': 'Reason',
                                'register_date': 'Submission Date',
                                'status': 'Status',
                                'document_path': 'Document Path',
                                'filename': 'Filename',
                                'file_type': 'Document Type',
                            })
                            
                            if len(br_result) == 0:
                                st.warning("No documents found for this phone number")
                            else:
                                # Display basic info
                                st.write(f"Found {len(br_result)} document(s) for phone: {search_phone}")
                                st.dataframe(
                                    br_result[['Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                                    use_container_width=True,
                                    hide_index=True
                                )
                                
                                # Display each document found
                                for _, row in br_result.iterrows():
                                    file_path = row['Document Path']
                                    
                                    # Verify file exists first
                                    if not os.path.exists(file_path):
                                        st.warning(f"File not found: {row['Filename']}")
                                    else:
                                        # Handle PDF files
                                        if row['Document Type'] == 'application/pdf':
                                            try:
                                                # Read and encode PDF content
                                                with open(file_path, "rb") as f:
                                                    pdf_content = f.read()
                                                base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                                                
                                                # Display PDF with responsive sizing
                                                pdf_display = f'''
                                                <div style="width:100%; height:75vh;">
                                                    <iframe src="data:application/pdf;base64,{base64_pdf}" 
                                                            width="100%" 
                                                            height="100%" 
                                                            style="border:none;">
                                                    </iframe>
                                                </div>
                                                '''
                                                st.markdown(pdf_display, unsafe_allow_html=True)
                                                
                                            except Exception as e:
                                                st.error(f"Failed to load PDF: {str(e)}")
                                        
                                        # Handle image files
                                        elif row['Document Type'] in ['image/png', 'image/jpeg']:
                                            try:
                                                # Open image with context manager
                                                with Image.open(file_path) as img:
                                                    # Create copy to ensure proper resource cleanup
                                                    img_copy = img.copy()
                                                    st.image(img_copy, 
                                                        caption=row['Filename'], 
                                                        use_container_width=True,
                                                        output_format='auto')
                                            except Exception as e:
                                                st.error(f"Failed to load image: {str(e)}")
                                        
                                        # Unsupported file types
                                        else:
                                            st.warning(f"Unsupported file type: {row['Document Type']}")
                                            st.download_button(
                                                label="Download File",
                                                data=open(file_path, "rb").read(),
                                                file_name=row['Filename'],
                                                mime=row['Document Type']
                                            )

                           
                
                # Show all recommendations if no search
                else:
                    st.info("Enter a phone number above to view specific documents")
                
            except Exception as e:
                st.error(f"Failed to load recommendations: {str(e)}")
                traceback.print_exc()
                
    elif role == "Admin" or role == "recomandation":
        total_recommendation = total_recommendations()
        total_df = pd.DataFrame(total_recommendation)
        col1, col2, col3, col4 = st.columns(4)
         # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Pending**", value=total_df['pending_count'], delta="Pending")
        col2.metric(label="**Total Approved**", value=total_df['approved_count'], delta="Approved")
        col3.metric(label="**Total Rejected**", value=total_df['rejected_count'], delta="Rejected")
        col4.metric(label="**Total Blocked**", value=total_df['blocked_count'], delta="Blocked")
        # col4.metric(label="***Total Blocked***", value=0, delta="unrecognized questions")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
        # st.subheader("Pending Loan Recommendations")
        st.markdown(
            "##### Pending Loan Recommendations &nbsp; <span style='color: #00adef; font-weight: 600;'>(For Today)</span>",
            unsafe_allow_html=True
        )
            
        from dependence import allget_recommendations
        
        try:
            recommendations = allget_recommendations()
            
            if not recommendations:
                st.info("No Pending recommendations found today.")
            else:
                # Convert to DataFrame
                df = pd.DataFrame(recommendations)
                
                # Rename columns
                df = df.rename(columns={
                    'district': 'District',
                    'full_Name': 'Branch',
                    'full_name': 'Full Name',
                    'customer_phone': 'Phone',
                    'customer_account': 'Account',
                    'reason': 'Reason',
                    'register_date': 'Submission Date',
                    'status': 'Status',
                    'document_path': 'Document Path',
                    'filename': 'Filename',
                    'file_type': 'Document Type',
                })

                # Create a column for view buttons
                df['View'] = False

                # Display the table with interactive buttons
                edited_df = st.data_editor(
                    df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'View', 'Status', 'Submission Date']],
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
                    phone = selected_row['Phone']
                    
                    # Document preview and approval section
                    st.subheader(f"Document Preview: {phone}")

                    try:
                        col11, col21 = st.columns([3, 1])  # 3:1 ratio for preview:controls
                        with col11:
                            # Check file existence
                            if not os.path.exists(file_path):
                                st.warning(f"File not found: {filename}")
                            else:
                                # Handle PDF files
                                if file_type == 'application/pdf':
                                    try:
                                        with open(file_path, "rb") as f:
                                            file_content = f.read()  # Read all content at once
                                        base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                        st.markdown(pdf_display, unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Failed to load PDF: {str(e)}")
                                        traceback.print_exc()
                                
                                # Handle image files
                                elif file_type in ['image/png', 'image/jpeg']:
                                    try:
                                        with Image.open(file_path) as img:
                                            # Create a copy to ensure the image is loaded into memory
                                            img_copy = img.copy()
                                        st.image(img_copy, caption=filename, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Failed to load image: {str(e)}")
                                        traceback.print_exc()
                                
                                else:
                                    st.warning("Unsupported file type for preview")
                        with col21:

                            # Approval controls section
                            with st.form(key=f"approval_form_{phone}", clear_on_submit=True):
                                # Get current status (with case normalization)
                                current_status = selected_row['Status'].capitalize()
                                
                                # Status options with current selection
                                status_options = ["Approved", "Rejected", "Blocked", "Pending"]
                                new_status = st.selectbox(
                                    "Action",
                                    options=status_options,
                                    index=status_options.index(current_status),
                                    key=f"status_{phone}"
                                )
                                
                                # Notes field
                                notes = st.text_area(
                                    "Review Notes",
                                    value="",
                                    key=f"notes_{phone}",
                                    help="Enter review comments (optional)"
                                )
                                
                                # Form submission
                                submitted = st.form_submit_button("Update Status")
                                if submitted:
                                    notes_stripped = notes.strip()
                                    
                                    # Check if status changed
                                    if new_status == current_status:
                                        st.info("No changes detected. Update skipped.")
                                    
                                    # Validate notes for non-approved actions
                                    elif new_status != "Approved" and not notes_stripped:
                                        st.warning("Please provide review notes for non-Approved actions.")
                                    elif role == "recomandation":
                                        st.warning("You do not have permission to update the status of this recommendation.")
                                    
                                    else:
                                        try:
                                            from dependence import update_recommendation_status
                                            # Update status in database
                                            if update_recommendation_status(phone, new_status, notes_stripped, username):
                                                # Success feedback
                                                success_placeholder = st.empty()
                                                success_placeholder.success("Status updated successfully!")
                                                st.balloons()
                                                
                                                # Clear success message after delay
                                                time.sleep(4)
                                                success_placeholder.empty()
                                                
                                                # Force refresh of the page to show updated status
                                                st.rerun()
                                            else:
                                                st.error("Failed to update status. Please try again.")
                                        
                                        except Exception as e:
                                            st.error(f"Error during status update: {str(e)}")
                                            traceback.print_exc()

                    except OSError as oe:
                        if "WinError 10055" in str(oe):
                            st.error("System resource error: Please try again later or close other applications")
                        else:
                            st.error(f"File access error: {str(oe)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                        traceback.print_exc()

                            

        except Exception as e:
                st.error(f"Failed to load recommendations: {str(e)}")
                traceback.print_exc()
        try:
            # Phone number search
            # st.subheader("Search by Phone Number")
            st.markdown(
                "##### Search by Phone Number"
            )
            search_phone = st.text_input("Enter customer phone number (e.g., +251912345678)", placeholder="e.g., 0912345678")
            
            if search_phone.strip():
                search_phone = search_phone.strip()
                # Validate phone number format
                if not (
                    (search_phone.startswith('09') and len(search_phone) == 10) or
                    (search_phone.startswith('+2519') and len(search_phone) == 13)
                ) or not search_phone.replace('+', '').isdigit():
                    st.error("Invalid phone number format. Must start with '09' (10 digits) or '+2519' (13 characters).")
                    return
                from dependence import search_allget_recommendations
                search = search_allget_recommendations(search_phone)
                # Convert to DataFrame
                br_result = pd.DataFrame(search) if search else pd.DataFrame()
                
                if br_result.empty:
                    st.warning("No documents found for this phone number")
                else:
                    # br_result = pd.DataFrame(search)
                    # Rename columns
                    br_result = br_result.rename(columns={
                        'district': 'District',
                        'full_Name': 'Branch',
                        'full_name': 'Full Name',
                        'customer_phone': 'Phone',
                        'customer_account': 'Account',
                        'reason': 'Reason',
                        'register_date': 'Submission Date',
                        'status': 'Status',
                        'document_path': 'Document Path',
                        'filename': 'Filename',
                        'file_type': 'Document Type',
                    })
                    
                    if len(br_result) == 0:
                        st.warning("No documents found for this phone number")
                    else:
                        # Display basic info
                        st.write(f"Found {len(br_result)} document(s) for phone: {search_phone}")
                        st.dataframe(
                            br_result[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Display each document found
                        for _, row in br_result.iterrows():
                            phone = row['Phone']
                            file_path = row['Document Path']
                            filename = row['Filename']
                            current_status = row['Status']
                            file_type = row['Document Type']
                            
                            # Create expandable section for each document
                            with st.expander(f"Document: {filename} (Status: {current_status})", expanded=True):
                                col1, col2 = st.columns([3, 1])  # 3:1 ratio for preview:controls
                                
                                with col1:
                                    # Document Preview Section
                                    st.subheader("Document Preview")
                                    try:
                                        if not os.path.exists(file_path):
                                            st.warning(f"File not found: {filename}")
                                        else:
                                            if file_type == 'application/pdf':
                                                with open(file_path, "rb") as f:
                                                    pdf_content = f.read()
                                                base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                                                pdf_display = f'''
                                                <div style="width:100%; height:75vh;">
                                                    <iframe src="data:application/pdf;base64,{base64_pdf}" 
                                                            width="100%" 
                                                            height="100%" 
                                                            style="border:none;">
                                                    </iframe>
                                                </div>
                                                '''
                                                st.markdown(pdf_display, unsafe_allow_html=True)
                                            
                                            elif file_type in ['image/png', 'image/jpeg']:
                                                with Image.open(file_path) as img:
                                                    st.image(img, caption=filename, use_container_width=True)
                                            
                                            else:
                                                st.warning(f"Unsupported file type: {file_type}")
                                                st.download_button(
                                                    label="Download File",
                                                    data=open(file_path, "rb").read(),
                                                    file_name=filename,
                                                    mime=file_type
                                                )
                                    except Exception as e:
                                        st.error(f"Error loading document: {str(e)}")
                                        traceback.print_exc()
                                
                                with col2:
                                    # Approval Controls Section
                                    with st.form(key=f"approval_{phone}_{filename}", clear_on_submit=True):
                                        st.subheader("Review Actions")
                                        
                                        # Status selector
                                        new_status = st.selectbox(
                                            "Change Status",
                                            options=["Approved", "Rejected", "Blocked", "Pending"],
                                            index=["Approved", "Rejected", "Blocked", "Pending"].index(current_status),
                                            key=f"status_{phone}_{filename}"
                                        )
                                        
                                        # Notes field
                                        notes = st.text_area(
                                            "Review Notes",
                                            value="",
                                            key=f"notes_{phone}_{filename}",
                                            help="Required for Rejected status"
                                        )
                                        
                                        # Submit button
                                        submitted = st.form_submit_button("Update Status")
                                        if submitted:
                                            notes_stripped = notes.strip()
                                            
                                            # Validation
                                            if new_status == current_status:
                                                st.info("Status unchanged - no update needed")
                                            elif new_status == "Rejected" and not notes_stripped:
                                                st.warning("Please provide notes when rejecting")
                                            elif role == "recomandation":
                                                st.warning("You do not have permission to update the status of this recommendation.")
                                            else:
                                                try:
                                                    from dependence import update_recommendation_status
                                                    if update_recommendation_status(
                                                        phone=phone,
                                                        new_status=new_status,
                                                        notes=notes_stripped,
                                                        username=username
                                                    ):
                                                        st.success("✅ Status updated successfully!")
                                                        time.sleep(1.5)
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Update failed - please try again")
                                                except Exception as e:
                                                    st.error(f"Database error: {str(e)}")
                                                    traceback.print_exc()
                
            # Show all recommendations if no search
            else:
                st.info("Enter a phone number above to view specific documents")
                
        except Exception as e:
            st.error(f"Failed to load recommendations: {str(e)}")
            traceback.print_exc()
    
    elif role == "Sales Admin" or role == "under_admin":
        total_recommendation = total_recommendations()
        total_df = pd.DataFrame(total_recommendation)
        col1, col2, col3, col4 = st.columns(4)
         # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        col1.metric(label="**Total Pending**", value=total_df['pending_count'], delta="Pending")
        col2.metric(label="**Total Approved**", value=total_df['approved_count'], delta="Approved")
        col3.metric(label="**Total Rejected**", value=total_df['rejected_count'], delta="Rejected")
        col4.metric(label="**Total Blocked**", value=total_df['blocked_count'], delta="Blocked")
        # col4.metric(label="***Total Blocked***", value=0, delta="unrecognized questions")
        style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

        # st.write(f"Total Recommendations: {total_recommendation}")
        st.markdown(
            "##### Pending Loan Recommendations &nbsp; <span style='color: #00adef; font-weight: 600;'>(For Today)</span>",
            unsafe_allow_html=True
        )

            
        from dependence import allget_recommendations
        
        try:
            recommendations = allget_recommendations()
            
            if not recommendations:
                st.info("No Pending recommendations found today.")
            else:
                # Convert to DataFrame
                df = pd.DataFrame(recommendations)
                
                # Rename columns
                df = df.rename(columns={
                    'district': 'District',
                    'full_Name': 'Branch',
                    'full_name': 'Full Name',
                    'customer_phone': 'Phone',
                    'customer_account': 'Account',
                    'reason': 'Reason',
                    'register_date': 'Submission Date',
                    'status': 'Status',
                    'document_path': 'Document Path',
                    'filename': 'Filename',
                    'file_type': 'Document Type',
                })

                # Create a column for view buttons
                df['View'] = False

                # Display the table with interactive buttons
                edited_df = st.data_editor(
                    df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status', 'View']],
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
                    phone = selected_row['Phone']
                    
                    # Document preview and approval section
                    st.subheader(f"Document Preview: {phone}")

                    try:
                        
                        # Check file existence
                        if not os.path.exists(file_path):
                            st.warning(f"File not found: {filename}")
                        else:
                            # Handle PDF files
                            if file_type == 'application/pdf':
                                try:
                                    with open(file_path, "rb") as f:
                                        file_content = f.read()  # Read all content at once
                                    base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                    st.markdown(pdf_display, unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Failed to load PDF: {str(e)}")
                                    traceback.print_exc()
                            
                            # Handle image files
                            elif file_type in ['image/png', 'image/jpeg']:
                                try:
                                    with Image.open(file_path) as img:
                                        # Create a copy to ensure the image is loaded into memory
                                        img_copy = img.copy()
                                    st.image(img_copy, caption=filename, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Failed to load image: {str(e)}")
                                    traceback.print_exc()
                            
                            else:
                                st.warning("Unsupported file type for preview")
                        

                    except OSError as oe:
                        if "WinError 10055" in str(oe):
                            st.error("System resource error: Please try again later or close other applications")
                        else:
                            st.error(f"File access error: {str(oe)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                        traceback.print_exc()

                            

        except Exception as e:
                st.error(f"Failed to load recommendations: {str(e)}")
                traceback.print_exc()
        try:
            # Phone number search
            # st.subheader("Search by Phone Number")
            st.markdown(
                "##### Search by Phone Number"
            )
            search_phone = st.text_input("Enter customer phone number (e.g., +251912345678)", placeholder="e.g., +251912345678")
            
            if search_phone.strip():
                search_phone = search_phone.strip()
                # Validate phone number format
                if not (
                    (search_phone.startswith('09') and len(search_phone) == 10) or
                    (search_phone.startswith('+2519') and len(search_phone) == 13)
                ) or not search_phone.replace('+', '').isdigit():
                    st.error("Invalid phone number format. Must start with '09' (10 digits) or '+2519' (13 characters).")
                    return
                from dependence import search_allget_recommendations
                search = search_allget_recommendations(search_phone)
                # Convert to DataFrame
                br_result = pd.DataFrame(search) if search else pd.DataFrame()
                
                if br_result.empty:
                    st.warning("No documents found for this phone number")
                else:
                    # br_result = pd.DataFrame(search)
                    # Rename columns
                    br_result = br_result.rename(columns={
                        'district': 'District',
                        'full_Name': 'Branch',
                        'full_name': 'Full Name',
                        'customer_phone': 'Phone',
                        'customer_account': 'Account',
                        'reason': 'Reason',
                        'register_date': 'Submission Date',
                        'status': 'Status',
                        'document_path': 'Document Path',
                        'filename': 'Filename',
                        'file_type': 'Document Type',
                    })
                    
                    if len(br_result) == 0:
                        st.warning("No documents found for this phone number")
                    else:
                        # Display basic info
                        st.write(f"Found {len(br_result)} document(s) for phone: {search_phone}")
                        st.dataframe(
                            br_result[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Display each document found
                        for _, row in br_result.iterrows():
                            phone = row['Phone']
                            file_path = row['Document Path']
                            filename = row['Filename']
                            current_status = row['Status']
                            file_type = row['Document Type']
                            
                            # Create expandable section for each document
                            with st.expander(f"Document: {filename} (Status: {current_status})", expanded=True):
                            
                                # Document Preview Section
                                st.subheader("Document Preview")
                                try:
                                    if not os.path.exists(file_path):
                                        st.warning(f"File not found: {filename}")
                                    else:
                                        if file_type == 'application/pdf':
                                            with open(file_path, "rb") as f:
                                                pdf_content = f.read()
                                            base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                                            pdf_display = f'''
                                            <div style="width:100%; height:75vh;">
                                                <iframe src="data:application/pdf;base64,{base64_pdf}" 
                                                        width="100%" 
                                                        height="100%" 
                                                        style="border:none;">
                                                </iframe>
                                            </div>
                                            '''
                                            st.markdown(pdf_display, unsafe_allow_html=True)
                                        
                                        elif file_type in ['image/png', 'image/jpeg']:
                                            with Image.open(file_path) as img:
                                                st.image(img, caption=filename, use_container_width=True)
                                        
                                        else:
                                            st.warning(f"Unsupported file type: {file_type}")
                                            st.download_button(
                                                label="Download File",
                                                data=open(file_path, "rb").read(),
                                                file_name=filename,
                                                mime=file_type
                                            )
                                except Exception as e:
                                    st.error(f"Error loading document: {str(e)}")
                                    traceback.print_exc()
                                
                                
            # Show all recommendations if no search
            else:
                st.info("Enter a phone number above to view specific documents")
                
        except Exception as e:
            st.error(f"Failed to load recommendations: {str(e)}")
            traceback.print_exc()

    else:
        # total_recommendation = total_recommendations()
        # total_df = pd.DataFrame(total_recommendation)
        # col1, col2, col3, col4 = st.columns(4)
        #  # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
        # col1.metric(label="**Total Pending**", value=total_df['pending_count'], delta="Pending")
        # col2.metric(label="**Total Approved**", value=total_df['approved_count'], delta="Approved")
        # col3.metric(label="**Total Rejected**", value=total_df['rejected_count'], delta="Rejected")
        # col4.metric(label="**Total Blocked**", value=total_df['blocked_count'], delta="Blocked")
        # # col4.metric(label="***Total Blocked***", value=0, delta="unrecognized questions")
        # style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")
        # # st.subheader("Pending Loan Recommendations")
        st.markdown(
            "##### Pending Loan Recommendations &nbsp; <span style='color: #00adef; font-weight: 600;'>(For Today)</span>",
            unsafe_allow_html=True
        )
            
        from dependence import allget_recommendations
        
        try:
            recommendations = allget_recommendations()
            
            if not recommendations:
                st.info("No Pending recommendations found today.")
            else:
                # Convert to DataFrame
                df = pd.DataFrame(recommendations)
                
                # Rename columns
                df = df.rename(columns={
                    'district': 'District',
                    'full_Name': 'Branch',
                    'full_name': 'Full Name',
                    'customer_phone': 'Phone',
                    'customer_account': 'Account',
                    'reason': 'Reason',
                    'register_date': 'Submission Date',
                    'status': 'Status',
                    'document_path': 'Document Path',
                    'filename': 'Filename',
                    'file_type': 'Document Type',
                })

                # Create a column for view buttons
                df['View'] = False

                # Display the table with interactive buttons
                edited_df = st.data_editor(
                    df[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'View', 'Status', 'Submission Date']],
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
                    phone = selected_row['Phone']
                    
                    # Document preview and approval section
                    st.subheader(f"Document Preview: {phone}")

                    try:
                        col11, col21 = st.columns([3, 1])  # 3:1 ratio for preview:controls
                        with col11:
                            # Check file existence
                            if not os.path.exists(file_path):
                                st.warning(f"File not found: {filename}")
                            else:
                                # Handle PDF files
                                if file_type == 'application/pdf':
                                    try:
                                        with open(file_path, "rb") as f:
                                            file_content = f.read()  # Read all content at once
                                        base64_pdf = base64.b64encode(file_content).decode('utf-8')
                                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                                        st.markdown(pdf_display, unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"Failed to load PDF: {str(e)}")
                                        traceback.print_exc()
                                
                                # Handle image files
                                elif file_type in ['image/png', 'image/jpeg']:
                                    try:
                                        with Image.open(file_path) as img:
                                            # Create a copy to ensure the image is loaded into memory
                                            img_copy = img.copy()
                                        st.image(img_copy, caption=filename, use_container_width=True)
                                    except Exception as e:
                                        st.error(f"Failed to load image: {str(e)}")
                                        traceback.print_exc()
                                
                                else:
                                    st.warning("Unsupported file type for preview")
                        with col21:

                            # Approval controls section
                            with st.form(key=f"approval_form_{phone}", clear_on_submit=True):
                                # Get current status (with case normalization)
                                current_status = selected_row['Status'].capitalize()
                                
                                # Status options with current selection
                                status_options = ["Approved", "Rejected", "Blocked", "Pending"]
                                new_status = st.selectbox(
                                    "Action",
                                    options=status_options,
                                    index=status_options.index(current_status),
                                    key=f"status_{phone}"
                                )
                                
                                # Notes field
                                notes = st.text_area(
                                    "Review Notes",
                                    value="",
                                    key=f"notes_{phone}",
                                    help="Enter review comments (optional)"
                                )
                                
                                # Form submission
                                submitted = st.form_submit_button("Update Status")
                                if submitted:
                                    notes_stripped = notes.strip()
                                    
                                    # Check if status changed
                                    if new_status == current_status:
                                        st.info("No changes detected. Update skipped.")
                                    
                                    # Validate notes for non-approved actions
                                    elif new_status != "Approved" and not notes_stripped:
                                        st.warning("Please provide review notes for non-Approved actions.")
                                    
                                    else:
                                        try:
                                            
                                            if current_status != "Pending":
                                                # Check if notes are provided for non-approved actions
                                                if username != get_by_user_id(phone):
                                                    st.warning("You are not authorized to change the status of this document.")
                                                    return
                                            from dependence import update_recommendation_status
                                            # Update status in database
                                            if update_recommendation_status(phone, new_status, notes_stripped, username):
                                                # Success feedback
                                                success_placeholder = st.empty()
                                                success_placeholder.success("Status updated successfully!")
                                                st.balloons()
                                                
                                                # Clear success message after delay
                                                time.sleep(4)
                                                success_placeholder.empty()
                                                
                                                # Force refresh of the page to show updated status
                                                st.rerun()
                                            else:
                                                st.error("Failed to update status. Please try again.")
                                        
                                        except Exception as e:
                                            st.error(f"Error during status update: {str(e)}")
                                            traceback.print_exc()

                    except OSError as oe:
                        if "WinError 10055" in str(oe):
                            st.error("System resource error: Please try again later or close other applications")
                        else:
                            st.error(f"File access error: {str(oe)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                        traceback.print_exc()

                            

        except Exception as e:
                st.error(f"Failed to load recommendations: {str(e)}")
                traceback.print_exc()
        try:
            # Phone number search
            # st.subheader("Search by Phone Number")
            st.markdown(
                "##### Search by Phone Number"
            )
            search_phone = st.text_input("Enter customer phone number (e.g., +251912345678)", placeholder="Enter phone number (must start with '09' or '+2519')")
            
            if search_phone.strip():
                search_phone = search_phone.strip()
                # Validate phone number format
                if not (
                    (search_phone.startswith('09') and len(search_phone) == 10) or
                    (search_phone.startswith('+2519') and len(search_phone) == 13)
                ) or not search_phone.replace('+', '').isdigit():
                    st.error("Invalid phone number format. Must start with '09' (10 digits) or '+2519' (13 characters).")
                    return
                from dependence import search_allget_recommendations
                search = search_allget_recommendations(search_phone)
                # Convert to DataFrame
                br_result = pd.DataFrame(search) if search else pd.DataFrame()
                
                if br_result.empty:
                    st.warning("No documents found for this phone number")
                else:
                    # br_result = pd.DataFrame(search)
                    # Rename columns
                    br_result = br_result.rename(columns={
                        'district': 'District',
                        'full_Name': 'Branch',
                        'full_name': 'Full Name',
                        'customer_phone': 'Phone',
                        'customer_account': 'Account',
                        'reason': 'Reason',
                        'register_date': 'Submission Date',
                        'status': 'Status',
                        'document_path': 'Document Path',
                        'filename': 'Filename',
                        'file_type': 'Document Type',
                    })
                    
                    if len(br_result) == 0:
                        st.warning("No documents found for this phone number")
                    else:
                        # Display basic info
                        st.write(f"Found {len(br_result)} document(s) for phone: {search_phone}")
                        st.dataframe(
                            br_result[['District', 'Branch', 'Full Name', 'Phone', 'Account', 'Reason', 'Submission Date', 'Status']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Display each document found
                        for _, row in br_result.iterrows():
                            phone = row['Phone']
                            file_path = row['Document Path']
                            filename = row['Filename']
                            current_status = row['Status']
                            file_type = row['Document Type']
                            
                            # Create expandable section for each document
                            with st.expander(f"Document: {filename} (Status: {current_status})", expanded=True):
                                col1, col2 = st.columns([3, 1])  # 3:1 ratio for preview:controls
                                
                                with col1:
                                    # Document Preview Section
                                    st.subheader("Document Preview")
                                    try:
                                        if not os.path.exists(file_path):
                                            st.warning(f"File not found: {filename}")
                                        else:
                                            if file_type == 'application/pdf':
                                                with open(file_path, "rb") as f:
                                                    pdf_content = f.read()
                                                base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
                                                pdf_display = f'''
                                                <div style="width:100%; height:75vh;">
                                                    <iframe src="data:application/pdf;base64,{base64_pdf}" 
                                                            width="100%" 
                                                            height="100%" 
                                                            style="border:none;">
                                                    </iframe>
                                                </div>
                                                '''
                                                st.markdown(pdf_display, unsafe_allow_html=True)
                                            
                                            elif file_type in ['image/png', 'image/jpeg']:
                                                with Image.open(file_path) as img:
                                                    st.image(img, caption=filename, use_container_width=True)
                                            
                                            else:
                                                st.warning(f"Unsupported file type: {file_type}")
                                                st.download_button(
                                                    label="Download File",
                                                    data=open(file_path, "rb").read(),
                                                    file_name=filename,
                                                    mime=file_type
                                                )
                                    except Exception as e:
                                        st.error(f"Error loading document: {str(e)}")
                                        traceback.print_exc()
                                
                                with col2:
                                    # Approval Controls Section
                                    with st.form(key=f"approval_{phone}_{filename}", clear_on_submit=True):
                                        st.subheader("Review Actions")
                                        
                                        # Status selector
                                        new_status = st.selectbox(
                                            "Change Status",
                                            options=["Approved", "Rejected", "Blocked", "Pending"],
                                            index=["Approved", "Rejected", "Blocked", "Pending"].index(current_status),
                                            key=f"status_{phone}_{filename}"
                                        )
                                        
                                        # Notes field
                                        notes = st.text_area(
                                            "Review Notes",
                                            value="",
                                            key=f"notes_{phone}_{filename}",
                                            help="Required for Rejected status"
                                        )
                                        
                                        # Submit button
                                        submitted = st.form_submit_button("Update Status")
                                        if submitted:
                                            notes_stripped = notes.strip()
                                            
                                            if current_status != "Pending":
                                                # Check if notes are provided for non-approved actions
                                                if username != get_by_user_id(phone):
                                                    st.warning("You are not authorized to change the status of this document.")
                                                    return
                                            # Validation
                                            if new_status == current_status:
                                                st.info("Status unchanged - no update needed")
                                            elif new_status == "Rejected" and not notes_stripped:
                                                st.warning("Please provide notes when rejecting")
                                            else:
                                                try:
                                                    from dependence import update_recommendation_status
                                                    if update_recommendation_status(
                                                        phone=phone,
                                                        new_status=new_status,
                                                        notes=notes_stripped,
                                                        username=username
                                                    ):
                                                        st.success("✅ Status updated successfully!")
                                                        time.sleep(1.5)
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Update failed - please try again")
                                                except Exception as e:
                                                    st.error(f"Database error: {str(e)}")
                                                    traceback.print_exc()
                
            # Show all recommendations if no search
            else:
                st.info("Enter a phone number above to view specific documents")
                
        except Exception as e:
            st.error(f"Failed to load recommendations: {str(e)}")
            traceback.print_exc()
      
    # Run cleanup at startup
    run_daily_cleanup()


        
if __name__ == "__main__":
    main()

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
