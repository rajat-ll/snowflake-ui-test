import pandas as pd
import streamlit as st
import time

# Load credentials and department mappings
login_creds = pd.read_csv('login_creds.csv')
dept_tables = pd.read_csv('table_dept_mapping.csv')

def login():
    # Initialize session states if not already set
    if 'allowed_tables_list' not in st.session_state:
        st.session_state.allowed_tables_list = []
    if 'user' not in st.session_state:
        st.session_state.user = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Title of the login page
    st.title("Liquiloans Data Editor")

    # Username and Password inputs
    cols = st.columns([3, 4, 4, 3])
    with cols[1]:
        username = st.text_input("Enter Username", placeholder="Your Username")
    with cols[2]:
        password = st.text_input("Enter Password", type="password", placeholder="Your Password")

    # Construct the key used for login validation
    user_key = f"{username}_{password}"
    st.session_state.username = username

    # Login button
    cols = st.columns([3, 3])
    with cols[1]:
        if st.button("Login"):
            # Check if the user exists in the login credentials
            if user_key in login_creds['key'].unique():
                st.session_state.user = True
                
                # Get department for the logged-in user
                department = login_creds.loc[login_creds['key'] == user_key, 'team'].values[0]
                
                # Update the allowed tables list if it's empty
                if not st.session_state.allowed_tables_list:
                    tables = dept_tables.loc[dept_tables['team'].str.contains(department), 'tables'].values
                    for table_set in tables:
                        st.session_state.allowed_tables_list.extend([table.strip() for table in table_set.split(',')])
                    st.session_state.allowed_tables_list = list(set(st.session_state.allowed_tables_list))
                
                # Success message and redirect
                st.success("User validated! Redirecting...", icon="✅")
                time.sleep(2)  # Simulate redirection delay
                st.session_state.current_page = 'editui'
                st.experimental_rerun()
            else:
                # Error message for invalid credentials
                st.error("Invalid Username or Password. Please try again.", icon="🚫")
