import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from utils.audio_features import estimate_audio_features
import pandas as pd
import random

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify API setup
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Define default empty DataFrame with correct columns
default_columns = ['Track URI', 'Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']
empty_df = pd.DataFrame(columns=default_columns)

# Mood to search keywords mapping
mood_keywords = {
    "Focus/Study": "chill OR instrumental OR acoustic",
    "Joyful": "happy OR upbeat OR cheerful",
    "Party": "dance OR party OR energetic",
    "Melancholic": "sad OR melancholic OR emotional",
    "Calm": "calm OR relaxing OR soothing",
    "Reflective": "reflective OR introspective OR deep",
    "Romantic": "romantic OR love OR tender",
    "Workout": "workout OR energetic OR motivational"
}

def fetch_and_predict_tracks(query, genre_for_estimation, limit, used_uris, target_mood, scaler, model):
    offset = random.randint(0, 50)
    try:
        results = sp.search(q=query, type='track', limit=limit, offset=offset)
    except Exception as e:
        print(f"Error fetching tracks for query '{query}': {e}")
        return empty_df
    tracks = []
    for track in results['tracks']['items']:
        track_id = track['id']
        track_uri = f"spotify:track:{track_id}"
        if track_uri in used_uris:
            continue
        used_uris.add(track_uri)
        track_name = track['name']
        artist_name = ", ".join(artist['name'] for artist in track['artists'])
        release_date = track['album']['release_date'].split('-')[0] if track['album']['release_date'] else 'Unknown'
        genres = genre_for_estimation if genre_for_estimation else 'Unknown'
        features = estimate_audio_features(track, genre_for_estimation, target_mood)
        features_df = pd.DataFrame([features])
        features_scaled = scaler.transform(features_df)
        predicted_mood = model.predict(features_scaled)[0]
        track_data = {
            'Track URI': track_uri,
            'Track Name': track_name,
            'Artist Name(s)': artist_name,
            'Mood': predicted_mood,
            'Genres': genres,
            'Release Date': release_date
        }
        tracks.append(track_data)
    df = pd.DataFrame(tracks) if tracks else empty_df

    # Replace any NaN values with None to ensure JSON compliance
    df = df.replace({float('nan'): None})
    return df