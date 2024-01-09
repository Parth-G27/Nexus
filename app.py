import streamlit as st
from pymongo import MongoClient
from datetime import datetime

from urllib.parse import quote_plus
from pymongo import MongoClient

# Replace 'username' and 'password' with your actual username and password
username = 'jeswin'
password = 'jeswin'

# Escape the username and password
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

uri = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.ukudqwu.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['logistics_app']
users_collection = db['users']
requests_collection = db['requests']


def create_user(username, password, user_type):
    user_data = {
        'username': username,
        'password': password,
        'user_type': user_type,
    }
    users_collection.insert_one(user_data)


def get_user(username):
    return users_collection.find_one({'username': username})


def create_request(sender, receiver, item_name, quantity, quoted_price):
    request_data = {
        'sender': sender,
        'receiver': receiver,
        'item_name': item_name,
        'quantity': quantity,
        'quoted_price': quoted_price,
        'status': 'INITIATED',
        'timestamp': datetime.now(),
        'communication': [],
    }
    requests_collection.insert_one(request_data)


def get_requests_to_user(username):
    return requests_collection.find({'receiver': username})


def get_requests_by_user(username):
    return requests_collection.find({'sender': username})


def update_request_status(request_id, status):
    requests_collection.update_one(
        {'_id': request_id},
        {'$set': {'status': status}}
    )


def add_communication(request_id, user_type, message):
    communication_data = {
        'user_type': user_type,
        'message': message,
        'timestamp': datetime.now(),
    }
    requests_collection.update_one(
        {'_id': request_id},
        {'$push': {'communication': communication_data}}
    )


# Streamlit UI
def main():
    st.set_page_config(
        page_title="Nexus App",
        page_icon="📦",
        layout="wide"
    )

    # Custom CSS for enhanced styling
    st.markdown("""
        <style>
            .st-eb {
                background-color: #f0f0f0;
                padding: 10px;
                margin: 10px 0;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for login
    with st.sidebar:
        st.markdown(
            "<h1 style='text-align: center; color: #444;'>Logistics App</h1>", unsafe_allow_html=True)
        st.header("Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        login_button = st.button("Login")

    # Main content
    if login_button:
        user = get_user(username)
        if user and user['password'] == password:
            st.success("Login successful!")

            st.header("User Profile")
            st.write(f"Welcome, {user['username']}!")

            # Display user profile information based on the logged-in user
            if user['user_type'] == 'admin':
                st.header("Admin Dashboard")

                # Add New User section
                st.subheader("Add New User")
                new_username = st.text_input("New Username:")
                new_password = st.text_input("New Password:", type="password")
                user_types = ['admin', 'normal']
                new_user_type = st.selectbox("User Type:", user_types)
                if st.button("Add User"):
                    create_user(new_username, new_password, new_user_type)
                    st.success(f"User '{new_username}' added successfully!")

            elif user['user_type'] == 'normal':
                st.header("Employee Dashboard")

                # Requests Sent to You
                st.subheader("Requests Sent to You")
                requests_to_user = get_requests_to_user(username)
                for request in requests_to_user:
                    st.markdown(
                        f"<div class='st-eb'>Request ID: {request['_id']}, Item: {request['item_name']}, Quantity: {request['quantity']}, Quoted Price: {request['quoted_price']}</div>", unsafe_allow_html=True)

                # Requests Sent by You
                st.subheader("Requests Sent by You")
                requests_by_user = get_requests_by_user(username)
                for request in requests_by_user:
                    st.markdown(
                        f"<div class='st-eb'>Request ID: {request['_id']}, Item: {request['item_name']}, Quantity: {request['quantity']}, Quoted Price: {request['quoted_price']}</div>", unsafe_allow_html=True)
        else:
            st.error("Invalid credentials. Please try again.")
        # Goods Request section (common for all users)
        st.header("Goods Request")

        item_name = st.text_input("Item Name:")
        quantity = st.number_input("Quantity:", min_value=1, value=1)
        quoted_price = st.number_input("Quoted Price:")
        recipient_employee = st.selectbox("Select Recipient Employee:", [
            'Employee1', 'Employee2'])
        if st.button("Send Request"):
            # Logic to create a new request
            create_request(sender=username, receiver=recipient_employee,
                           item_name=item_name, quantity=quantity, quoted_price=quoted_price)
            st.success("Request sent successfully!")

        if st.button("Accept Request"):
            # Logic to show pending requests and accept them
            pending_requests = get_requests_to_user(username)
            if pending_requests.count() > 0:
                selected_request = st.radio("Select Request to Accept:", [
                                            f"Request ID: {request['_id']}, Item: {request.get('item_name', 'N/A')}" for request in pending_requests])
                if st.button("Accept Selected Request"):
                    # Extracting the request ID from the selected string
                    request_id = selected_request.split(" ")[3]
                    update_request_status(request_id, 'ACCEPTED')
                    st.success("Request accepted successfully!")
                else:
                    st.warning("Please select a request to accept.")
            else:
                st.info("No pending requests to accept.")

        if st.button("Complete Request"):
            # Logic to show ongoing requests and mark them as completed
            ongoing_requests = get_requests_by_user(username)
            if ongoing_requests.count() > 0:
                selected_request = st.radio("Select Request to Complete:", [
                                            f"Request ID: {request['_id']}, Item: {request.get('item_name', 'N/A')}" for request in ongoing_requests])
                if st.button("Complete Selected Request"):
                    # Extracting the request ID from the selected string
                    request_id = selected_request.split(" ")[3]
                    update_request_status(request_id, 'COMPLETED')
                    st.success("Request completed successfully!")
                else:
                    st.warning("Please select a request to complete.")
            else:
                st.info("No ongoing requests to complete.")

        # Communication updates
        st.header("Communication Updates")

        communication_message = st.text_input("Enter message:")
        if st.button("Send Message"):
            # Logic to add communication message to a request
            ongoing_requests = get_requests_by_user(username)
            if ongoing_requests.count() > 0:
                selected_request = st.radio("Select Request:", [
                                            f"Request ID: {request['_id']}, Item: {request.get('item_name', 'N/A')}" for request in ongoing_requests])
                if st.button("Send Message to Selected Request"):
                    # Extracting the request ID from the selected string
                    request_id = selected_request.split(" ")[3]
                    add_communication(
                        request_id, user_type='Sender', message=communication_message)
                    st.success("Message sent successfully!")
                else:
                    st.warning("Please select a request to send a message.")
            else:
                st.info("No ongoing requests to send a message.")

        # Delivery history and goods track
        st.header("Delivery History and Goods Track")
        # Logic to display delivery history and track goods


if __name__ == '__main__':
    main()
