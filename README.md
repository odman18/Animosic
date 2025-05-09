# 🎧 Animosic Project

**Animosic** is a mood-based music playlist generation system that creates personalized playlists based on user inputs such as mood, genre, and artist. It uses a pre-trained machine learning model to predict song moods and combines tracks from a local database with new songs fetched from Spotify.

---

## 🌐 Frontend Overview

The frontend is a static web application built with **HTML**, **CSS**, and **JavaScript**. It provides an interactive user interface for:
- Selecting moods, genres, and artists
- Naming playlists
- Integrating with Spotify to create playlists

Make sure the `Assets` folder (containing images like the Spotify logo and cassette graphics) is present for a complete UI experience.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/odman18/Animosic.git
cd Animosic
```

### 2. Set Up a Virtual Environment

**Unix/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Spotify API Credentials

Create a `.env` file in the root directory with your credentials:

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### 5. Generate Required Files

- **Main Database**  
Run the following to convert your CSV to JSON:

```bash
python convert_csv_to_json.py
```
Ensure your CSV file (e.g., `Final_database_predicted1.csv`) is in the correct location.

- **Model and Scaler**  
Open and run `Animosic_Model.ipynb` using your training dataset. This will generate:

```text
animosic_scaler1.pkl
animosic_mood_model1.pkl
```
Necessary .csv files can be found inside `CSV_Data` folder

### 6. Run the Application

```bash
python main.py
```

---

## 🌍 Frontend Setup

No additional dependencies are needed.

To test the frontend UI, serve the files locally:

```bash
python -m http.server 3000
```

Then, open `http://localhost:3000` in your browser.

---

## 🤝 Contributing

Feel free to **fork** this repository and submit **pull requests** to contribute to Animosic!

