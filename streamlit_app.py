# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()

# Write directly to the app
st.title("Intro of POC ")

# query = "SELECT * FROM LL_PROD_RAW_ZONE.PUBLIC.EXTRA_TABLES;"
# df = pd.DataFrame(session.sql(query).collect())
# st.write(df)

st.write("Hello World I am Rajat Tiwari from India....Developing a automation of streamlit deployment")


# dept_tables = pd.read_csv('table_dept_mapping.csv')
# st.write(dept_tables)

