import pandas as pd
import streamlit as st
import time

# Load the CSV files
login_creds = pd.read_csv('login_creds.csv')
dept_tables = pd.read_csv('table_dept_mapping.csv')

# Define the login function
def login():
    # Initialize session state variables
    if 'allowed_tables_list' not in st.session_state:
        st.session_state.allowed_tables_list = []
    if 'user' not in st.session_state:
        st.session_state.user = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Main title with styling
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Liquiloans Data Editor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Please login to access the dashboard</p>", unsafe_allow_html=True)

    # Only display login form if the user is not logged in
    if not st.session_state.user:
        # Create columns for layout
        cols = st.columns([2, 6, 6, 2])

        # Username input with a unique key
        with cols[1]:
            username = st.text_input("Enter Username", placeholder="Username", help="Enter your username here", key="username_input_unique")
        
        # Password input with a unique key
        with cols[2]:
            pswrd = st.text_input("Enter Password", type="password", placeholder="Password", help="Enter your password here", key="password_input_unique")

        # Combine username and password for authentication
        inputkey = f"{username}_{pswrd}"
        st.session_state.username = username

        # Create a centered button for login
        cols = st.columns([3, 2, 3])
        with cols[1]:
            login_button = st.button("Login", use_container_width=True, key="login_button_unique")

        # Validate login when the button is clicked
        if login_button:
            if inputkey in login_creds.key.unique():
                st.session_state.user = True
                dept = login_creds.loc[login_creds['key'].isin([inputkey]), 'team']
                if len(st.session_state.allowed_tables_list) == 0:
                    st.session_state.allowed_tables_list.extend(
                        table.strip() for tables in dept_tables.loc[dept_tables['team'].str.contains(dept.values[0]), 'tables'] for table in tables.split(',')
                    )
                    st.session_state.allowed_tables_list = list(set(st.session_state.allowed_tables_list))

                st.success("User Validated! Redirecting...", icon="✅")
                time.sleep(2)
                st.session_state.current_page = 'editui'
                st.experimental_rerun()
            else:
                st.error("Invalid Username or Password", icon="🚫")

# Call the login function
login()
