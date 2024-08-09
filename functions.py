import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session

def st_read_from_snowflake(query):
    session = get_active_session()
    df = pd.DataFrame(session.sql(query).collect())
    return df

def st_execute_query_on_snowflake(query):
    session = get_active_session()
    try:
        session.sql(query).collect()
    except Exception as e:
        st.error(f"An error occurred during the requested operation: \n{e}")

def generate_update_query(row, table_name, primary_key, dataset):
    pk_value = row[primary_key]
    set_clauses = []

    dtype_mappings = {
        'object': 'VARCHAR(16777216)',
        'int64': 'NUMBER(38,0)',
        'float64': 'NUMBER(38,4)',
        'datetime64[ns]': 'TIMESTAMP_LTZ(9)',
        'bool': 'BOOLEAN'
    }

    for col in dataset.columns:
        if col == primary_key:
            continue
        col_data_type = dataset[col].dtype
        sql_type = dtype_mappings.get(str(col_data_type), 'VARCHAR(16777216)')
        value = row[col]
        if pd.isnull(value):
            set_value = 'NULL'
        elif col_data_type == 'bool':
            set_value = str(value).lower()
        elif col_data_type == 'datetime64[ns]':
            set_value = f"'{value}'"
        elif col_data_type == 'object':
            set_value = f"'{value}'"
        else:
            set_value = f"{value}"
        if set_value == 'NULL':
            set_clause = f"{col} = {set_value}"
        else:
            set_clause = f"{col} = {set_value}::{sql_type}"
        set_clauses.append(set_clause)

    set_clause = ", ".join(set_clauses)
    update_query = f'''
    UPDATE {table_name} SET {set_clause} WHERE {primary_key} = {pk_value};
    '''
    return update_query

def generate_insert_query(row, table_name, dataset):
    columns = []
    values = []

    dtype_mappings = {
        'object': 'VARCHAR(16777216)',
        'int64': 'NUMBER(38,0)',
        'float64': 'NUMBER(38,4)',
        'datetime64[ns]': 'TIMESTAMP_LTZ(9)',
        'bool': 'BOOLEAN'
    }

    for col in dataset.columns:
        col_data_type = dataset[col].dtype
        sql_type = dtype_mappings.get(str(col_data_type), 'VARCHAR(16777216)')
        value = row[col]
        if pd.isnull(value):
            value = 'NULL'
        elif col_data_type == 'bool':
            value = str(value).lower()
        elif col_data_type == 'datetime64[ns]':
            value = f"'{value}'"
        elif col_data_type == 'object':
            value = f"'{value}'"
        else:
            value = f"{value}"
        columns.append(f'{col}')
        if value == 'NULL':
            values.append(f"{value}")
        else:
            values.append(f"{value}::{sql_type}")

    columns_str = ", ".join(columns)
    values_str = ", ".join(values)
    insert_query = f'''
    INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});
    '''
    return insert_query

def apply_filters(df, filters):
    filtered_df = df.copy()
    for column, value in filters.items():
        filtered_df = filtered_df[filtered_df[column] == value]
    return filtered_df
