import pandas as pd
import numpy as np
import snowflake.connector
from datetime import datetime
import streamlit as st
import time
from snowflake.connector.pandas_tools import write_pandas
import os

def download_files_from_stage():
    ctx = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        database="LL_PROD_RAW_ZONE",
        schema="PUBLIC"
    )
    cs = ctx.cursor()
    files = ["login_creds.csv", "table_dept_mapping.csv", "env_det.yml", "snowflake.yml", "requirements.txt", "login_page.py", "data_edit_ui_page.py", "functions.py", "streamlit_app.py"]
    for file in files:
        cs.execute(f"GET @my_app_stage/{file} file://{file}")
        if os.path.exists(file):
            print(f"Downloaded {file} successfully")
        else:
            print(f"Failed to download {file}")
    cs.close()
    ctx.close()

def main():
    download_files_from_stage()

    # Verify that the files are downloaded before importing
    required_files = ["login_page.py", "data_edit_ui_page.py", "functions.py"]
    for file in required_files:
        if not os.path.exists(file):
            st.error(f"Required file {file} is missing. Please check the Snowflake stage.")
            return

    # Now import the modules
    import login_page
    import data_edit_ui_page

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    if st.session_state.current_page == 'login':
        login_page.login()
    elif st.session_state.current_page == 'editui':
        data_edit_ui_page.edit_ui()

if __name__ == "__main__":
    main()
