import pandas as pd
import json

# Load JSON
with open('main_database.json', 'r') as f:
    json_data = json.load(f)

# Convert to DataFrame
df_main = pd.DataFrame(json_data)

required_columns = ['Track URI', 'Track Name', 'Artist Name(s)', 'Mood', 'Genres', 'Release Date']
if not all(col in df_main.columns for col in required_columns):
    raise ValueError(f"Main database must contain columns: {required_columns}")