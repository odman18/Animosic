function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]]; // Swap elements
    }
    return array;
}
// Show Lunabot greeting on page load (only on welcome page)
if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    window.onload = function() {
        const greetingModal = document.getElementById('greeting-modal');
        greetingModal.style.display = 'flex';
    };
}

// Close the Lunabot greeting modal
function closeGreeting() {
    const greetingModal = document.getElementById('greeting-modal');
    greetingModal.style.display = 'none';
}

// Mood selection and color persistence
function selectMood(mood, color) {
    localStorage.setItem('selectedMood', mood);
    localStorage.setItem('moodColor', color);
    window.location.href = 'genre_artist.html';
}

// Change background color on hover for mood items
if (window.location.pathname.includes('mood.html')) {
    const moodItems = document.querySelectorAll('.mood-item');
    const originalBgColor = '#278783';

    // Function to remove .active from all mood items
    const clearActive = () => {
        moodItems.forEach(item => item.classList.remove('active'));
    };

    // Add click event to each mood item
    moodItems.forEach(item => {
        const selectButton = item.querySelector('.select-button');
        const moodColor = item.getAttribute('data-color');

        item.addEventListener('click', function() {
            clearActive(); // Remove .active from all items
            this.classList.add('active'); // Add .active to the clicked item
        });

        selectButton.addEventListener('mouseover', function() {
            document.body.style.backgroundColor = moodColor;
            document.querySelector('header').style.backgroundColor = moodColor;
        });

        selectButton.addEventListener('mouseout', function() {
            document.body.style.backgroundColor = originalBgColor;
            document.querySelector('header').style.backgroundColor = originalBgColor;
        });
    });

    // Set the first mood item as active by default
    if (moodItems.length > 0) {
        moodItems[0].classList.add('active');
    }
}

// Genre and Artist selection
let selectedGenre = null;
let selectedArtist = null;

function selectGenre(genre) {
    selectedGenre = genre;
    const genreItems = document.querySelectorAll('.genre-item');
    genreItems.forEach(item => {
        item.classList.remove('selected');
        if (item.textContent === genre) {
            item.classList.add('selected');
        }
    });

    // Show artist section
    const artistSection = document.getElementById('artist-section');
    const artistList = document.getElementById('artist-list');
    artistSection.style.display = 'block';
    artistList.innerHTML = '';

    // Define artists based on genre
    const artistsByGenre = {
        'Afrobeat': ['Burna Boy', 'Wizkid', 'Davido', 'Tiwa Savage', 'Rema'],
        'Pop': ['Taylor Swift', 'Billie Eilish', 'The Weeknd', 'Dua Lipa', 'Ed Sheeran'],
        'Rock': ['The Beatles', 'Imagine Dragons', 'Coldplay', 'Linkin Park', 'Muse']
    };

    const artists = artistsByGenre[genre] || [];
    artists.forEach(artist => {
        const div = document.createElement('div');
        div.className = 'artist-item';
        div.textContent = artist;
        div.onclick = () => selectArtist(artist);
        artistList.appendChild(div);
    });

    // Show generate button
    document.getElementById('generate-button').style.display = 'block';
}

function selectArtist(artist) {
    selectedArtist = artist;
    const artistItems = document.querySelectorAll('.artist-item');
    artistItems.forEach(item => {
        item.classList.remove('selected');
        if (item.textContent === artist) {
            item.classList.add('selected');
        }
    });
}

// Go to name playlist page
function goToNamePlaylist() {
    localStorage.setItem('selectedGenre', selectedGenre || '');
    localStorage.setItem('selectedArtist', selectedArtist || '');
    window.location.href = 'name_playlist.html';
}

// Apply mood color and display mood on name-playlist page
if (window.location.pathname.includes('name_playlist.html')) {
    const selectedMood = localStorage.getItem('selectedMood') || 'Unknown';
    document.getElementById('selected-mood').textContent = `Mood: ${selectedMood}`;
}

// Generate playlist
async function generatePlaylist() {
    const playlistName = document.getElementById('playlist-name').value;
    if (!playlistName) {
        alert('Please enter a playlist name.');
        return;
    }

    // Show loading state
    const generateButton = document.getElementById('generate-button');
    const loadingMessage = document.getElementById('loading-message');
    generateButton.disabled = true;
    generateButton.textContent = 'Generating...';
    loadingMessage.style.display = 'inline';

    const mood = localStorage.getItem('selectedMood');
    const genre = localStorage.getItem('selectedGenre') || null;
    const artist = localStorage.getItem('selectedArtist') || null;

    const requestBody = {
        mood: mood,
        genre: genre,
        artist: artist,
        access_token: ''
    };

    console.log('Generating playlist with request:', requestBody);

    try {
        const response = await fetch('http://localhost:8000/generate_playlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        console.log('Raw response status:', response.status);
        const data = await response.json();
        console.log('Backend response:', data);

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate playlist');
        }

        if (data.playlist && Array.isArray(data.playlist)) {
            console.log('Saving playlist to localStorage:', data.playlist);
            localStorage.setItem('playlistName', playlistName);
            localStorage.setItem('tracks', JSON.stringify(data.playlist));
            console.log('Saved tracks:', localStorage.getItem('tracks'));
            window.location.href = 'playlist.html';
        } else {
            throw new Error('Invalid playlist data received from backend');
        }
    } catch (error) {
        console.error('Error generating playlist:', error.message);
        alert('Error generating playlist: ' + error.message);
    } finally {
        // Reset loading state
        generateButton.disabled = false;
        generateButton.textContent = 'Done';
        loadingMessage.style.display = 'none';
    }
}

// Display playlist and handle Spotify addition
if (window.location.pathname.includes('playlist.html')) {
    const playlistName = localStorage.getItem('playlistName') || 'My Animosic Playlist';
    const tracks = JSON.parse(localStorage.getItem('tracks')) || [];

    console.log('Playlist Name:', playlistName);
    console.log('Tracks:', tracks);

    // Update the page with playlist details
    const playlistTitle = document.getElementById('playlist-title');
    const trackList = document.getElementById('track-list');

    if (playlistTitle) {
        playlistTitle.textContent = playlistName;
    } else {
        console.error('Playlist title element not found');
    }

    if (trackList) {
        if (tracks.length === 0) {
            trackList.innerHTML = '<div>No tracks available. Please generate a playlist.</div>';
        } else {
            const shuffledTracks = shuffleArray([...tracks]); // Create a copy to shuffle
            shuffledTracks.forEach(track => {
                const div = document.createElement('div');
                div.textContent = `${track['Track Name']} by ${track['Artist Name(s)']}`;
                trackList.appendChild(div);
            });
        }
    } else {
        console.error('Track list element not found');
    }

    // Check for access token and automatically add to Spotify
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get("access_token");
    if (accessToken) {
        console.log('Access token detected on page load, running addToSpotify()...');
        addToSpotify();
    }
}

// Spotify authentication
async function addToSpotify() {
    const playlistName = localStorage.getItem('playlistName') || 'My Animosic Playlist';
    const tracks = JSON.parse(localStorage.getItem('tracks')) || [];
    const token = localStorage.getItem("spotify_access_token");

    if (tracks.length === 0) {
        console.log("No tracks to add to Spotify.");
        alert("No tracks to add to Spotify.");
        return;
    }

    // Show loading state
    const addButton = document.getElementById('add-to-spotify-button');
    const loadingMessage = document.getElementById('loading-message');
    addButton.disabled = true;
    addButton.textContent = 'Add to Spotify';
    loadingMessage.style.display = 'inline';

    try {
        console.log("Fetching user ID...");
        const userResponse = await fetch("https://api.spotify.com/v1/me", {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!userResponse.ok) {
            const errorText = await userResponse.text();
            console.error("Failed to fetch user ID:", userResponse.status, errorText);
            throw new Error(`Failed to fetch user ID: ${errorText}`);
        }
        const userData = await userResponse.json();
        const userId = userData.id;
        console.log("User ID:", userId);

        console.log("Creating playlist...");
        const createResponse = await fetch(`https://api.spotify.com/v1/users/${userId}/playlists`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name: playlistName, description: "Generated by Animosic", public: false })
        });
        if (!createResponse.ok) {
            const errorText = await createResponse.text();
            console.error("Failed to create playlist:", createResponse.status, errorText);
            throw new Error(`Failed to create playlist: ${errorText}`);
        }
        const playlist = await createResponse.json();
        const playlistId = playlist.id;
        console.log("Playlist created with ID:", playlistId);

        console.log("Searching for track URIs...");
        const trackUris = [];
        for (const track of tracks) {
            const searchResponse = await fetch(
                `https://api.spotify.com/v1/search?q=${encodeURIComponent(track['Track Name'])}%20artist:${encodeURIComponent(track['Artist Name(s)'])}&type=track&limit=1`,
                { headers: { "Authorization": `Bearer ${token}` } }
            );
            const searchData = await searchResponse.json();
            const trackUri = searchData.tracks.items[0]?.uri;
            if (trackUri) {
                trackUris.push(trackUri);
                console.log(`Found URI for ${track['Track Name']}: ${trackUri}`);
            } else {
                console.log(`No URI found for ${track['Track Name']} by ${track['Artist Name(s)']}`);
            }
        }

        console.log("Adding tracks to playlist...");
        const addResponse = await fetch(`https://api.spotify.com/v1/playlists/${playlistId}/tracks`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ uris: trackUris })
        });
        if (addResponse.ok) {
            console.log("Playlist added successfully!");
            alert("Playlist added to your Spotify!");
            window.location.href = 'index.html'; // Redirect to home
        } else {
            const errorText = await addResponse.text();
            console.error("Failed to add tracks:", addResponse.status, errorText);
            throw new Error(`Failed to add tracks: ${errorText}`);
        }
    } catch (error) {
        console.error("Error adding to Spotify:", error.message);
        alert("Error adding to Spotify: " + error.message);
        // Clear token if it fails/expires
        localStorage.removeItem("spotify_access_token");
        window.location.href = "http://127.0.0.1:8000/login"; // Retry login
    } finally {
        // Reset loading state
        addButton.disabled = false;
        addButton.textContent = 'Add to Spotify';
        loadingMessage.style.display = 'none';
    }
}