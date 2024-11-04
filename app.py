from typing import List, Tuple
from wordcloud import WordCloud
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

# convert the time period to the same format as pylast
period_dict = {
    "Overall": pylast.PERIOD_OVERALL,
    "Weekly": pylast.PERIOD_7DAYS,
    "Monthly": pylast.PERIOD_1MONTH,
    "Yearly": pylast.PERIOD_12MONTHS,
    None: pylast.PERIOD_OVERALL,
}

title = "TuneSync"
# Use a music icon
icon = "🎧"
st.set_page_config(
    page_title=title,
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("TuneSync")

total_count = network.get_user(USERNAME).get_playcount()
st.write(f"Total Play Count: {total_count}")

# Sidebar options for time periods
chosen_time_period = st.sidebar.selectbox(
    "Select Time Period", ["Weekly", "Monthly", "Yearly", "Overall"], index=0
)
time_period = period_dict.get(chosen_time_period)
st.header(f"{chosen_time_period} data")

st.sidebar.markdown("---")
st.sidebar.markdown("Made by [Meni](https://github.com/menisadi)")
st.sidebar.markdown("Powered by [Last.fm](https://www.last.fm/)")

# Display current playing track
now_playing = network.get_user(USERNAME).get_now_playing()
if now_playing:
    track = network.get_track(now_playing.artist, now_playing.title)
    album = now_playing.get_album().get_name()
    album_image_url = now_playing.get_cover_image()

    col1, col2 = st.columns([1, 3])  # Adjust the proportions as needed

    with col1:
        if album_image_url:
            st.image(
                album_image_url, caption="", width=100
            )  # Adjust width for smaller image
        else:
            st.write("")  # Fallback in case there is no image

    with col2:
        st.markdown(f"**Artist**: {now_playing.artist}")
        st.markdown(f"**Album**: {album}")
        st.markdown(f"**Title**: {now_playing.title}")


def display_wordcloud(genres: List[Tuple[str, float]]):
    genres_dict = dict(genres)
    wordcloud = WordCloud(
        width=400,
        height=400,
        background_color="#282a36",
        contour_color="#bd93f9",
        contour_width=3,
    ).generate_from_frequencies(genres_dict)

    # plt.figure(figsize=(3, 3))
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")
    # st.pyplot(plt.gcf())
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


def get_top_genres(
    top_artists: List[Tuple[str, int]], limit: int = 0, prune_tag_list: int = 0
) -> List[Tuple[str, float]]:
    tags = dict()
    for artist, artist_weight in top_artists:
        top_genres = network.get_artist(artist).get_top_tags(limit=prune_tag_list)
        for genre in top_genres:
            if genre.item.name in tags:
                tags[genre.item.name] += int(genre.weight) * artist_weight
            else:
                tags[genre.item.name] = int(genre.weight) * artist_weight

    normalized_tags = normalize_weights(list(tags.items()))
    if limit == 0:
        return normalized_tags
    else:
        # return the top genres in descending order of weight
        limited_tags = sorted(normalized_tags, key=lambda x: x[1], reverse=True)[:limit]
        return limited_tags


# Display top 3 artists
st.subheader("Top 3 Artists")
top_artists = get_top_artists(time_period, limit=3)
for artist, weight in top_artists:
    st.write(f"**{artist}**")
    st.progress(int(weight / max([w for _, w in top_artists]) * 100))

# Tags wordcloud
more_top_artists = get_top_artists(time_period, limit=20)
all_tags = get_top_genres(more_top_artists, limit=0, prune_tag_list=3)
st.subheader("Word Cloud of Top Tags")
display_wordcloud(all_tags)
