import streamlit as st
import json


def load_users() -> dict[str, str]:
    with open("config.json", "r") as file:
        config = json.load(file)
    return config.get("users", {})


# Login widget
def login(users):
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in users and users[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")


# Main app
def main():
    st.title("Welcome to the App")
    st.write(f"Hello, {st.session_state['username']}! 🎉")


# App entry point
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    users = load_users()
    login(users)
else:
    main()
