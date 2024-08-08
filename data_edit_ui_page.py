import pandas as pd
import snowflake.connector
from datetime import datetime
import json
import streamlit as st
import time
from snowflake.connector.pandas_tools import write_pandas

from snowflake.snowpark.context import get_active_session
from functions import st_read_from_snowflake, st_execute_query_on_snowflake, generate_update_query, generate_insert_query, apply_filters

st.set_page_config(layout="centered", initial_sidebar_state="collapsed", page_title="Data Editor", page_icon="🧮")

def edit_ui():
    if 'selected_tablename' not in st.session_state:
        st.session_state.selected_tablename = None
    if 'selected_table_df' not in st.session_state:
        st.session_state.selected_table_df = pd.DataFrame()
    if 'filters' not in st.session_state:
        st.session_state.filters = {}
    if 'selected_table_df_original' not in st.session_state:
        st.session_state.selected_table_df_original = pd.DataFrame()
    if 'identifier_column' not in st.session_state:
        st.session_state.identifier_column = None
    if 'submit_button' not in st.session_state:
        st.session_state.submit_button = False
    if 'insert_button' not in st.session_state:
        st.session_state.insert_button = False
    if 'master_pk_list' not in st.session_state:
        st.session_state.master_pk_list = []
    if 'uploaded_pk_list' not in st.session_state:
        st.session_state.uploaded_pk_list = []
    if 'user_query_list' not in st.session_state:
        st.session_state.user_query_list = []
    if 'right_pane_table_view' not in st.session_state:
        st.session_state.right_pane_table_view = True

    st.title("Snowflake Table Editor ❄️")

    a = datetime.now()
    print(f"\nSTART time is {a}")

    st.sidebar.write("Please select the table to edit from below dropdown")
    selected_tablename = st.sidebar.selectbox(
        label="table choice", options=st.session_state.allowed_tables_list, label_visibility="hidden"
    )
    st.write(f"Your selected table is : {selected_tablename}")
    print(st.session_state.selected_tablename, selected_tablename)

    if selected_tablename != st.session_state.selected_tablename:
        st.session_state.filters = {}
        st.session_state.selected_tablename = selected_tablename
        st.session_state.selected_table_df = st_read_from_snowflake(f"Select * from {st.session_state.selected_tablename}")
        print(st.session_state.selected_table_df.info())
        print(st.session_state.selected_table_df.head(3))
    else:
        print(f"already READ from SF")
    st.session_state.selected_table_df_original = st.session_state.selected_table_df

    st.session_state.master_pk_list = st.session_state.selected_table_df_original['ID'].unique()

    b = datetime.now()
    print(f"read successfully in {b-a}")

    with st.sidebar.expander("Add Filters"):
        column_options = st.session_state.selected_table_df.columns.difference(list(st.session_state.filters.keys()))
        cols = st.columns([4, 3])
        with cols[0]:
            column = st.selectbox("Select Column", options=column_options)
            print(f"DType of {column} is : {st.session_state.selected_table_df[column].dtype}")
        with cols[1]:
            if st.session_state.selected_table_df[column].dtype == 'object':
                value = st.text_input("Filter Value", key=column, value=None)
            elif st.session_state.selected_table_df[column].dtype == 'int64':
                value = st.number_input("Filter Value", key=column, step=1, value=1)
            elif st.session_state.selected_table_df[column].dtype == 'float64':
                value = st.number_input("Filter Value", key=column, value=1)
            else:
                value = st.text_input("Filter Value", key=column, value=None)

        cols = st.columns([4, 5])
        with cols[0]:
            if st.button("Apply Filter"):
                st.session_state.filters[column] = value
        with cols[1]:
            if st.button("Remove Filter"):
                st.session_state.filters = {}
                st.session_state.selected_table_df = st.session_state.selected_table_df_original
                st.session_state.right_pane_table_view = True

        st.write(f"Filter applied are :\n{st.session_state.filters}") if len(st.session_state.filters) > 0 else None

    st.session_state.selected_table_df = st.session_state.selected_table_df if any(
        value is None for value in st.session_state.filters.values()
    ) else apply_filters(st.session_state.selected_table_df, st.session_state.filters)

    if st.session_state.right_pane_table_view:
        with st.form("data_editor_form"):
            st.caption("Change below to UPDATE DATA in the selected table")
            edited = st.experimental_data_editor(
                st.session_state.selected_table_df.reset_index(drop=True), use_container_width=True, num_rows="fixed"
            )
            submit_button = st.form_submit_button("Submit Changes")
            st.session_state.submit_button = submit_button

    if st.session_state.submit_button:
        edited_df_pk = edited['ID'].unique()
        if len(edited_df_pk) > 0:
            edited_update_df = edited
            try:
                for index, row in edited_update_df.iterrows():
                    user_query = generate_update_query(row, selected_tablename, 'ID', edited_update_df)
                    if user_query not in st.session_state.user_query_list:
                        st.session_state.user_query_list.append(user_query.strip())
                        st.write(user_query)
                        st_execute_query_on_snowflake(user_query)

                escaped_queries = [q.replace("'", "''") for q in st.session_state.user_query_list]
                user_query_json = json.dumps(escaped_queries)
                update_log_query = f'''
                    INSERT INTO LL_PROD_RAW_ZONE.PUBLIC.STREAMLIT_DATA_EDIT_UI_LOGS (USERNAME, TABLENAME, USER_QUERY, DATETIME) 
                    values ('{st.session_state.username}', '{selected_tablename}', '{user_query_json}', '{datetime.now()}');
                '''
                st.write(f"update query log {update_log_query}")
                st_execute_query_on_snowflake(update_log_query)
                st.success("Table updated")

                time.sleep(5)
                st.session_state.user_query_list = []
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Error UPDATING Edited table: {e}")

    if st.session_state.right_pane_table_view:
        with st.form("data_adding_form"):
            st.caption("Fill below to ADD DATA in the selected table")
            added_df = st.session_state.selected_table_df_original[:1]
            added = st.experimental_data_editor(added_df.reset_index(drop=True), use_container_width=True, num_rows="dynamic")

            insert_button = st.form_submit_button("Submit Additions")
            st.session_state.insert_button = insert_button

    if st.session_state.insert_button:
        added = added[1:]
        added_df_pk = added['ID'].unique()
        added_update_pk_list = [pk for pk in added_df_pk if pk in st.session_state.master_pk_list]
        added_insert_pk_list = list(set(added['ID'].unique()) - set(st.session_state.master_pk_list))

        st.write(f"Added BUT EXISTING keys are {added_update_pk_list}\n while new keys are {added_insert_pk_list}")

        if len(added_insert_pk_list) > 0:
            added_insert_df = added[added['ID'].isin(added_insert_pk_list)]
            st.write(added_insert_df)
            try:
                for index, row in added_insert_df.iterrows():
                    user_query = generate_insert_query(row, selected_tablename, added_insert_df)
                    if user_query not in st.session_state.user_query_list:
                        st.session_state.user_query_list.append(user_query.strip())
                        st.write(user_query)
                        st_execute_query_on_snowflake(user_query)

                escaped_queries = [q.replace("'", "''") for q in st.session_state.user_query_list]
                user_query_json = json.dumps(escaped_queries)
                insert_log_query = f'''
                    INSERT INTO LL_PROD_RAW_ZONE.PUBLIC.STREAMLIT_DATA_EDIT_UI_LOGS (USERNAME, TABLENAME, USER_QUERY, DATETIME) 
                    values ('{st.session_state.username}', '{selected_tablename}', '{user_query_json}', '{datetime.now()}');
                '''
                st.write(f"insert query log {insert_log_query}")
                st_execute_query_on_snowflake(insert_log_query)
                st.success("Table Appended")

                time.sleep(5)
                st.session_state.user_query_list = []
                added_df = st.session_state.selected_table_df_original[:1]
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Error APPENDING Edited table: {e}")

    st.session_state.selected_table_df = st.session_state.selected_table_df_original
    st.session_state.user_query_list = []

    c = datetime.now()
    print(c-a)
