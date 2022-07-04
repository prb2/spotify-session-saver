#!/usr/bin/python3

import sys
import spotipy
import spotipy.util as util
import time
from datetime import datetime as dt



if len(sys.argv) != 4:
    print("usage:\n\t./spotifysess.py <username> <client_id> <client_secret>")
    sys.exit()


# capture the session start time right away
session_start = time.time()
dt_start = dt.fromtimestamp(session_start)
print("> starting session at: {}".format(dt_start))


# authorize and create the spotify client
username = sys.argv[1]
client_id = sys.argv[2]
client_secret = sys.argv[3]
# print(username, client_id, client_secret)
scope = 'user-read-recently-played playlist-modify-private'
token = util.prompt_for_user_token(
    username,
    scope,
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='https://www.example.com'
)
if not token:
    print("> couldn't get token for", username)
    sys.exit()
sp = spotipy.Spotify(auth=token)



print("> press enter or type a name and press enter to end session...")
sess_name = input()

millis = int(session_start*1000) # convert s to ms, then truncate float to int

# get tracks played since session start time
r = sp.current_user_recently_played(after=millis) # at most limit is 50

tracks = []
max_col_width = 0
for it in r["items"]:
    pa = it["played_at"]
    a = it["track"]["artists"][0]["name"]
    t = it["track"]["name"]
    u = it["track"]["uri"]
    tracks.append((pa, a, t, u))
    if len(a) > max_col_width:
        max_col_width = len(a)


if not tracks:
    print("> no tracks found in session since {}".format(dt_start))
    sys.exit()

# we want earliest played tracks at the beginning
tracks.reverse()

first_played_at = dt.fromisoformat(tracks[0][0][:-1]) # drop the 'Z' at the end before passing param

# pretty print the tracks included in the session
print()
fmt_str = "{:<27}{:<" + str(max_col_width + 2) + "}{:<}"
print(fmt_str.format("Played At", "Artist", "Track"))
print(fmt_str.format("---------", "------", "-----"))
for pa, a, t, _ in tracks: # list of (played_at, artist, track) tuples
    print(fmt_str.format(pa, a, t))
print()
# print("first played at: ", first_played_at)

if sess_name == "":
    print("> no session name provided, using default")
    sess_name = first_played_at.strftime("%B %e, %Y")

print("> saving {} session tracks to new playlist: '{}'".format(len(tracks), sess_name))

playlist = sp.user_playlist_create(
    user=username,
    name=sess_name,
    public=False,
    collaborative=False,
    description=""
)

items = [t[3] for t in tracks]
add_tracks = sp.playlist_add_items(playlist["id"], items)
