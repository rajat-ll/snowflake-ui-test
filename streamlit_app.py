import pandas as pd
import numpy as np
import snowflake.connector
from datetime import datetime
import streamlit as st
import time
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import os
import importlib.util

def download_files_from_stage():
    session = get_active_session()
    target_directory = "downloaded_files"
    os.makedirs(target_directory, exist_ok=True)

    files = ["login_creds.csv", "table_dept_mapping.csv", "env_det.yml", "snowflake.yml", "requirements.txt", "login_page.py", "data_edit_ui_page.py", "functions.py", "streamlit_app.py"]
    for file in files:
        local_path = os.path.join(target_directory, file)
        session.file.get(f"@my_app_stage/{file}", f"file://{local_path}")
        if os.path.isfile(local_path):
            print(f"Downloaded {file} successfully to {local_path}")
        else:
            print(f"Failed to download {file} to {local_path}")

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    download_files_from_stage()

    target_directory = "downloaded_files"
    required_files = ["login_page.py", "data_edit_ui_page.py", "functions.py"]
    
    for file in required_files:
        full_path = os.path.join(target_directory, file)
        if not os.path.isfile(full_path):
            print(f"Required file {file} is missing. Full path checked: {full_path}")
            st.error(f"Required file {file} is missing. Please check the Snowflake stage.")
            return
        else:
            print(f"Required file {file} exists at {full_path}")

    # Import modules from downloaded files
    login_page = import_module_from_file('login_page', os.path.join(target_directory, 'login_page.py'))
    data_edit_ui_page = import_module_from_file('data_edit_ui_page', os.path.join(target_directory, 'data_edit_ui_page.py'))

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    if st.session_state.current_page == 'login':
        login_page.login()
    elif st.session_state.current_page == 'editui':
        data_edit_ui_page.edit_ui()

if __name__ == "__main__":
    main()
