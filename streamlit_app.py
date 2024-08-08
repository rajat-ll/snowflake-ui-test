import pandas as pd
import numpy as np
import snowflake.connector
from datetime import datetime
import streamlit as st
import time
from snowflake.connector.pandas_tools import write_pandas
import data_edit_ui_page

import login_page

def main():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    if st.session_state.current_page == 'login':
        login_page.login()
    elif st.session_state.current_page == 'editui':
        data_edit_ui_page.edit_ui()

if __name__ == "__main__":
    main()
