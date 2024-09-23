import pandas as pd
import streamlit as st
import time
import os

login_creds_path = 'login_creds.csv'
dept_tables = pd.read_csv('table_dept_mapping.csv')

if os.path.exists(login_creds_path):
    login_creds = pd.read_csv(login_creds_path)
else:
    login_creds = pd.DataFrame(columns=['username', 'password', 'key', 'team'])


def display_logo():
    st.image("logo.png", width=200)  

# Login function
def login():
    if 'allowed_tables_list' not in st.session_state:
        st.session_state.allowed_tables_list = []
    if 'user' not in st.session_state:
        st.session_state.user = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Display the logo
    display_logo()

    st.title("Liquiloans Data Editor")

    # Existing user login section
    cols = st.columns([3, 4, 4, 3])
    with cols[1]:
        username = st.text_input("Enter Username", placeholder="Your Username")
    with cols[2]:
        password = st.text_input("Enter Password", type="password", placeholder="Your Password")

    # Construct the key for validation
    user_key = f"{username}_{password}"
    st.session_state.username = username

    cols = st.columns([3, 3])
    with cols[1]:
        if st.button("Login"):
            if user_key in login_creds['key'].unique():
                st.session_state.user = True
                
                # Get the department for the logged-in user
                department = login_creds.loc[login_creds['key'] == user_key, 'team'].values[0]
                
                # Update allowed tables list if empty
                if not st.session_state.allowed_tables_list:
                    tables = dept_tables.loc[dept_tables['team'].str.contains(department), 'tables'].values
                    for table_set in tables:
                        st.session_state.allowed_tables_list.extend([table.strip() for table in table_set.split(',')])
                    st.session_state.allowed_tables_list = list(set(st.session_state.allowed_tables_list))
                
                st.success("User validated! Redirecting...", icon="✅")
                time.sleep(2)
                st.session_state.current_page = 'editui'
                st.experimental_rerun()
            else:
                st.error("Invalid Username or Password. Please try again.", icon="🚫")

    # New user registration section
    st.write("")
    st.markdown("### New User? Register Here")

    with st.form(key='registration_form'):
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        team = st.text_input("Enter Your Team")

        if st.form_submit_button(label="Register"):
            new_key = f"{new_username}_{new_password}"
            if new_key in login_creds['key'].unique():
                st.error("User already exists, please login.")
            else:
                new_entry = {'username': new_username, 'password': new_password, 'key': new_key, 'team': team}
                login_creds = login_creds.append(new_entry, ignore_index=True)
                login_creds.to_csv(login_creds_path, index=False)
                st.success("Registration successful! Please login.")
