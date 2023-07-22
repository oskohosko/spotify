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
from collections import Counter

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

    return lyrics

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

def categorise(feature: list):
    """
    Function to categorise our audio features. Skips tempo and valence as they are slightly different.
    """
    value, category = feature[0], feature[1]

    adjective = ''
    if category == "energy":
        adjective = "Energetic"
    elif category == "danceability":
        adjective = "Danceable"
    elif category == "acousticness":
        adjective = "Acoustic"
    elif category == "speechiness":
        adjective = "Speechy"
    elif category == "instrumentalness":
        adjective = "Instrumental"

    if value >= 0.8:
        return "Very" + " " + adjective
    elif value >= 0.6:
        return adjective
    elif value >= 0.4:
        return "Moderately" + " " + adjective
    else:
        return None # Don't want to consider these values in our analysis

def categorise_valence(valence):
    """
    Categorises how cheerful a track is based on its valence value.
    """
    if valence >= 0.8:
        return "Very Happy"
    elif valence >= 0.6:
        return "Happy"
    elif valence >= 0.4:
        return None # Don't want to consider this value in our analysis
    elif valence >= 0.2:
        return "Sad"
    else:
        return "Very Sad"

def summarise_themes(themes: pd.Series):
    """
    Takes the playlist_df['themes'] column and uses GPT to summarise them.
    """
    openai.api_key = os.getenv("OPENAI_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f'Here is a series of key meanings and themes for a spotify playlist. Can you please summarise all of these words, themes and meanings into 5 words. Format your response as "word 1", "word 2", "word 3", "word 4", "word 5": {themes}'}
        ])
    return completion.choices[0].message.content

def get_images(genres, themes, audio_features):
    """
    Takes the playlist's genres, themes and audio features and makes a cover image.
    """
    openai.api_key = os.getenv("OPENAI_KEY")
    response = openai.Image.create(
        prompt=f"generate me an image on {genres} music about {themes}, {audio_features}, without any words on the image",
        n=4,
        size="1024x1024",
        response_format="url"
        )
    return response.data

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
        print("Starting...\n")
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
        print("Artists...\n")
        artist_df = pd.DataFrame(columns=sp.artist(NPH).keys())
        for artist in playlist_df['artist_id']:
            artist_df.loc[len(artist_df)] = sp.artist(artist).values()

        playlist_df['genres'] = artist_df['genres']

        # Getting audio features for every track
        print("Audio features...\n")
        playlist_tracks = [song_id for song_id in playlist_df['id']]
        track_features = sp.audio_features(playlist_tracks)
        features_df = pd.DataFrame(columns=track_features[0].keys(), data=track_features)

        # Dropping irrelevent columns and merging
        features_df = features_df.drop(columns=['type','uri','track_href','analysis_url','duration_ms','time_signature', 'key', 'loudness', 'mode', 'liveness'])
        playlist_df = pd.merge(playlist_df, features_df)

        """
        Now that we have everything in our dataframe, it's time to do a little bit more analysing.
        Let's look at the audio features:
        > danceability: how suitable the track is for dancing. 0 to 1.0
        > energy: measure of intensity and activity 0 to 1.0
        > speechiness: measure of how *spoken* the track is. Like a podcast for instance. above 0.66 mostly spoken
        > acousticness: measure from 0 to 1.0 on whether the track is acoustic. (confidence measure)
        > instrumentalness: predicts whether a track has no vocals. (confidence measure) closer to 1, less lyrics
        > valence: musical positivity measure. 0 to 1.0 sad, angry to happy, cheerful
        > tempo: bpm
        """
        print("Categorising audio features...\n")
        # Categorising every feature based on their mean values
        audio_feature_cats = {
            "danceability": categorise([playlist_df['danceability'].mean(), "danceability"]),
            "energy": categorise([playlist_df['energy'].mean(), "energy"]),
            "speechiness": categorise([playlist_df['speechiness'].mean(), "speechiness"]),
            "acousticness": categorise([playlist_df['acousticness'].mean(), "acousticness"]),
            "instrumentalness": categorise([playlist_df['instrumentalness'].mean(), "instrumentalness"]),
            "valence": categorise_valence(playlist_df['valence'].mean()),
            # "tempo": round(playlist_df['tempo'].mean())     # tempo as a value is easier to understand
            }
        # Audio features are None if their value isn't worth putting into DALLE
        # Putting all features that aren't None in to a list
        features = [feature for feature in audio_feature_cats.values() if feature != None]

        #! Need to test whether we have enough lyrics in the playlist to analyse
        print("Getting lyrics...\n")
        # Now that we have everything that we can get from the spotify API, we are going to grab some lyrics using Musixmatch's API
        playlist_df['lyrics'] = playlist_df.apply(lambda row: get_lyrics(row['name'], row['artists']), axis=1)

        # Onto the OpenAI section. This is where we will be using GPT and DALLE to get us key words and themes and images respectively.
        print("Analysing themes...\n")
        playlist_df['themes'] = playlist_df['lyrics'].apply(lambda x: get_themes(x) if x != None else None)
        playlist_df.to_csv(playlist_name + '.csv')

        # Now we are going to look at all the themes of the lyrics and get GPT to summarise them for me, then put them into a list
        theme_summary = summarise_themes(playlist_df['themes']).split(", ")

        # Cleaning each string of genres and getting them all into individual strings (some returned a list of multiple genres)
        genres_temp = [str(genre.strip("[]")).split(", ") for genre in playlist_df['genres']]
        all_genres = [genre.strip("'") for genre in sum(genres_temp, [])]

        # Now let's get the 2 most common genres using the Counter module from collections
        top_genres_temp = Counter(all_genres).most_common(2)
        top_genres = [genre[0] for genre in top_genres_temp]

        # Just need to think about how I'm going to format my request to DALLE
        """
        music album cover, genres: {genre 1}, {genre 2}, themes: {themes1,2,3,4,5}, audio features: feature1,2,3 etc
        """
        print("Generating images...\n")
        images = get_images(top_genres, theme_summary, features)

        print("Complete!")
        print(images)
        return images



if __name__ == "__main__":
    main()