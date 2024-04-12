import pandas as pd
from fuzzywuzzy import fuzz

# Read the CSV files
hostels_df = pd.read_csv('Privies.csv', low_memory=False)
bigData_df = pd.read_csv('mother4.csv', low_memory=False)

# Function to find the best match for the destination
def find_best_match(destination, hostels_df):
    best_score = 0
    best_match = None
    for hostel_name in hostels_df['Name']:
        score = fuzz.token_sort_ratio(destination, hostel_name)
        if score > best_score:
            best_score = score
            best_match = hostel_name
    return best_match if best_score >= 80 else None

# Function to update latitude and longitude
def update_lat_long(destination, hostels_df):
    best_match = find_best_match(destination, hostels_df)
    if best_match:
        # Get the latitude and longitude from the hostels_df
        return hostels_df[hostels_df['Name'] == best_match][['Latitude', 'Longitude']].iloc[0].tolist()
    return None, None

# Count matches
match_count = 0

# Apply the function to each destination in bigData
for index, row in bigData_df.iterrows():
    lat, long = update_lat_long(row['Destination'], hostels_df)
    if lat is not None and long is not None:
        bigData_df.at[index, 'Latitude'] = lat
        bigData_df.at[index, 'Longitude'] = long
        match_count += 1

# Output the match count
print(f"Number of matches found: {match_count}")

# Save the updated bigData DataFrame
bigData_df.to_csv('mother5.csv', index=False)