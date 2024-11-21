from collections import Counter
import pylast
import streamlit as st
import json

with open("tokens.json", "r") as file:
    tokens = json.load(file)

API_KEY = tokens.get("last_api_key")
API_SECRET = tokens.get("last_secret")
USERNAME = tokens.get("last_username")
PASSWORD_HASH = pylast.md5(tokens.get("last_password"))

network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH,
)

second_user_name = "GlowingGroove"
other_user = network.get_user(second_user_name)
now_playing = other_user.get_now_playing()
top_artists = other_user.get_top_artists(period=pylast.PERIOD_7DAYS, limit=3)

print(now_playing)
print(top_artists)
