import numpy as np
from typing import List, Tuple
from wordcloud import WordCloud, get_single_color_func
import matplotlib.pyplot as plt
from collections import Counter
import pylast
import streamlit as st
import json


def func(genre_file):
    genres_list = [l.split(": ")[1][:-1] for l in genre_file]


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

# convert the time period to the same format as pylast
period_dict = {
    "Overall": pylast.PERIOD_OVERALL,
    "Weekly": pylast.PERIOD_7DAYS,
    "Monthly": pylast.PERIOD_1MONTH,
    "Yearly": pylast.PERIOD_12MONTHS,
    None: pylast.PERIOD_OVERALL,
}

title = "TuneSync"
icon = "🎧"
st.set_page_config(
    page_title=title,
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("TuneSync")

# total_count = network.get_user(USERNAME).get_playcount()
# st.write(f"Total Play Count: {total_count}")

st.sidebar.markdown("Made by [Meni](https://github.com/menisadi)")
st.sidebar.markdown("Powered by [Last.fm](https://www.last.fm/)")

# Display current playing track
now_playing = network.get_user(USERNAME).get_now_playing()
if now_playing:
    st.header("Now Playing")
    track = network.get_track(now_playing.artist, now_playing.title)
    album = now_playing.get_album().get_name()
    album_image_url = now_playing.get_cover_image()

    col1, col2, col3 = st.columns([2, 1, 6])

    with col1:
        if album_image_url:
            st.image(
                album_image_url,
                caption="",
            )
        else:
            st.write("")  # Fallback in case there is no image

    with col2:
        st.write("")
        st.markdown("**Artist**")
        st.markdown("**Album**")
        st.markdown("**Track**")
    with col3:
        st.write("")
        st.markdown(now_playing.artist)
        st.markdown(album)
        st.markdown(now_playing.title)
else:
    st.markdown("*No track currently playing*")

st.header("Summary")
col1, col2 = st.columns([1, 2])

with col1:
    chosen_time_period = st.selectbox(
        "Select Time Period",
        ["Weekly", "Monthly", "Yearly", "Overall"],
        index=0,
    )

time_period = period_dict.get(chosen_time_period)


def display_wordcloud(tags_list: List[Tuple[str, float]]):
    tags_dict = dict(tags_list)
    wordcloud = WordCloud(
        width=230,
        height=230,
        background_color="#282a36",
        contour_color="#282a36",
        contour_width=3,
    ).generate_from_frequencies(tags_dict)
    wordcloud.recolor(color_func=get_single_color_func("#f8f8f2"))

    st.image(wordcloud.to_array())


def get_top_artists(period, limit=3):
    top_artists = network.get_user(USERNAME).get_top_artists(period=period, limit=limit)
    top_artists_names = [
        (artist.item.name, int(artist.weight)) for artist in top_artists
    ]

    return top_artists_names


def normalize_weights(tags: List[Tuple[str, int]]) -> List[Tuple[str, float]]:
    max_weight = max([w for _, w in tags])
    return [(t, w / max_weight) for t, w in tags]


def get_top_tags(
    top_artists: List[Tuple[str, int]], limit: int = 0, prune_tag_list: int = 0
) -> List[Tuple[str, float]]:
    tags = dict()
    for artist, artist_weight in top_artists:
        top_tags = network.get_artist(artist).get_top_tags(limit=prune_tag_list)
        for one_tag in top_tags:
            # exclude the "seen live", as it is not interesting
            if one_tag.item.name == "seen live":
                continue
            if one_tag.item.name in tags:
                tags[one_tag.item.name] += int(one_tag.weight) * artist_weight
            else:
                tags[one_tag.item.name] = int(one_tag.weight) * artist_weight

    normalized_tags = normalize_weights(list(tags.items()))
    if limit == 0:
        return normalized_tags
    else:
        # return the top tags in descending order of weight
        limited_tags = sorted(normalized_tags, key=lambda x: x[1], reverse=True)[:limit]
        return limited_tags


# Display top 3 artists
st.subheader("Top 3 Artists")
top_artists = get_top_artists(time_period, limit=3)
max_weight = max([w for _, w in top_artists])

for artist, weight in top_artists:
    col1, col2, col3 = st.columns([4, 1, 7])
    with col1:
        st.write(f"**{artist}**")
    with col2:
        st.write(f"**{weight}**")
    with col3:
        st.progress(int(weight / max_weight * 100))

# Tags wordcloud
# TODO: add mask to the cloud
more_top_artists = get_top_artists(time_period, limit=20)
all_tags = get_top_tags(more_top_artists, limit=0, prune_tag_list=3)
st.subheader("Top Tags")
display_wordcloud(all_tags)
