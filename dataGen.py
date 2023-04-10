"""
This program is intended to collect a dataset from Spotify's Developer API
Process:
1. Collect EDM Playlists for Different Genres.
2. From the playlists, collect track analysis individually.
3. Save the dataset in .csv format
"""

import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = '7a1f9f43284247beb18a00bd0a274fe5'
client_secret = '827a7a49c03745ae952971c94c1f5678'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

genres = ['house', 'techno', 'trance', 'dubstep', 'dnb', 'hardstyle']

df = pd.concat(pd.read_excel('./spotify_playlists.xlsx', sheet_name=None), ignore_index=True)


def get_features(playlist_id, genre):
    print(playlist_id + " " + genre)
    results = sp.playlist_tracks(playlist_id)
    songs = results['items']

    while results['next']:
        results = sp.next(results)
        songs.extend(results['items'])

    ids = []

    for i in range(len(songs)):
        ids.append(songs[i]['track']['id'])

    ids = list(filter(None, ids))
    features = []

    for i in range(0, len(ids), 50):
        audio_features = sp.audio_features(ids[i:i + 50])
        for track in audio_features:
            features.append(track)

    features = list(filter(None, features))
    df = pd.DataFrame(features)
    df['genre'] = genre
    return df


def create_df(playlists):
    result = pd.DataFrame()

    for i in range(len(playlists)):
        df = get_features(playlists['playlistid'][i], playlists['genre'][i])
        # df['title'] = playlists['title'][i]
        result = pd.concat([result, df], ignore_index=True)

    result = result.drop_duplicates()
    result = result[result.duration_ms < 1000000]
    result = result[result.tempo > 50]
    return result


songs = create_df(df)
print('init Complete')

print(songs[songs.genre == 'dubstep']['tempo'].head())


def change2full_time(data, genre):
    tempo = data.loc[data.genre == genre, 'tempo']
    threshold = max(tempo)/2
    print(genre + str(threshold))
    tempo[tempo < threshold] = tempo * 2
    return tempo


songs.loc[songs.genre == 'dubstep', 'tempo'] = change2full_time(songs, 'dubstep')
songs.loc[songs.genre == 'dnb', 'tempo'] = change2full_time(songs, 'dnb')
songs.loc[songs.genre == 'hardstyle', 'tempo'] = change2full_time(songs, 'hardstyle')
print("full time processed")


def filter_tempo(data, genre, max_thresh, min_thresh):
    tempo = songs.loc[songs.genre == genre, 'tempo']

    above_threshold = tempo[tempo > max_thresh].index.tolist()
    below_threshold = tempo[tempo < min_thresh].index.tolist()
    indexNames = above_threshold + below_threshold

    data.drop(indexNames, inplace=True)


filter_tempo(songs, 'house', 135, 115)
filter_tempo(songs, 'techno', 150, 120)
filter_tempo(songs, 'trance', 155, 125)
filter_tempo(songs, 'dubstep', 220, 110)
filter_tempo(songs, 'dnb', 185, 160)
filter_tempo(songs, 'hardstyle', 165, 140)

print("tempo controlled")
print(songs.head())
print("techno:"+str(len(songs[songs['genre'] == 'techno'])))
print("trance:"+str(len(songs[songs['genre'] == 'trance'])))
print("dubstep:"+str(len(songs[songs['genre'] == 'dubstep'])))
print("hardstyle:"+str(len(songs[songs['genre'] == 'hardstyle'])))
print("house:"+str(len(songs[songs['genre'] == 'house'])))
print("dnb:"+str(len(songs[songs['genre'] == 'dnb'])))


def sample_songs(df, genres, n):
    result = pd.DataFrame()
    for i in range(len(genres)):
        sample = df[df['genre'] == genres[i]].sample(n=n)
        result = pd.concat([result, sample], ignore_index=True)

    return result


songs = sample_songs(songs, genres, 1000)
songs.to_csv('./edm_tracks.csv')
print("Complete!")
