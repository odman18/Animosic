# Animosic Project

Animosic is a mood-based music playlist generation system that creates personalized playlists based on user inputs such as mood, genre, and artist. It uses a pre-trained machine learning model to predict song moods and combines tracks from a local database with new songs fetched from Spotify.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/odman18/Animosic.git
   cd Animosic

2. Set up a virtual environment

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file with your Spotify API credentials:

SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

Refer to .env.example for the format.

5. Generate required files:

Database: Run python convert_csv_to_json.py with Final_database_predicted1.csv to generate main_database.json.

Model and Scaler: Run python Animosic_Model.ipynb with the training dataset to generate animosic_scaler1.pkl and animosic_mood_model1.pkl.

6. Run the application:
python main.py

Contributing
Feel free to fork this repository and submit pull requests!

