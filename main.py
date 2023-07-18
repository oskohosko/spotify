"""

"""
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import json
import openai

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
playlist_uri = "spotify:Oskar_Hosken:TECHNO:playlist:1lGXPfqwCeSqZ0O5h4yps0"
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

# Cleaning up columns in our dataframe to make them more readable and to consist of only relevant/interesting data.

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

playlist_df['album'] = playlist_df['album'].apply(lambda x: filter_album(x))

playlist_df['artists'] = playlist_df['artists'].apply(lambda x: x[0]['name'])

print("Playlist DF Complete!\n")

print("Analysing artists...\n")

# Okay so after some trial and error I'm not able to get any genres from any of the albums. We're going to try the artists now.
artist_df = pd.DataFrame(columns=sp.artist(NPH).keys())

for artist in playlist_df['artist_id']:
    artist_df.loc[len(artist_df)] = sp.artist(artist).values()

playlist_df['genres'] = artist_df['genres']

print('Getting audio features...\n')

# Getting audio features for every track
playlist_tracks = [song_id for song_id in playlist_df['id']]
track_features = sp.audio_features(playlist_tracks)
features_df = pd.DataFrame(columns=track_features[0].keys(), data=track_features)

# Dropping irrelevent columns and merging
features_df = features_df.drop(columns=['type','uri','track_href','analysis_url','duration_ms','time_signature'])
playlist_df = pd.merge(playlist_df, features_df)

# Now that we have everything that we can get from the spotify API, we are going to grab some lyrics using Musixmatch's API

"""
This section will be dedicated to the Musixmatch part of the code. My thoughts and ideas are that we can grab 30% of the lyrics of each song in our playlist using Musixmatch's free API. This will allow us to delve a little deeper into the meaning of songs. We can then use those lyrics and OpenAI's API to put into GPT 3.5 which can summarise the key themes and meanings behind each song into perhaps 5 words each.
These 5 words will then be associated with every song, along with genre and other audio features if I think they're necessary to include.
Then, we can get the most commonly occuring genres, themes and song meanings to attach alongside the genres to plug into DALLE 2 which can then give us a playlist cover image.
"""

# Firstly, let's make sure we can get lyrics first by creating a function

# Getting our API key so we can make requests
KEY = os.getenv("MM_API_KEY")

def get_lyrics(track_name, artist_name):
    """
    Function that gets lyrics for an input track by the input artist.
    It does so by first finding the musixmatch track id and then using that track id to get lyrics.
    """
    api_key = KEY
    base_url = 'http://api.musixmatch.com/ws/1.1/'

    # Making a search request to get the track_id
    search_url = base_url + 'track.search'
    search_params = {
        'q_track': track_name,      #&q_track=
        'q_artist': artist_name,    #&q_artist=
        'apikey': api_key,
        'format': 'json'
        }

    response = requests.get(search_url, params=search_params)
    data = response.json()
    for track in data['message']['body']['track_list']:
        # Some songs don't have lyrics attached
        if track['track']['has_lyrics']:
            track_id = track['track']['track_id']
            break
        return None

    # Making a request to get the lyrics using the track_id
    lyrics_url = base_url + 'track.lyrics.get'
    lyrics_params = {
        'track_id': track_id,
        'apikey': api_key,
        'format': 'json'
        }
    response = requests.get(lyrics_url, params=lyrics_params)
    data = response.json()
    lyrics = data['message']['body']['lyrics']['lyrics_body']

    return lyrics

# Now we can use this function on our main playlist_df to get lyrics for each song.
print("Getting lyrics...\n")
# playlist_df['lyrics'] = playlist_df.apply(lambda row: get_lyrics(row['name'], row['artists']), axis=1)
playlist_df.to_csv(playlist_name + '.csv')
print("Complete!")

"""
Onto the OpenAI section. This is where we will be using GPT and DALLE to get us key words and themes and images respectively.
"""

openai.api_key = os.getenv("OPENAI_KEY")