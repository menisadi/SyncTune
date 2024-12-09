import time
from typing import List, Tuple
from wordcloud import WordCloud, get_single_color_func
import pylast
import streamlit as st
import streamlit_authenticator as stauth
import json


def func(genre_file: list[str]):
    genres_list = [line.split(": ")[1][:-1] for line in genre_file]
    return genres_list


def display_wordcloud(tags_list: list[tuple[str, float]]):
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


def get_top_artists(user_name, period, limit=3):
    top_artists = network.get_user(user_name).get_top_artists(
        period=period, limit=limit
    )
    top_artists_names = [
        (artist.item.name, int(artist.weight)) for artist in top_artists
    ]

    return top_artists_names


def get_top_songs(user_name, period, limit=3):
    top_songs_items = network.get_user(user_name).get_top_tracks(
        period=period, limit=limit
    )
    top_songs = [
        (song.item.title, song.item.artist, int(song.weight))
        for song in top_songs_items
    ]

    return top_songs


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


def login(users: dict[str, dict[str, str]]):
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in users.keys() and users[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password")


def main():
    st.title("SyncTune")

    # total_count = network.get_user(USERNAME).get_playcount()
    # st.write(f"Total Play Count: {total_count}")

    # Sidebar
    st.sidebar.title("Settings")

    # import user_names from json

    people_names = list(user_names.keys())
    chosen_person = st.sidebar.selectbox("User", people_names, index=0)
    chosen_user = user_names.get(chosen_person).get("username")

    chosen_time_period = st.sidebar.selectbox(
        "Time Period",
        ["Weekly", "Monthly", "Yearly", "Overall"],
        index=0,
    )
    chosen_top_k = st.sidebar.selectbox("How many to show?", [1, 3, 5, 10], index=1)

    # adding some space
    st.sidebar.markdown("---")

    st.sidebar.markdown("Made by [Meni](https://github.com/menisadi)")
    st.sidebar.markdown("Powered by [Last.fm](https://www.last.fm/)")

    # Display current playing track
    placeholder = st.empty()
    time_interval = 30 * 1
    time_loop = 200
    wordcloud_artist_limit = 20

    for seconds in range(time_loop):
        last_updated = time.time()
        should_we_update = False
        now_playing = network.get_user(chosen_user).get_now_playing()
        album_image_url = ""

        # for the extra part
        time_period = period_dict.get(chosen_time_period)
        top_artists = get_top_artists(chosen_user, time_period, limit=chosen_top_k)
        max_weight = max([w for _, w in top_artists])

        top_songs = get_top_songs(chosen_user, time_period, limit=chosen_top_k)
        songs_max_weight = max([w for _, _, w in top_songs])

        # for the tags wordcloud
        more_top_artists = get_top_artists(
            chosen_user, time_period, limit=wordcloud_artist_limit
        )

        with placeholder.container():
            st.markdown(f"### :gray[{chosen_person}]")
            if now_playing:
                st.header("Now Playing")
                track = network.get_track(now_playing.artist, now_playing.title)
                album = now_playing.get_album().get_name()
                album_image_url = now_playing.get_cover_image()

                col1, col2, col3 = st.columns([2, 1, 6])

                with col1:
                    if album_image_url != "":
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

            st.header(f"{chosen_time_period} Summary")

            # Display top 3 artists
            st.subheader(f"Top {chosen_top_k} Artists")

            for artist, weight in top_artists:
                col1, col2, col3 = st.columns([8, 1, 7])
                with col1:
                    st.write(f"**{artist}**")
                with col2:
                    st.write(f"**{weight}**")
                with col3:
                    st.progress(int(weight / max_weight * 100))

            # Display top songs
            st.subheader(f"Top {chosen_top_k} Songs")

            for song, artist, weight in top_songs:
                col1, col2, col3, col4 = st.columns([4, 4, 1, 7])
                with col1:
                    st.write(f"**{song}**")
                with col2:
                    st.write(f"**{artist}**")
                with col3:
                    st.write(f"**{weight}**")
                with col4:
                    st.progress(int(weight / songs_max_weight * 100))

            # Tags wordcloud
            all_tags = get_top_tags(more_top_artists, limit=0, prune_tag_list=3)
            st.subheader("Top Tags")
            display_wordcloud(all_tags)

            time.sleep(1)


with open("tokens.json", "r") as file:
    tokens = json.load(file)
with open("user_names.json", "r") as file:
    user_names = json.load(file)


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

title = "SyncTune"
icon = "🎵"
st.set_page_config(
    page_title=title,
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="auto",
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login(user_names)
else:
    main()
