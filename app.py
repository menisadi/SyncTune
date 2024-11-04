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

st.title("My Music Dashboard")

# add a subtitle with total play count
total_count = network.get_user(USERNAME).get_playcount()
st.subheader(f"Total Play Count: {total_count}")

# Sidebar options for time periods
chosen_time_period = st.sidebar.selectbox(
    "Select Time Period", ["Weekly", "Monthly", "Yearly", "Overall"], index=3
)
time_period = period_dict.get(chosen_time_period)
st.header(f"{chosen_time_period} data")

st.sidebar.markdown("---")
st.sidebar.markdown("Made by [meni](https://github.com/menisadi)")

# Display current playing track
now_playing = network.get_user(USERNAME).get_now_playing()
if now_playing:
    st.subheader("Now Playing")
    st.write(f"🎵 {now_playing.artist} - {now_playing.title}")
else:
    st.subheader("Now Playing")
    st.write("No song is currently playing.")


def get_top_artists(period, limit=3):
    top_artists = network.get_user(USERNAME).get_top_artists(period=period, limit=limit)
    top_artists_names = [(artist.item.name, artist.weight) for artist in top_artists]

    return top_artists_names


def get_top_genres(top_artists, limit=3, prune_tag_list=3):
    # initiate a list to store the top genres
    tags = dict()
    for artist, artist_weight in top_artists:
        top_genres = network.get_artist(artist).get_top_tags(limit=prune_tag_list)
        for genre in top_genres:
            if genre.item.name in tags:
                tags[genre.item.name] += int(genre.weight) * int(artist_weight)
            else:
                tags[genre.item.name] = int(genre.weight) * int(artist_weight)

    # return the top genres in descending order of weight
    return sorted(tags.items(), key=lambda x: x[1], reverse=True)[:limit]


# Display top 3 artists
st.subheader("Top 3 Artists")
top_artists = get_top_artists(time_period, limit=3)
for artist, weight in top_artists:
    st.write(f"{artist} - {weight}")

# Display top 3 genres
st.subheader("Top 3 Genres")
for genre, weight in get_top_genres(top_artists, limit=3, prune_tag_list=3):
    st.write(f"{genre} - {weight}")
