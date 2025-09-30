import streamlit as st
import DatabaseManager

# Ensure user is logged in as admin
if "role" not in st.session_state or st.session_state.role != "admin":
    st.warning("⚠️ Access denied. Only admins can view the Management Page.")
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

# Set page config
st.set_page_config(page_title="Management Page", page_icon=":wrench:")

# Show logout button and admin info in the navigation bar
show_admin_info()
show_logout_button()

# Management page content
st.title('Management Page')
st.write("---")

with st.expander('Get Price to Pay at Check Out'):
    cid = int(st.number_input('Enter Customer ID', step=1))
    if st.button('Submit'):
        totalamt = DatabaseManager.getFinalAmount(cid)
        st.info(f'Amount to be paid is {totalamt}')
        DatabaseManager.addBookingDetails(cid, totalamt)
        st.success('Successfully Updated')

with st.expander('Add Room Service Ticket'):
    itemid = int(st.number_input('Enter Item ID', step=1))
    quantity = int(st.number_input('Enter Quantity', step=1))
    rscid = int(st.number_input('Enter CustomerID', step=1))
    if st.button('Add Ticket'):
        DatabaseManager.addRoomService(itemid, quantity, rscid)
        st.success('Successfully Updated')

with st.expander('List of Items'):
    df = DatabaseManager.getAllItems()
    st.table(data=df)

with st.expander('List of Employees'):
    df = DatabaseManager.getAllEmployees()
    st.table(data=df)

with st.expander('List of Employee Roles'):
    df = DatabaseManager.getAllRoles()
    st.table(data=df)

with st.expander('List of Rooms'):
    df = DatabaseManager.getAllRooms()
    st.table(data=df)

with st.expander('List of Room Types'):
    df = DatabaseManager.getAllRoomTypes()
    st.table(data=df)

with st.expander('List of Bookings'):
    df = DatabaseManager.getAllBookingDetails()
    st.table(data=df)

with st.expander('List of Customers'):
    df = DatabaseManager.getAllCustomerDetails()
    st.table(data=df)

with st.expander('List of Orders'):
    df = DatabaseManager.getAllOrders()
    st.table(data=df)