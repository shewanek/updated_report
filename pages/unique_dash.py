import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
from navigation import home_sidebar
from dependence import  load_unquie, load_account, load_disbursment
from dependence import initialize_session, update_activity, check_session_timeout




# # Initialize session when app starts
# if 'logged_in' not in st.session_state:
#     initialize_session()

# Check timeout on every interaction
check_session_timeout()

# Function to establish MySQL connection
# @st.cache_resource
# @st.cache_resource(allow_output_mutation=True)
# Function to establish MySQL connection (with error handling and resource cleanup)



def main():
    # Set page configuration, menu, and minimize top padding
    st.set_page_config(page_title="Michu Report", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="collapsed")
    custom_cs = """
    <style>
        div.block-container {
            padding-top: 1.5rem; /* Adjust this value to reduce padding-top */
        }
        #MainMenu { visibility: hidden; }
        .stDeployButton { visibility: hidden; }
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
    custom_css = """
    <style>
        div.block-container {
            padding-top: 0.1rem; /* Adjust this value to reduce padding-top */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    customm = """
        <style>
            .app-header {
                display: none;
            }
        </style>
        """

    # Apply the custom CSS
    st.markdown(customm, unsafe_allow_html=True)
    update_activity()

    
    # Auto-refresh interval (in seconds)
    refresh_interval = 6600  # Adjust as needed (e.g., 10 minutes for real-time)
    st_autorefresh(interval=refresh_interval * 1000, key="Michu Bot dash")


    # image = Image.open('pages/michu.png')

    col1, col2 = st.columns([0.1,0.9])
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
        <center> <h3 class = "title_dash"> Michu Customer  Dashboard (<span style="color: #00adef; font-size: 20px;">Year to date</span>)</h3> </center>
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
    

    # Fetch data from different tables
    # Database connection and data fetching (with error handling)
    role = st.session_state.get("role", "")
    username = st.session_state.get("username", "")
    try:
        tab_options = ["Unique Customer", "Account Number", "Total Disbursement"]
        active_tab = st.radio("Select a Tab", tab_options, horizontal=True)
        if active_tab == "Unique Customer":
            
            df_combine = load_unquie(role, username)
            
            # Side bar
            st.sidebar.image("pages/michu.png")
            # username = st.session_state.get("username", "")
            full_name = st.session_state.get("full_name", "")
            # st.sidebar.write(f'Welcome, :orange[{full_name}]')
            st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
            st.sidebar.header("Please filter")
            district = st.sidebar.multiselect("Select District", options=df_combine["District"].dropna().unique())

            if not district:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["District"].isin(district)]
            branch = st.sidebar.multiselect("Select Branch", options=df_combine["Branch"].dropna().unique())
            if not branch:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]

                
            if df_combine is not None and not df_combine.empty:
                col1, col2 = st.sidebar.columns((2))
                # df_combine["Disbursed_date"] = pd.to_datetime(df_combine["Disbursed_date"])

                # Getting the min and max date 
                startDate = df_combine["Disbursed Date"].min()
                endDate = df_combine["Disbursed Date"].max()

                with col1:
                    date1 = st.date_input("Start Date", startDate, min_value=startDate, max_value=endDate)

                with col2:
                    date2 = st.date_input("End Date", endDate, min_value=startDate, max_value=endDate)

                df_combine = df_combine[(df_combine["Disbursed Date"] >= date1) & (df_combine["Disbursed Date"] <= date2)].copy()
            

            if not district and not branch:
                df_combine = df_combine
            elif district:
                df_combine = df_combine[df_combine["District"].isin(district)]
            elif branch:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]
            else:
                df_combine = df_combine[df_combine["District"].isin(district) & df_combine["Branch"].isin(branch)]

            
            # Hide the sidebar by default with custom CSS
            hide_sidebar_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                </style>
            """
            st.markdown(hide_sidebar_style, unsafe_allow_html=True)

            home_sidebar()
        
            st.markdown(
                """
                <style>
                .metric-card-container {
                    padding-top: 0.2rem;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            
            col1, col2, col3 = st.columns(3)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col1.metric(label="**Total Rigister Customer**", value=df_combine.uniqueId.nunique(), delta="Customer")
            col2.metric(label="**Total District**", value=df_combine.District.nunique(), delta="District")
            col3.metric(label="**Total Branch**", value=df_combine.Branch.nunique(), delta="Branch")
            # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
            # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

            # Grouping data by District and counting ConversionId
            category_df = df_combine.groupby(by=["District"], as_index=False)["uniqueId"].count()
            category_df.rename(columns={"uniqueId": "Total Registered"}, inplace=True)

            # Creating the bar chart
            # st.subheader("Total Registered by District")
            fig = px.bar(
                category_df, 
                x="District", 
                y="Total Registered", 
                text="Total Registered", 
                template="seaborn",
                hover_data={"Total Registered": True},  # Display Total Registered on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels
            fig.update_traces(textposition='outside')  # Show text outside the bars
            fig.update_layout(
                xaxis_title="District Name",
                yaxis_title="Total Registered",
                title="Total Registered Customers by District",
                height=500  # Adjust height as needed
            )

            # Displaying the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            
            
            # Grouping data by Branch and counting ConversionId
            branch_df = df_combine.groupby(by=["Branch"], as_index=False)["uniqueId"].count()
            branch_df.rename(columns={"uniqueId": "Total Registered"}, inplace=True)

            # Sorting and selecting the top 10 branches
            top_branches_df = branch_df.sort_values(by="Total Registered", ascending=False).head(10)

            # Creating the horizontal bar chart for branches
            fig_branch = px.bar(
                top_branches_df, 
                y="Branch", 
                x="Total Registered", 
                text="Total Registered", 
                template="seaborn",
                orientation='h',  # Horizontal bar chart
                hover_data={"Total Registered": True},  # Display Total Registered on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels for branch chart
            fig_branch.update_traces(textposition='outside')  # Show text outside the bars
            fig_branch.update_layout(
                xaxis_title="Total Registered",
                yaxis_title="Branch Name",
                title="Top 10 Branches by Total Registered Customers",
                height=500  # Adjust height as needed
            )

            # Displaying the branch chart in Streamlit
            st.plotly_chart(fig_branch, use_container_width=True)

            col4, col5 = st.columns([0.6,0.4])
            # Categorize Product Type based on Disbursed Amount
            # df_combine['Product Type'] = df_combine['Disbursed Amount'].apply(lambda x: 'Guya' if x < 50000 else 'Wabi')
            with col5:
                # Grouping data by Product Type and counting ConversionId
                product_df = df_combine.groupby(by=["Product Type"], as_index=False)["uniqueId"].count()
                product_df.rename(columns={"uniqueId": "Total Registered"}, inplace=True)

                # Creating the pie chart for product types
                fig_product = px.pie(
                    product_df, 
                    names="Product Type", 
                    values="Total Registered", 
                    hole = 0.5,
                    title="Distribution of Registered Customers by Product Type"
                    # color_discrete_sequence=px.colors.sequential.Cyans  # Set pie chart colors
                )

                # Updating layout and labels for product chart
                fig_product.update_traces(textposition='inside', textinfo='percent+label')
                fig_product.update_layout(
                    height=500  # Adjust height as needed
                )

                # Displaying the product pie chart in Streamlit
                st.plotly_chart(fig_product, use_container_width=True)

            with col4:
                # Group by Branch and aggregate data
                grouped_df = df_combine.groupby(["District", "Branch", "Product Type"]).agg(Total_Registered=("uniqueId", "count")).reset_index().rename(lambda x: x + 1)

                # Display the grouped data in a table
                st.write(":orange[Grouped Data by Branch 👇🏻]")
                st.dataframe(grouped_df)

                # Option to download the grouped data as CSV
                csv = grouped_df.to_csv(index=False)
                st.download_button(label=":blue[Download CSV]", data=csv, file_name='grouped_data.csv', mime='text/csv')


            # # Display data in a table
            # st.write(":orange[Customer List 👇🏻]")
            # # st.write(df_combine.drop(columns=['uniqueId', 'userName']))
            # st.write(df_combine.drop(columns=['uniqueId', 'userName']).reset_index(drop=True).rename(lambda x: x + 1))

            # df = df_combine.drop(columns=['uniqueId', 'userName'])

            # # Create a download button
            # csv = df.to_csv(index=False)
            # st.download_button(
            #     label=":blue[Download CSV]",
            #     data=csv,
            #     file_name='unique_data.csv',
            #     mime='text/csv'
            # )
        
        elif active_tab == "Account Number":
            df_combine = load_account(role, username)
            
            # Side bar
            st.sidebar.image("pages/michu.png")
            # username = st.session_state.get("username", "")
            full_name = st.session_state.get("full_name", "")
            # st.sidebar.write(f'Welcome, :orange[{full_name}]')
            st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
            st.sidebar.header("Please filter")
            district = st.sidebar.multiselect("Select District", options=df_combine["District"].dropna().unique())

            if not district:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["District"].isin(district)]
            branch = st.sidebar.multiselect("Select Branch", options=df_combine["Branch"].dropna().unique())
            if not branch:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]

                
            if df_combine is not None and not df_combine.empty:
                col1, col2 = st.sidebar.columns((2))
                # df_combine["Disbursed_date"] = pd.to_datetime(df_combine["Disbursed_date"])

                # Getting the min and max date 
                startDate = df_combine["Disbursed Date"].min()
                endDate = df_combine["Disbursed Date"].max()

                with col1:
                    date1 = st.date_input("Start Date", startDate, min_value=startDate, max_value=endDate)

                with col2:
                    date2 = st.date_input("End Date", endDate, min_value=startDate, max_value=endDate)

                df_combine = df_combine[(df_combine["Disbursed Date"] >= date1) & (df_combine["Disbursed Date"] <= date2)].copy()
            

            if not district and not branch:
                df_combine = df_combine
            elif district:
                df_combine = df_combine[df_combine["District"].isin(district)]
            elif branch:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]
            else:
                df_combine = df_combine[df_combine["District"].isin(district) & df_combine["Branch"].isin(branch)]

            
            # Hide the sidebar by default with custom CSS
            hide_sidebar_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                </style>
            """
            st.markdown(hide_sidebar_style, unsafe_allow_html=True)

            home_sidebar()
        
            st.markdown(
                """
                <style>
                .metric-card-container {
                    padding-top: 0.2rem;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            
            col1, col2, col3 = st.columns(3)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col1.metric(label="**Total Account Number**", value=df_combine.uniqueId.count(), delta="Customer")
            col2.metric(label="**Total District**", value=df_combine.District.nunique(), delta="District")
            col3.metric(label="**Total Branch**", value=df_combine.Branch.nunique(), delta="Branch")
            # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
            # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

            # Grouping data by District and counting ConversionId
            category_df = df_combine.groupby(by=["District"], as_index=False)["uniqueId"].count()
            category_df.rename(columns={"uniqueId": "Total Account"}, inplace=True)

            # Creating the bar chart
            # st.subheader("Total Account by District")
            fig = px.bar(
                category_df, 
                x="District", 
                y="Total Account", 
                text="Total Account", 
                template="seaborn",
                hover_data={"Total Account": True},  # Display Total Account on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels
            fig.update_traces(textposition='outside')  # Show text outside the bars
            fig.update_layout(
                xaxis_title="District Name",
                yaxis_title="Total Account",
                title="Total Account Number by District",
                height=500  # Adjust height as needed
            )

            # Displaying the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            
            
            # Grouping data by Branch and counting ConversionId
            branch_df = df_combine.groupby(by=["Branch"], as_index=False)["uniqueId"].count()
            branch_df.rename(columns={"uniqueId": "Total Account"}, inplace=True)

            # Sorting and selecting the top 10 branches
            top_branches_df = branch_df.sort_values(by="Total Account", ascending=False).head(10)

            # Creating the horizontal bar chart for branches
            fig_branch = px.bar(
                top_branches_df, 
                y="Branch", 
                x="Total Account", 
                text="Total Account", 
                template="seaborn",
                orientation='h',  # Horizontal bar chart
                hover_data={"Total Account": True},  # Display Total Account on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels for branch chart
            fig_branch.update_traces(textposition='outside')  # Show text outside the bars
            fig_branch.update_layout(
                xaxis_title="Total Account",
                yaxis_title="Branch Name",
                title="Top 10 Branches by Total Account Number",
                height=500  # Adjust height as needed
            )

            # Displaying the branch chart in Streamlit
            st.plotly_chart(fig_branch, use_container_width=True)

            col4, col5 = st.columns([0.6,0.4])
            # Categorize Product Type based on Disbursed Amount
            # df_combine['Product Type'] = df_combine['Disbursed Amount'].apply(lambda x: 'Guya' if x < 50000 else 'Wabi')
            with col5:
                # Grouping data by Product Type and counting ConversionId
                product_df = df_combine.groupby(by=["Product Type"], as_index=False)["uniqueId"].count()
                product_df.rename(columns={"uniqueId": "Total Account"}, inplace=True)

                # Creating the pie chart for product types
                fig_product = px.pie(
                    product_df, 
                    names="Product Type", 
                    values="Total Account", 
                    hole = 0.5,
                    title="Distribution of Account Number by Product Type"
                    # color_discrete_sequence=px.colors.sequential.Cyans  # Set pie chart colors
                )

                # Updating layout and labels for product chart
                fig_product.update_traces(textposition='inside', textinfo='percent+label')
                fig_product.update_layout(
                    height=500  # Adjust height as needed
                )

                # Displaying the product pie chart in Streamlit
                st.plotly_chart(fig_product, use_container_width=True)

            with col4:
                # Group by Branch and aggregate data
                grouped_df = df_combine.groupby(["District", "Branch", "Product Type"]).agg(Total_Registered=("uniqueId", "count")).reset_index().rename(lambda x: x + 1)

                # Display the grouped data in a table
                st.write(":orange[Grouped Data by Branch 👇🏻]")
                st.dataframe(grouped_df)

                # Option to download the grouped data as CSV
                csv = grouped_df.to_csv(index=False)
                st.download_button(label=":blue[Download CSV]", data=csv, file_name='grouped_data.csv', mime='text/csv')


            # # Display data in a table
            # st.write(":orange[Customer List 👇🏻]")
            # # st.write(df_combine.drop(columns=['uniqueId', 'userName']))
            # st.write(df_combine.drop(columns=['uniqueId', 'userName']).reset_index(drop=True).rename(lambda x: x + 1))

            # df = df_combine.drop(columns=['uniqueId', 'userName'])

            # # Create a download button
            # csv = df.to_csv(index=False)
            # st.download_button(
            #     label=":blue[Download CSV]",
            #     data=csv,
            #     file_name='unique_data.csv',
            #     mime='text/csv'
            # )

        elif active_tab == "Total Disbursement":
            df_combine = load_disbursment(role, username)
            
            # Side bar
            # st.write(df_combine)
            st.sidebar.image("pages/michu.png")
            # username = st.session_state.get("username", "")
            full_name = st.session_state.get("full_name", "")
            # st.sidebar.write(f'Welcome, :orange[{full_name}]')
            st.sidebar.markdown(f'<h4> Welcome, <span style="color: #e38524;">{full_name}</span></h4>', unsafe_allow_html=True)
            st.sidebar.header("Please filter")
            district = st.sidebar.multiselect("Select District", options=df_combine["District"].dropna().unique())

            if not district:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["District"].isin(district)]
            branch = st.sidebar.multiselect("Select Branch", options=df_combine["Branch"].dropna().unique())
            if not branch:
                df_combine = df_combine.copy()
            else:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]

                
            if df_combine is not None and not df_combine.empty:
                col1, col2 = st.sidebar.columns((2))
                # df_combine["Disbursed_date"] = pd.to_datetime(df_combine["Disbursed_date"])

                # Getting the min and max date 
                startDate = df_combine["Disbursed Date"].min()
                endDate = df_combine["Disbursed Date"].max()

                with col1:
                    date1 = st.date_input("Start Date", startDate, min_value=startDate, max_value=endDate)

                with col2:
                    date2 = st.date_input("End Date", endDate, min_value=startDate, max_value=endDate)

                df_combine = df_combine[(df_combine["Disbursed Date"] >= date1) & (df_combine["Disbursed Date"] <= date2)].copy()
            

            if not district and not branch:
                df_combine = df_combine
            elif district:
                df_combine = df_combine[df_combine["District"].isin(district)]
            elif branch:
                df_combine = df_combine[df_combine["Branch"].isin(branch)]
            else:
                df_combine = df_combine[df_combine["District"].isin(district) & df_combine["Branch"].isin(branch)]

            
            # Hide the sidebar by default with custom CSS
            hide_sidebar_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                </style>
            """
            st.markdown(hide_sidebar_style, unsafe_allow_html=True)

            home_sidebar()
        
            st.markdown(
                """
                <style>
                .metric-card-container {
                    padding-top: 0.2rem;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            disbursed_amount_sum = float(df_combine.disbursed_amount.sum())
            # Format the amount in billions or millions
            if disbursed_amount_sum >= 1_000_000_000:  # If the amount is >= 1 billion
                formatted_value = f"{disbursed_amount_sum / 1_000_000_000:.2f} B"  # Format as billions
            elif disbursed_amount_sum >= 1_000_000:  # If the amount is >= 1 million
                formatted_value = f"{disbursed_amount_sum / 1_000_000:.2f} M"  # Format as millions
            else:
                formatted_value = f"{disbursed_amount_sum:.2f}"  # Keep as is for smaller amounts
            col1, col2, col3 = st.columns(3)
            # col2.markdown('<style>div.block-container{padding-top:0.0002rem;}</style>', unsafe_allow_html=True)
            col1.metric(label="**Total Disbursement Amount**", value=formatted_value, delta="Customer")
            col2.metric(label="**Total District**", value=df_combine.District.nunique(), delta="District")
            col3.metric(label="**Total Branch**", value=df_combine.Branch.nunique(), delta="Branch")
            # col4.metric(label="***Unrecognized Questions***", value=df_combine[df_combine['intent'] == 'nlu_fallback']['text_id'].nunique(), delta="unrecognized questions")
            # col5.metric(label="***Michu Channel Joined User***", value=df_combine.groupby('user_id')['ch_id'].nunique().sum(), delta="Michu Channel")
            style_metric_cards(background_color="#00adef", border_left_color="#e38524", border_color="#1f66bd", box_shadow="#f71938")

            # Grouping data by District and counting ConversionId
            category_df = df_combine.groupby(by=["District"], as_index=False)["disbursed_amount"].sum()
            category_df.rename(columns={"disbursed_amount": "Total Amount"}, inplace=True)

            # Creating the bar chart
            # st.subheader("Total Account by District")
            fig = px.bar(
                category_df, 
                x="District", 
                y="Total Amount", 
                text="Total Amount", 
                template="seaborn",
                hover_data={"Total Amount": True},  # Display Total Amount on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels
            fig.update_traces(textposition='outside')  # Show text outside the bars
            fig.update_layout(
                xaxis_title="District Name",
                yaxis_title="Total Amount",
                title="Total Amount by District",
                height=500  # Adjust height as needed
            )

            # Displaying the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            
            
            # Grouping data by Branch and counting ConversionId
            branch_df = df_combine.groupby(by=["Branch"], as_index=False)["disbursed_amount"].sum()
            branch_df.rename(columns={"disbursed_amount": "Total Amount"}, inplace=True)

            # Sorting and selecting the top 10 branches
            top_branches_df = branch_df.sort_values(by="Total Amount", ascending=False).head(10)

            # Creating the horizontal bar chart for branches
            fig_branch = px.bar(
                top_branches_df, 
                y="Branch", 
                x="Total Amount", 
                text="Total Amount", 
                template="seaborn",
                orientation='h',  # Horizontal bar chart
                hover_data={"Total Amount": True},  # Display Total Amount on hover
                color_discrete_sequence=['#00adef']  # Set bar color to cyan blue
            )

            # Updating layout and labels for branch chart
            fig_branch.update_traces(textposition='outside')  # Show text outside the bars
            fig_branch.update_layout(
                xaxis_title="Total Amount",
                yaxis_title="Branch Name",
                title="Top 10 Branches by Total Amount",
                height=500  # Adjust height as needed
            )

            # Displaying the branch chart in Streamlit
            st.plotly_chart(fig_branch, use_container_width=True)

            col4, col5 = st.columns([0.6,0.4])
            # Categorize Product Type based on Disbursed Amount
            # df_combine['Product Type'] = df_combine['Disbursed Amount'].apply(lambda x: 'Guya' if x < 50000 else 'Wabi')
            with col5:
                # Grouping data by Product Type and counting ConversionId
                product_df = df_combine.groupby(by=["Product Type"], as_index=False)["disbursed_amount"].sum()
                product_df.rename(columns={"disbursed_amount": "Total Amount"}, inplace=True)

                # Creating the pie chart for product types
                fig_product = px.pie(
                    product_df, 
                    names="Product Type", 
                    values="Total Amount", 
                    hole = 0.5,
                    title="Distribution of Total Amount by Product Type"
                    # color_discrete_sequence=px.colors.sequential.Cyans  # Set pie chart colors
                )

                # Updating layout and labels for product chart
                fig_product.update_traces(textposition='inside', textinfo='percent+label')
                fig_product.update_layout(
                    height=500  # Adjust height as needed
                )

                # Displaying the product pie chart in Streamlit
                st.plotly_chart(fig_product, use_container_width=True)

            with col4:
                # Group by Branch and aggregate data
                grouped_df = df_combine.groupby(["District", "Branch", "Product Type"]).agg(Total_Registered=("disbursed_amount", "sum")).reset_index().rename(lambda x: x + 1)

                # Display the grouped data in a table
                st.write(":orange[Grouped Data by Branch 👇🏻]")
                st.dataframe(grouped_df)

                # Option to download the grouped data as CSV
                csv = grouped_df.to_csv(index=False)
                st.download_button(label=":blue[Download CSV]", data=csv, file_name='grouped_data.csv', mime='text/csv')


            # # Display data in a table
            # st.write(":orange[Customer List 👇🏻]")
            # # st.write(df_combine.drop(columns=['uniqueId', 'userName']))
            # st.write(df_combine.drop(columns=['uniqueId', 'userName']).reset_index(drop=True).rename(lambda x: x + 1))

            # df = df_combine.drop(columns=['uniqueId', 'userName'])

            # # Create a download button
            # csv = df.to_csv(index=False)
            # st.download_button(
            #     label=":blue[Download CSV]",
            #     data=csv,
            #     file_name='unique_data.csv',
            #     mime='text/csv'
            # )

    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")

        



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
  