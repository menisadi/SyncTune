import streamlit as st
import streamlit_authenticator as stauth

# Set up configuration for authentication
# Replace these hashed passwords with your own securely generated ones
hashed_passwords = stauth.Hasher(["password1", "password2"]).generate()

# User credentials
credentials = {
    "usernames": {
        "user1": {"name": "User One", "password": hashed_passwords[0]},
        "user2": {"name": "User Two", "password": hashed_passwords[1]},
    }
}

# Initialize the authenticator
authenticator = stauth.Authenticate(
    credentials, "my_app_cookie", "my_app_key", cookie_expiry_days=30
)

# Display the login widget
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    # If authentication is successful
    st.write(f"Welcome, {name}!")
elif authentication_status is False:
    # If authentication fails
    st.error("Username or password is incorrect")
elif authentication_status is None:
    # If no authentication is attempted
    st.info("Please enter your username and password")

# Include a logout button
authenticator.logout("Logout", "sidebar")
