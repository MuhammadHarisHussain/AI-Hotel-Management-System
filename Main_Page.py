import streamlit as st
import mysql.connector
import datetime
import DatabaseManager
from PIL import Image

# --- Styling ---
st.markdown("""
    <style>
        .stButton > button {
            background-color: #007BFF;
            color: white;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        .stTextInput > div > input,
        .stDateInput > div > input,
        .stNumberInput > div > input {
            border-radius: 6px;
            padding: 10px;
        }
        [data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #dc3545 !important;
            color: white !important;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 8px;
            transition: background-color 0.3s ease !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: #a71d2a !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- DB Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port='3306',
        user="root",
        password="1234rayyan",
        database="hoteldatabase"
    )

# --- User Authentication ---
def register_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

# --- Login/Register ---
def login_register():
    st.title("🔐 Login / Register")

    menu = ["Login", "Register"]
    choice = st.selectbox("Select Action", menu)

    if choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type='password')
        role = st.selectbox("Select Role", ["customer", "admin"])
        if st.button("Register"):
            if register_user(new_user, new_pass, role):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists.")

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            role = login_user(username, password)
            if role:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success(f"Logged in as {username} ({role})")
                st.rerun()
            else:
                st.error("Invalid credentials.")

# --- Booking Page ---
def main_page():
    st.title("🏨 Four Seasons Hotel")
    st.markdown("Enjoy luxury rooms, spa, gym, and gourmet dining at your fingertips.")
    st.write("---")

    with st.form("booking_form"):
        st.header("📅 Booking Details")
        col1, col2 = st.columns(2)
        checkin = col1.date_input("Check-in Date")
        checkout = col2.date_input("Check-out Date")

        cname = st.text_input("Full Name", placeholder="e.g., Muhammad Ahmed")
        cage = st.number_input("Age", step=1, min_value=0)
        cnic = st.text_input("SSN / CNIC", placeholder="e.g., 1234567890123")
        phone = st.text_input("Phone Number (10 digits)", placeholder="e.g., 300123456")
        caddress = st.text_area("Address", placeholder="e.g., House #123, Street 4, City, Country")

        st.write("---")
        st.header("🛏️ Room Selection")

        for i in range(1, 6):
            with st.expander(f"Room Option {i}"):
                row = DatabaseManager.getRoomType(i)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f'Hotel-Management-using-SQL-main\Hotel-Management-using-SQL-main\Images\Room{i}.jpg', use_container_width=True)
                with col2:
                    st.markdown(f"**Room Number**: {row[0]}")
                    st.markdown(f"**Beds**: {row[1]} |  {row[2]}")
                    st.markdown(f"**Price**: ${row[3]}")
                st.markdown(f"**Description**: {row[4]}")

        roomtypeid = st.number_input("Enter Room Number to Book (1-5)", step=1,min_value=0, max_value=5)

        # Live Price Estimate
        if checkin and checkout and 1 <= roomtypeid <= 5 and checkin < checkout:
            try:
                totalprice = DatabaseManager.selectRoom(roomtypeid, checkin, checkout)
                st.info(f"Estimated Total Price: ${totalprice}")
            except:
                st.warning("Could not estimate price. Check room number.")

        submitted = st.form_submit_button("Submit Booking")

        if submitted:
            flag = 0
            if checkin >= checkout:
                st.error("Check-out cannot be before check-in")
                flag = 1
            if cage < 18:
                st.error("You must be 18+ to book")
                flag = 1
            if not cnic.isdigit():
                st.error("CNIC must be numeric only")
                flag = 1
            if len(phone) != 10 or not phone.isdigit():
                st.error("Phone must be 10 digits")
                flag = 1
            if roomtypeid not in range(1, 6):
                st.error("Invalid Room Number")
                flag = 1

            if flag == 0:
                totalprice = DatabaseManager.selectRoom(roomtypeid, checkin, checkout)
                cid = DatabaseManager.addCustDetails(
                    int(cnic), cname, int(cage), int(phone),
                    caddress, totalprice, checkin, checkout
                )
                show_confirmation(cid, checkin, checkout)

# --- Booking Confirmation ---
def show_confirmation(cid, checkin, checkout):
    st.success("🎉 Booking Confirmed!")
    row = DatabaseManager.getCustDetails(cid)
    st.write(f"Customer ID: {cid}")
    st.write(f"Name: {row[2]}")
    st.write(f"CNIC: {row[1]}")
    st.write(f"Phone: {row[4]}")
    st.write(f"Address: {row[5]}")
    st.write(f"Check-in: {checkin} | Check-out: {checkout}")
    st.write(f"Total Price: ${row[6]}")
    st.info("Please pay your bill at checkout. Thank you!")

# --- Main ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = ""

if not st.session_state.logged_in:
    login_register()
else:
    st.sidebar.success(f"Welcome, {st.session_state.username}")
    if st.session_state.role == "admin":
        st.sidebar.info("You are logged in as Admin.")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = None
        st.rerun()
        
    main_page()
