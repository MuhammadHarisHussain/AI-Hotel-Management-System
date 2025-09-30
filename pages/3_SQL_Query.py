import streamlit as st
import mysql.connector
import pandas as pd

st.set_page_config(page_title="SQL Query Executor", page_icon="🧮")

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port='3306',
        user="root",
        password="1234rayyan",
        database="hoteldatabase"
    )

# Role check from session
if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("⚠️ Access denied. Only admins can view SQL queries Page.")
    st.stop()

# Add a logout button that is visible in the navigation bar
def show_logout_button():
    if st.session_state.logged_in:
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = None
            st.session_state.page = None
            st.experimental_rerun()

# Show admin info if logged in as admin
def show_admin_info():
    if st.session_state.role == "admin":
        st.sidebar.info(f"You are logged in as Admin ({st.session_state.username})")

# Show logout button and admin info in the navigation bar
show_admin_info()
show_logout_button()

# SQL Query interface
st.title("SQL Query Executor")
query = st.text_area("Enter your SQL Query below", height=100, placeholder="e.g. SELECT * FROM items;")

if st.button("Run Query"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            cols = [i[0] for i in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df)
        else:
            conn.commit()
            st.success("Query executed successfully.")

    except mysql.connector.Error as e:
        st.error(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
