import pandas as pd
import streamlit as st
import time

login_creds = pd.read_csv('login_creds.csv')
dept_tables = pd.read_csv('table_dept_mapping.csv')

def login():
    if 'allowed_tables_list' not in st.session_state:
        st.session_state.allowed_tables_list = []
    if 'user' not in st.session_state:
        st.session_state.user = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    st.title("Login Page")

    cols = st.columns([3, 6, 6, 3])
    with cols[1]:
        username = st.text_input("Enter Username")
    with cols[2]:
        pswrd = st.text_input("Enter Password", type="password")
    inputkey = f"{username}_{pswrd}"
    st.session_state.username = username

    cols = st.columns([3, 4])
    with cols[1]:
        if st.button("Login_Rajat"):
            if inputkey in login_creds.key.unique():
                st.session_state.user = True
                dept = login_creds.loc[login_creds['key'].isin([inputkey]), 'team']
                if len(st.session_state.allowed_tables_list) == 0:
                    st.session_state.allowed_tables_list.extend(
                        table.strip() for tables in dept_tables.loc[dept_tables['team'].str.contains(dept.values[0]), 'tables'] for table in tables.split(',')
                    )
                    st.session_state.allowed_tables_list = list(set(st.session_state.allowed_tables_list))
                st.success("User Validated")
                time.sleep(2)
                st.session_state.current_page = 'editui'
                st.experimental_rerun()
            else:
                st.error("Invalid User Credentials")
