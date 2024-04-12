import pandas as pd
import os
from fuzzywuzzy import fuzz

# Define the input directory and the output file
input_dir = '/home/ugrads/majors/jenniferchandran/SocialMediaVis/Sobo' 
output_file = os.path.join(input_dir, 'output.csv')

# List all the files in the directory
files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]

# Sort the files to make sure they are processed in the desired order
files.sort()

# List to store dataframes
dfs = []

# Iterrate through each file, read its content, and add a "Year" column
for file in files:
    path = os.path.join(input_dir, file)
    
    # Extract the year from the filename. Assumes filenames are like "2018.csv", "2019.csv", etc.
    year = file.split('.')[0]
    
    # Read the CSV content into a dataframe
    df = pd.read_csv(path)
    
    # Add a "Year" column
    df['Year'] = year
    
    # Append the dataframe to the list
    dfs.append(df)

# Concatenate all dataframes in the list
result = pd.concat(dfs, ignore_index=True)


# Save the combined dataframe to the output file
result.to_csv(output_file, index=False)


