def estimate_audio_features(track, genre, target_mood):
    popularity = track.get('popularity', 50)
    release_year = int(track['album']['release_date'].split('-')[0]) if track['album']['release_date'] else 2000
    genre = genre.lower() if genre else 'pop'
    artist_name = ", ".join(artist['name'] for artist in track['artists']).lower()
    track_name = track['name'].lower()

    if genre in ['pop', 'dance pop', 'edm', 'afrobeat']:
        danceability = 0.85 if popularity > 70 else 0.65
    elif genre in ['hip hop', 'rap']:
        danceability = 0.75
    elif genre in ['rock', 'indie']:
        danceability = 0.5
    elif genre in ['classical', 'instrumental', 'folk']:
        danceability = 0.25
    else:
        danceability = 0.4

    if genre in ['edm', 'rock', 'metal', 'hip hop', 'afrobeat']:
        energy = 0.85 if release_year > 2000 else 0.65
    elif genre in ['pop', 'dance pop']:
        energy = 0.75 if release_year > 2000 else 0.55
    elif genre in ['classical', 'instrumental', 'folk']:
        energy = 0.25
    else:
        energy = 0.4
    if 'billie eilish' in artist_name:
        energy = 0.35

    if genre in ['pop', 'dance pop', 'afrobeat'] and popularity > 70:
        valence = 0.85
    elif genre in ['rock', 'indie', 'hip hop']:
        valence = 0.45
    elif genre in ['classical', 'folk']:
        valence = 0.35
    else:
        valence = 0.4
    if 'billie eilish' in artist_name:
        valence = 0.3

    if genre in ['edm', 'dance pop', 'afrobeat']:
        tempo = 120 if release_year > 2000 else 100
    elif genre in ['pop', 'rock', 'hip hop']:
        tempo = 110
    elif genre in ['classical', 'instrumental', 'folk']:
        tempo = 80
    else:
        tempo = 90

    if genre in ['hip hop', 'rap']:
        speechiness = 0.3
    elif genre in ['classical', 'instrumental']:
        speechiness = 0.03
    else:
        speechiness = 0.1

    if target_mood in ["Focus/Study", "Calm"]:
        danceability = min(danceability, 0.4)
        energy = min(energy, 0.3)
        speechiness = min(speechiness, 0.05)
        tempo = min(tempo, 90)
        valence = min(valence, 0.4)
    elif target_mood in ["Party", "Workout"]:
        danceability = max(danceability, 0.8)
        energy = max(energy, 0.8)
        tempo = max(tempo, 120)
        valence = max(valence, 0.7)
    elif target_mood == "Joyful":
        danceability = max(danceability, 0.7)
        energy = max(energy, 0.7)
        valence = max(valence, 0.8)
    elif target_mood == "Romantic":
        danceability = min(danceability, 0.5)
        energy = min(energy, 0.5)
        valence = max(valence, 0.7)
        tempo = min(tempo, 100)
    elif target_mood in ["Melancholic", "Reflective"]:
        danceability = min(danceability, 0.4)
        energy = min(energy, 0.4)
        valence = min(valence, 0.3)
        tempo = min(tempo, 90)

    if any(keyword in track_name for keyword in ['chill', 'instrumental', 'acoustic', 'study', 'focus']):
        danceability = min(danceability, 0.3)
        energy = min(energy, 0.2)
        speechiness = min(speechiness, 0.03)
    if any(keyword in track_name for keyword in ['dance', 'party', 'energetic']):
        danceability = max(danceability, 0.8)
        energy = max(energy, 0.8)

    return {
        'Danceability': danceability,
        'Energy': energy,
        'Valence': valence,
        'Tempo': tempo,
        'Speechiness': speechiness
    }