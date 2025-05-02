import pandas as pd
import json

# Load CSV
df_main = pd.read_csv('Final_database_predicted1.csv')

# Replace NaN with None
df_main = df_main.replace({float('nan'): None})

# Convert to JSON
json_data = df_main.to_dict(orient='records')

# Save to file
with open('main_database.json', 'w') as f:
    json.dump(json_data, f, indent=4)