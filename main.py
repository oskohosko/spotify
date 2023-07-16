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

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# To test before making a json file with all the info etc
playlist_uri = "spotify:Oskar_Hosken:TECHNO:playlist:1lGXPfqwCeSqZ0O5h4yps0"
like = True

username, playlist_id, playlist_name = playlist_uri.split(':')[1], playlist_uri.split(':')[4], playlist_uri.split(':')[2]
# Returning a dict of all the tracks
sp_tracks = sp.user_playlist(username, playlist_id, 'tracks')

# Creating a dataframe with basic details on the track, e.g artist name, album name, track name
names_df = pd.DataFrame(columns=sp_tracks['tracks']['items'][0]['track'].keys())

# Adding the data into the df
for track in sp_tracks['tracks']['items']:
    names_df.loc[len(names_df)] = track['track']

# Cleaning up columns in our dataframe to make them more readable and to consist of only relevant/interesting data.

# First removing any columns that are completely of no interest

names_df = names_df.drop(columns=['available_markets', 'disc_number', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'is_local', 'track', 'track_number', 'type', 'uri', 'preview_url'])

# Keys that we want are: album_type, name, release_date, total_tracks
def filter_album(album):
    """
    Little function to filter out irrelevant album data.
    """
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
names_df['album'] = names_df['album'].apply(lambda x: filter_album(x))

# We just want the artist's name from that column
names_df['artists'] = names_df['artists'].apply(lambda x: x[0]['name'])

# Putting the data into a csv file
# names_df.to_csv('results.csv')

# Now moving on to get the genres of each track. This one is different as we can only access genres from the album the song is in.
# Hopefully it works with singles
album_df = pd.DataFrame(columns=sp.album('spotify:album:3fSff3bKd7pS7kLYiNakMV').keys())

# So we need to go through our names_df to get the URI of each album that each song is from and then add the album to a new database, grab the genres and other relevant stuff and keep them somewhere.

print(album_df)