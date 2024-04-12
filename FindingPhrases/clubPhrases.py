import pandas as pd

def check_bounds(lat, long, lat_start, lat_end, long_start, long_end):
    """Check if given latitude and longitude fall within given bounds."""
    #print(lat_end)
    #print(long_end)
    #and long_start <= long <= long_end lat_start <= lat <= lat_end
    return long_start <= long <= long_end 


# Load the Excel files into DataFrames
df_merged = pd.read_excel('magicFiltered2023.xlsx')

df_merged['Longitude'] = df_merged['Longitude'].astype(float)
combinedCoords = pd.read_excel('combinedCoords.xlsx')

# Convert the relevant columns to float to ensure proper comparison
cols_to_convert = ['latitude_start', 'latitude_end', 'longitude_start', 'longitude_end']
for col in cols_to_convert:
    combinedCoords[col] = combinedCoords[col].astype(float)

# Add columns for Region and Acronym in the df_merged DataFrame
df_merged['Region'] = ""
df_merged['Acronym'] = ""


# Iterate through each row in df_merged
for idx, row in df_merged.iterrows():
    lat, long = row['Latitude'], row['Longitude']
    
    # Check each row in combinedCoords to find matching bounds
    for _, region in combinedCoords.iterrows():
        if check_bounds(lat, long, region['latitude_start'], region['latitude_end'], region['longitude_start'], region['longitude_end']):
            #print("HEREH")
            df_merged.at[idx, 'Region'] = region['Region']
            df_merged.at[idx, 'Acronym'] = region['Acronym']
            break  # Assuming a point can belong to only one region

# Save the updated df_merged DataFrame to a new Excel file
df_merged.to_excel('clubPhrases.xlsx', index=False)