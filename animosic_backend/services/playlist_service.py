import pandas as pd
from services.spotify_service import fetch_and_predict_tracks, mood_keywords, empty_df
from data.database import df_main
import joblib
import time

# Load scaler and model
scaler = joblib.load('animosic_scaler1.pkl')
model = joblib.load('animosic_mood_model1.pkl')

# Limited genres and artists
genres_artists = {
    "Afrobeat": ["Burna Boy", "Wizkid", "Davido", "Tiwa Savage", "Rema"],
    "Pop": ["Taylor Swift", "Billie Eilish", "The Weeknd", "Dua Lipa", "Ed Sheeran"],
    "Rock": ["The Beatles", "Imagine Dragons", "Coldplay", "Linkin Park", "Muse"]
}

# Fallback mood mapping (only for Spotify tracks)
fallback_moods = {
    "Focus/Study": "Calm",
    "Joyful": "Party",
    "Reflective": "Calm",
    "Romantic": "Calm",
    "Workout": "Party"
}

def generate_playlist(user_mood, user_genre, user_artist, total_playlist_size=20, tracks_per_request=50):
    # Validate user inputs
    if user_mood not in mood_keywords:
        raise ValueError(f"Mood must be one of {list(mood_keywords.keys())}")
    if user_genre and user_genre not in genres_artists:
        raise ValueError(f"Genre must be one of {list(genres_artists.keys())} or None")
    if user_artist and (not user_genre or user_artist not in genres_artists.get(user_genre, [])):
        raise ValueError(f"Artist must match the selected genre {user_genre} or both should be None")

    # Track used URIs to avoid duplicates
    used_uris = set()

    # Ensure df_main has consistent dtypes for key columns
    df_main_subset = df_main.astype({
        'Track URI': 'object',
        'Track Name': 'object',
        'Artist Name(s)': 'object',
        'Mood': 'object',
        'Genres': 'object',
        'Release Date': 'object'
    })

    # Step 1: Handle case when no genre/artist is selected
    if not user_genre and not user_artist:
        print("No genre or artist selected. Generating playlist from database (80%) and new songs (20%).")
        # 80% from database (16 tracks, 4 recent)
        recent_tracks = df_main[
            (df_main['Mood'] == user_mood) &
            (df_main['Release Date'].astype(str).str.isdigit()) &
            (df_main['Release Date'].astype(int) >= 2020) &
            (~df_main['Track URI'].isin(used_uris))
        ]
        recent_tracks = recent_tracks.sample(n=min(4, len(recent_tracks)), random_state=int(time.time())) if not recent_tracks.empty else empty_df
        print(f"Recent database tracks:\n{recent_tracks}")
        used_uris.update(recent_tracks['Track URI'].dropna().values)
        
        remaining_db = 12  # 16 total - 4 recent
        other_tracks = df_main[
            (df_main['Mood'] == user_mood) &
            (~df_main['Track URI'].isin(used_uris))
        ]
        other_tracks = other_tracks.sample(n=min(remaining_db, len(other_tracks)), random_state=int(time.time())) if not other_tracks.empty else empty_df
        print(f"Other database tracks:\n{other_tracks}")
        used_uris.update(other_tracks['Track URI'].dropna().values)
        
        playlist = pd.concat([recent_tracks, other_tracks], ignore_index=True)
        print(f"Playlist after database tracks:\n{playlist}")
        
        # 20% new songs (4 tracks)
        new_query = 'year:2023-2025'
        new_tracks_df = fetch_and_predict_tracks(new_query, None, tracks_per_request, used_uris, user_mood, scaler, model)
        print("\nNew songs (2023-2025) before selection:")
        print(new_tracks_df[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
        new_mood_tracks = new_tracks_df[new_tracks_df['Mood'] == user_mood].head(4)
        if len(new_mood_tracks) < 4:
            target_mood = fallback_moods.get(user_mood, user_mood)
            print(f"\nNot enough new songs matched mood {user_mood}. Using fallback mood {target_mood}:")
            new_mood_tracks = new_tracks_df[new_tracks_df['Mood'] == target_mood].head(4)
            print(new_mood_tracks[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
        print(f"Selected new songs:\n{new_mood_tracks}")
        used_uris.update(new_mood_tracks['Track URI'].dropna().values)
        playlist = pd.concat([playlist, new_mood_tracks], ignore_index=True)

    else:
        # Step 2: Select tracks by artist (3 tracks if available, fallback to 2)
        artist_mood_tracks = empty_df
        artist_found = False
        if user_artist:
            artist_query = f'artist:"{user_artist}" genre:"{user_genre}" {mood_keywords[user_mood]}'
            artist_tracks_df = fetch_and_predict_tracks(artist_query, user_genre, tracks_per_request, used_uris, user_mood, scaler, model)
            if artist_tracks_df.empty:
                print(f"No tracks found for query '{artist_query}'. Falling back to broader query.")
                artist_query = f'artist:"{user_artist}" genre:"{user_genre}"'
                artist_tracks_df = fetch_and_predict_tracks(artist_query, user_genre, tracks_per_request, used_uris, user_mood, scaler, model)
            print(f"\nArtist tracks ({user_artist}) before selection:")
            print(artist_tracks_df[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
            artist_mood_tracks = artist_tracks_df[artist_tracks_df['Mood'] == user_mood].head(3)
            artist_found = len(artist_mood_tracks) > 0
            if len(artist_mood_tracks) < 3:
                target_mood = fallback_moods.get(user_mood, user_mood)
                print(f"\nSystem couldn’t find songs from artist {user_artist} that match mood {user_mood}. Using fallback mood {target_mood}:")
                artist_mood_tracks = artist_tracks_df[artist_tracks_df['Mood'] == target_mood].head(2)
                print(artist_mood_tracks[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
            print(f"Selected artist tracks:\n{artist_mood_tracks}")
            used_uris.update(artist_mood_tracks['Track URI'].dropna().values)

        # Step 3: Select tracks by genre (4 tracks if available, fallback to 2)
        genre_mood_tracks = empty_df
        genre_found = False
        if user_genre:
            genre_query = f'genre:"{user_genre}" {mood_keywords[user_mood]}'
            genre_tracks_df = fetch_and_predict_tracks(genre_query, user_genre, tracks_per_request, used_uris, user_mood, scaler, model)
            if genre_tracks_df.empty:
                print(f"No tracks found for query '{genre_query}'. Falling back to broader query.")
                genre_query = f'genre:"{user_genre}"'
                genre_tracks_df = fetch_and_predict_tracks(genre_query, user_genre, tracks_per_request, used_uris, user_mood, scaler, model)
            print(f"\nGenre tracks ({user_genre}) before selection:")
            print(genre_tracks_df[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
            genre_mood_tracks = genre_tracks_df[genre_tracks_df['Mood'] == user_mood].head(4)
            genre_found = len(genre_mood_tracks) > 0
            if len(genre_mood_tracks) < 4:
                target_mood = fallback_moods.get(user_mood, user_mood)
                print(f"\nSystem couldn’t find songs in genre {user_genre} that match mood {user_mood}. Using fallback mood {target_mood}:")
                genre_mood_tracks = genre_tracks_df[genre_tracks_df['Mood'] == target_mood].head(2)
                print(genre_mood_tracks[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
            print(f"Selected genre tracks:\n{genre_mood_tracks}")
            used_uris.update(genre_mood_tracks['Track URI'].dropna().values)

        # Step 4: Notify user if both artist and genre fail
        if user_artist and user_genre and not artist_found and not genre_found:
            print(f"\nSystem couldn’t find songs that match your filter (artist: {user_artist}, genre: {user_genre}, mood: {user_mood}).")

        # Step 5: Select new songs (3 tracks if available, fallback to 2)
        new_query = 'year:2023-2025'
        new_tracks_df = fetch_and_predict_tracks(new_query, user_genre, tracks_per_request, used_uris, user_mood, scaler, model)
        print("\nNew songs (2023-2025) before selection:")
        print(new_tracks_df[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
        new_mood_tracks = new_tracks_df[new_tracks_df['Mood'] == user_mood].head(3)
        if len(new_mood_tracks) < 3:
            target_mood = fallback_moods.get(user_mood, user_mood)
            print(f"\nNot enough new songs matched mood {user_mood}. Using fallback mood {target_mood}:")
            new_mood_tracks = new_tracks_df[new_tracks_df['Mood'] == target_mood].head(2)
            print(new_mood_tracks[['Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']])
        print(f"Selected new songs:\n{new_mood_tracks}")
        used_uris.update(new_mood_tracks['Track URI'].dropna().values)

        # Step 6: Combine tracks and balance with database (4 recent tracks total in final playlist)
        playlist = pd.concat([artist_mood_tracks, genre_mood_tracks, new_mood_tracks], ignore_index=True)
        print(f"Playlist after Spotify tracks:\n{playlist}")
        
        # Define recent_tracks for this branch
        recent_tracks = df_main[
            (df_main['Mood'] == user_mood) &
            (df_main['Release Date'].astype(str).str.isdigit()) &
            (df_main['Release Date'].astype(int) >= 2020) &
            (~df_main['Track URI'].isin(used_uris))
        ]
        
        # Count current recent tracks (2020+) in the playlist
        recent_count = len(playlist[
            (playlist['Release Date'].astype(str).str.isdigit()) &
            (playlist['Release Date'].astype(int) >= 2020)
        ])
        recent_needed = max(0, 4 - recent_count)  # Ensure 4 recent tracks total
        
        # Select recent tracks from database
        recent_tracks = recent_tracks.sample(n=min(recent_needed, len(recent_tracks)), random_state=int(time.time())) if not recent_tracks.empty else empty_df
        print(f"Recent database tracks:\n{recent_tracks}")
        used_uris.update(recent_tracks['Track URI'].dropna().values)
        playlist = pd.concat([playlist, recent_tracks], ignore_index=True)
        print(f"Playlist after adding recent database tracks:\n{playlist}")
        
        # Fill remaining slots from database (strictly matching user_mood)
        remaining_slots = total_playlist_size - len(playlist)
        if remaining_slots > 0:
            additional_tracks = df_main[
                (df_main['Mood'] == user_mood) &
                (~df_main['Track URI'].isin(used_uris))
            ]
            additional_tracks = additional_tracks.sample(n=min(remaining_slots, len(additional_tracks)), random_state=int(time.time())) if not additional_tracks.empty else empty_df
            print(f"Additional database tracks:\n{additional_tracks}")
            used_uris.update(additional_tracks['Track URI'].dropna().values)
            playlist = pd.concat([playlist, additional_tracks], ignore_index=True)

    # Step 7: Ensure no duplicates and limit to 20 tracks
    playlist = playlist.drop_duplicates(subset=['Track URI']).head(total_playlist_size)
    # Select only the columns needed for the output
    output_columns = ['Track URI', 'Track Name', 'Artist Name(s)']
    playlist = playlist[output_columns]
    # Final cleanup of NaN values
    playlist = playlist.replace({float('nan'): None})
    print(f"Final playlist (limited columns):\n{playlist}")
    return playlist