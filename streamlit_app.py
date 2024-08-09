import streamlit as st
import login_page
import data_edit_ui_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Edit UI"])

    if page == "Login":
        login_page.login()
    elif page == "Edit UI":
        data_edit_ui_page.edit_ui()

if __name__ == "__main__":
    main()
