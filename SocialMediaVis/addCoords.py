import pandas as pd

# Load the geoData.csv and noboCombined.csv into DataFrames
geo_data = pd.read_csv('50632geo_posts.csv')
nobo_combined = pd.read_csv('soboCombined.csv')

# Merge the two DataFrames on 'Post_ID', keeping all rows from nobo_combined
# and only the matching rows from geo_data. The 'how' parameter set to 'left' ensures this.
merged = nobo_combined.merge(geo_data[['Post_ID', 'Latitude', 'Longitude']], 
                             on='Post_ID', 
                             how='left')



# Save the merged DataFrame back to noboCombined.csv
merged.to_csv('soboCombined.csv', index=False)

number_of_matches = merged['Latitude'].notna().sum()

# Print the number of matches to the terminal
print(f"Number of matches found: {number_of_matches}")