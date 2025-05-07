# Animosic Project

Animosic is a mood-based music playlist generation system that creates personalized playlists based on user inputs such as mood, genre, and artist. It uses a pre-trained machine learning model to predict song moods and combines tracks from a local database with new songs fetched from Spotify.

## Frontend Overview

The frontend is a static web application built with HTML, CSS, and JavaScript. It provides an interactive user interface to select moods, genres, and artists, name playlists, and integrate with Spotify for playlist creation. Assets (e.g., images) are included in the Assets folder.

## Setup Instructions
### Clone the Repository
```bash
git clone https://github.com/odman18/Animosic.git
cd Animosic

### Set Up a Virtual Environment

Follow standard Python virtual environment setup (e.g., python -m venv venv and source venv/bin/activate on Unix or venv\Scripts\activate on Windows).

### Install Dependencies
```bash
pip install -r requirements.txt

### configure Spotify API Credentials
Create a .env file with your Spotify API credentials:
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

###Generate Required Files

Database: Run python convert_csv_to_json.py with Final_database_predicted1.csv to generate main_database.json.

Model and Scaler: Run python Animosic_Model.ipynb with the training dataset to generate animosic_scaler1.pkl and animosic_mood_model1.pkl.

### Run the Application
```bash
python main.py

### Frontend Setup

No additional dependencies are required for the frontend.

Serve the files locally (e.g., using python -m http.server 3000 in the project root) to test the UI.

Ensure the Assets folder is present for images (e.g., Spotify logo, cassette).

### Contributing
Feel free to fork this repository and submit pull requests!
