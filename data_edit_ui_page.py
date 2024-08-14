import pandas as pd
import streamlit as st
from functions import st_read_from_snowflake, st_execute_query_on_snowflake, generate_update_query, generate_insert_query, apply_filters

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

    st.sidebar.write("Please select the table to edit from below dropdown")
    selected_tablename = st.sidebar.selectbox(
        label="table choice", options=st.session_state.allowed_tables_list, label_visibility="hidden"
    )
    st.write(f"Your selected table is: {selected_tablename}")

    if selected_tablename != st.session_state.selected_tablename:
        st.session_state.filters = {}
        st.session_state.selected_tablename = selected_tablename
        st.session_state.selected_table_df = st_read_from_snowflake(f"SELECT * FROM {st.session_state.selected_tablename}")
    st.session_state.selected_table_df_original = st.session_state.selected_table_df

    if 'ID' in st.session_state.selected_table_df_original.columns:
        st.session_state.master_pk_list = st.session_state.selected_table_df_original['ID'].unique()
    else:
        st.error("The column 'ID' does not exist in the selected table.")

    with st.sidebar.expander("Add Filters"):
        column_options = st.session_state.selected_table_df.columns.difference(list(st.session_state.filters.keys()))
        cols = st.columns([4, 3])
        with cols[0]:
            column = st.selectbox("Select Column", options=column_options)
        with cols[1]:
            value = st.text_input("Filter Value", key=column) if st.session_state.selected_table_df[column].dtype == 'object' else \
                    st.number_input("Filter Value", key=column, step=1)
        cols = st.columns([4, 5])
        with cols[0]:
            if st.button("Apply Filter"):
                st.session_state.filters[column] = value
        with cols[1]:
            if st.button("Remove Filter"):
                st.session_state.filters = {}
                st.session_state.selected_table_df = st.session_state.selected_table_df_original
                st.session_state.right_pane_table_view = True

    st.session_state.selected_table_df = apply_filters(st.session_state.selected_table_df, st.session_state.filters) if st.session_state.filters else st.session_state.selected_table_df

    if st.session_state.right_pane_table_view:
        with st.form("data_editor_form"):
            st.caption("Change below to UPDATE DATA in the selected table")
            edited = st.experimental_data_editor(
                st.session_state.selected_table_df.reset_index(drop=True), use_container_width=True, num_rows="fixed"
            )
            submit_button = st.form_submit_button("Submit Changes")
            st.session_state.submit_button = submit_button

    if st.session_state.submit_button:
        try:
            for index, row in edited.iterrows():
                user_query = generate_update_query(row, selected_tablename, 'ID', edited)
                if user_query not in st.session_state.user_query_list:
                    st.session_state.user_query_list.append(user_query.strip())
                    st_execute_query_on_snowflake(user_query)
            st.success("Table updated")
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
        try:
            for index, row in added.iterrows():
                user_query = generate_insert_query(row, selected_tablename, added)
                if user_query not in st.session_state.user_query_list:
                    st.session_state.user_query_list.append(user_query.strip())
                    st_execute_query_on_snowflake(user_query)
            st.success("Table Appended")
            st.session_state.user_query_list = []
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error APPENDING Edited table: {e}")

    st.session_state.selected_table_df = st.session_state.selected_table_df_original
