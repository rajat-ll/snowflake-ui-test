import pandas as pd
import numpy as np
import snowflake.connector
from datetime import datetime
import streamlit as st
import time
from snowflake.connector.pandas_tools import write_pandas

import login_page
import data_edit_ui_page

def download_files_from_stage():
    ctx = snowflake.connector.connect(
        user=st.secrets["snowflake_user"],
        password=st.secrets["snowflake_password"],
        account=st.secrets["snowflake_account"],
        role=st.secrets["snowflake_role"],
        database="LL_PROD_RAW_ZONE",  
        schema="PUBLIC"  
    )
    cs = ctx.cursor()
    files = ["login_creds.csv", "table_dept_mapping.csv", "env_det.yml", "snowflake.yml"]
    for file in files:
        cs.execute(f"GET @my_app_stage/{file} file://{file}")
    cs.close()
    ctx.close()

def main():
    download_files_from_stage()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    if st.session_state.current_page == 'login':
        login_page.login()
    elif st.session_state.current_page == 'editui':
        data_edit_ui_page.edit_ui()

if __name__ == "__main__":
    main()
