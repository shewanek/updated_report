import streamlit as st
from navigation import login_bar
from navigation import home_sidebar
from time import sleep
from dependence import get_district_from_db
from dependence import initialize_session, update_activity, check_session_timeout

# Main function to handle user sign-up
def select():
    """
    Handles user sign-up process and form interactions.
    Resets input fields upon successful registration.
    """
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_cs = """
    <style>
        div.block-container {
            # padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
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
        .stButton button:hover {
            background-color: #00bfff; /* Cyan blue on hover */
            color: white; /* Change text color to white on hover */
        }
    </style>
    """
    st.markdown(custom_cs, unsafe_allow_html=True)
    update_activity()
    login_bar()
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

    col1, col2 = st.columns([0.1, 0.9])
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
        <center> <h2 class = "title_dash">Michu User District </h2> </center>
        """
    with col2:
        st.markdown(html_title, unsafe_allow_html=True)
    hide_sidebar_style = """
            <style>
                #MainMenu {visibility: hidden;}
            </style>
        """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)
    # Side bar
    st.sidebar.image("pages/michu.png")
    username = st.session_state.get("username", "")
    full_name = st.session_state.get("full_name", "")
    # st.sidebar.write(f'Welcome, :orange[{full_name}]')
    st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
    role = st.session_state.get('selected_role', 'Select Role')
    # st.write(role)
    home_sidebar()   
    with st.form(key='Create Account'):
        st.subheader(f'Select District for :orange[{role}]')
        if role == 'Sales Admin':
            district_options = []
        else:
            district_options = ['Select District']
        
        
       
        try:
            
            dis_from_db = get_district_from_db()
            if dis_from_db:
                district_options.extend(dis_from_db)
        except Exception:
            st.warning("Failed to retrieve district from the database. Please try again later.")
    
        
        district_key = 'district_input'
            # district_options = st.selectbox('Select District', district_options)

        # district_key = 'district_input'
        # district_options = ['Select District', 'Centeral Finfinne', 'East Finfinne', 'Western Finfinne', 'North Finfinne', 'South Finfinne', 'Adama', 'Asella', 'Hosana', 'Dirree Dhawa', 'Hawassa', 'Chiro', 'Jimma', 'Naqamte', 'Shashamanne', 'Bale', 'Bahirdar Area Relationship', 'Mekele Area Relationship', 'Head Office']
        
        if role == 'Sales Admin' or role == 'collection_user':
            district = st.multiselect('District', district_options, key=district_key)
        elif role == 'District User' or role == 'Branch User':
            district = st.selectbox('District', district_options, key=district_key)
        else:
            district = 'Head office'
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            if st.form_submit_button(':orange[Add User]'):  
                if district == 'Select District' or district == [] or district is None:
                    st.warning('Please select a district.')
                else:
                    st.session_state['selected_role'] = role
                    st.session_state['selected_district'] = district
                    st.switch_page('pages/Signup.py')
        with col2:
            st.write('change  role')
        with col3:
            if st.form_submit_button("change"):
                with st.spinner('Logging in...'):
                    sleep(0.5)
                st.switch_page('pages/district.py')

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
    select()
