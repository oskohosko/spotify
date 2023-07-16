"""

"""
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Loading our environment variables for us
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

print("Initialising request...\n")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

TECHNO = "spotify:Oskar_Hosken:TECHNO:playlist:1lGXPfqwCeSqZ0O5h4yps0"

PROVINCIAL = "spotify:Oskar_Hosken:PROVINCIAL:playlist:07o6kTp4nYhgcbIvVQpcEq"

TEST_ALBUM = "spotify:album:3fSff3bKd7pS7kLYiNakMV"

NPH = "500YRyClzP6Z7HtWd1BIje"

# To test before making a json file with all the info etc
playlist_uri = "spotify:Oskar_Hosken:PROVINCIAL:playlist:07o6kTp4nYhgcbIvVQpcEq"
like = True

username, playlist_id, playlist_name = playlist_uri.split(':')[1], playlist_uri.split(':')[4], playlist_uri.split(':')[2]
# Returning a dict of all the tracks

print("Retrieving playlist...\n")

sp_tracks = sp.user_playlist(username, playlist_id, 'tracks')

# Creating a dataframe with basic details on the track, e.g artist name, album name, track name
playlist_df = pd.DataFrame(columns=sp_tracks['tracks']['items'][0]['track'].keys())

print("Populating playlist DataFrame...\n")

# Adding the data into the df
for track in sp_tracks['tracks']['items']:
    playlist_df.loc[len(playlist_df)] = track['track']

# Getting all the ids for each song in the playlist
playlist_tracks = [song_id for song_id in playlist_df['id']]
# print(playlist_tracks)

track_features = sp.audio_features(playlist_tracks)

# print(track_features[0].keys())

features_df = pd.DataFrame(columns=track_features[0].keys(), data=track_features)

features_df = features_df.drop(columns=['type','uri','track_href','analysis_url','duration_ms','time_signature'])

features_df.to_csv('features.csv')

# Cleaning up columns in our dataframe to make them more readable and to consist of only relevant/interesting data.

"""
print("Cleaning DataFrame...\n")

# First removing any columns that are completely of no interest
playlist_df = playlist_df.drop(columns=['available_markets', 'disc_number', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'is_local', 'track', 'track_number', 'type', 'uri', 'preview_url'])

# Getting the artist's id from the album
playlist_df['artist_id'] = playlist_df['album'].apply(lambda x: x['artists'][0]['id'])

# Keys that we want are: album_type, name, release_date, total_tracks
def filter_album(album):
    # Little function to filter out irrelevant album data.
    new_data = {
    'album_type': None,
    'name': None,
    'release_date': None,
    'total_tracks': None,
    'uri': None
    }
    for key in new_data.keys():
        new_data[key] = album[key]
    return new_data

# Filtering every album row
playlist_df['album'] = playlist_df['album'].apply(lambda x: filter_album(x))

# We just want the artist's name from that column
playlist_df['artists'] = playlist_df['artists'].apply(lambda x: x[0]['name'])

print("Playlist DF Complete!\n")

print("Analysing artists...\n")


# My code to get the album info. It was not helpful for what I wanted to achieve so I've commented it out.

# # # Now moving on to get the genres of each track. This one is different as we can only access genres from the album the song is in.
# # # Hopefully it works with singles
# album_df = pd.DataFrame(columns=sp.album('spotify:album:3fSff3bKd7pS7kLYiNakMV').keys())

# # # So we need to go through our playlist_df to get the URI of each album that each song is from and then add the album to a new database, grab the genres and other relevant stuff and keep them somewhere.

# for album in playlist_df['album']:
#     album_df.loc[len(album_df)] = sp.album(album['uri']).values()

# album_df.to_csv('albums.csv')

# Okay so after some trial and error I'm not able to get any genres from any of the albums. We're going to try the artists now.
artist_df = pd.DataFrame(columns=sp.artist(NPH).keys())

for artist in playlist_df['artist_id']:
    artist_df.loc[len(artist_df)] = sp.artist(artist).values()

# artist_df.to_csv('artists.csv')

playlist_df['genres'] = artist_df['genres']

# Putting the data into a csv file
# playlist_df.to_csv('results.csv')
print("Complete.")
"""