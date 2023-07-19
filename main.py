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

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

TECHNO = "spotify:Oskar_Hosken:TECHNO:playlist:1lGXPfqwCeSqZ0O5h4yps0"  # My techno playlist
PROVINCIAL = "spotify:Oskar_Hosken:PROVINCIAL:playlist:07o6kTp4nYhgcbIvVQpcEq"  # My aussie indie playlist
TEST_ALBUM = "spotify:album:3fSff3bKd7pS7kLYiNakMV"     # Test album for columns for dataframe
NPH = "500YRyClzP6Z7HtWd1BIje"  # Northeast Party House



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

def get_lyrics(track_name, artist_name):
    """
    Function that gets lyrics for an input track by the input artist.
    It does so by first finding the musixmatch track id and then using that track id to get lyrics.
    """
    api_key = os.getenv("MM_API_KEY")
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

    # Cleaning the lyrics
    return lyrics.split("...")[0].strip()

def get_themes(lyrics):
    """
    Uses OpenAI's GPT 3.5 Turbo to get 5 key words to describe the meaning and themes behind songs.
    """
    openai.api_key = os.getenv("OPENAI_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f'Please give me the key themes and meanings behind these lyrics in 5 words: {lyrics}'}
        ])

    return completion.choices[0].message.content

def main():
    """

    """
    playlist_uri = PROVINCIAL
    username, playlist_id, playlist_name = playlist_uri.split(':')[1], playlist_uri.split(':')[4], playlist_uri.split(':')[2]

    # Checking to see if a dataframe has already been created for this playlist
    filename = playlist_name + '.csv'
    path = './'
    if os.path.isfile(os.path.join(path, filename)):
        playlist_df = pd.read_csv(os.path.join(path, filename))
        print("Playlist already in system.")
        return None
    # Otherwise, let's go through the analysis stuff
    else:
        # Creating a dataframe with basic details on the track, e.g artist name, album name, track name
        sp_tracks = sp.user_playlist(username, playlist_id, 'tracks')
        playlist_df = pd.DataFrame(columns=sp_tracks['tracks']['items'][0]['track'].keys())
        for track in sp_tracks['tracks']['items']:
            playlist_df.loc[len(playlist_df)] = track['track']

        # First removing any columns that are completely of no interest
        playlist_df = playlist_df.drop(columns=['available_markets', 'disc_number', 'episode', 'explicit', 'external_ids', 'external_urls', 'href', 'is_local', 'track', 'track_number', 'type', 'uri', 'preview_url'])

        # Getting the artist's id from the album
        playlist_df['artist_id'] = playlist_df['album'].apply(lambda x: x['artists'][0]['id'])
        playlist_df['album'] = playlist_df['album'].apply(lambda x: filter_album(x))
        playlist_df['artists'] = playlist_df['artists'].apply(lambda x: x[0]['name'])

        # Okay so after some trial and error I'm not able to get any genres from any of the albums. We're going to try the artists now.
        artist_df = pd.DataFrame(columns=sp.artist(NPH).keys())
        for artist in playlist_df['artist_id']:
            artist_df.loc[len(artist_df)] = sp.artist(artist).values()

        playlist_df['genres'] = artist_df['genres']

        # Getting audio features for every track
        playlist_tracks = [song_id for song_id in playlist_df['id']]
        track_features = sp.audio_features(playlist_tracks)
        features_df = pd.DataFrame(columns=track_features[0].keys(), data=track_features)

        # Dropping irrelevent columns and merging
        features_df = features_df.drop(columns=['type','uri','track_href','analysis_url','duration_ms','time_signature'])
        playlist_df = pd.merge(playlist_df, features_df)

        # Now that we have everything that we can get from the spotify API, we are going to grab some lyrics using Musixmatch's API
        playlist_df['lyrics'] = playlist_df.apply(lambda row: get_lyrics(row['name'], row['artists']), axis=1)

        # Onto the OpenAI section. This is where we will be using GPT and DALLE to get us key words and themes and images respectively.
        playlist_df['themes'] = playlist_df['lyrics'].apply(lambda x: get_themes(x) if x != None else None)

        playlist_df.to_csv(playlist_name + '.csv')
        return None



# if __name__ == "__main__":
#     main()