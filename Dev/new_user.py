import numpy as np
from typing import List, Tuple
from wordcloud import WordCloud, get_single_color_func
import matplotlib.pyplot as plt
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

SECOND_USER = "GlowingGroove"
user2 = network.get_user(SECOND_USER)
list_of_artists = [a.item.get_name() for a in user2.get_top_artists()]
print("\nTop artist:")
print(list_of_artists[0])

list_of_songs = [s.item.get_title() for s in user2.get_top_tracks()]
print("\nTop song:")
print(list_of_songs[0])

now_playing = user2.get_now_playing()
if now_playing:
    print("\nNow playing:")
    print(now_playing)
else:
    print("No song is currently playing")
