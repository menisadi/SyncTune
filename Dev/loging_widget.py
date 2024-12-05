import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth

with open("../config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# initiate app
st.set_page_config(
    page_title="Office Jam",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

name, authentication_status, username = authenticator.login("Login", "main")
