import pandas as pd
import os
import string 

# Define a function that cleans up common abbreviations
def clean_abbreviations(s):
    if isinstance(s, str):
        s = s.replace('Mtn', 'Mt')
        s = s.replace('Mtn', 'Mt.')
        s = s.replace('Mtn', 'Mountain')
        s = s.title()
        return s
    
def rmve_punc(s): 
    if isinstance(s, str):
        s = ''.join(ch for ch in s if ch not in string.punctuation)
        return s

def lower_case(s):
    if isinstance(s, str):
        return s.lower()
    
def no_spaces(s):
    if isinstance(s, str):
        s = s.replace(' ', '')
    return s 
# Load the constant Excel file
df_constant = pd.read_excel('fileWith.xlsx')  # File with latitude and longitude

# Rename the 'shelter name' column in df_constant to 'destination' so it matches the other files
df_constant.rename(columns={'Shelter Name': 'Destination'}, inplace=True)
df_constant['Destination'] = df_constant['Destination'].apply(clean_abbreviations).apply(rmve_punc).apply(lower_case)


# Initialize an empty DataFrame to hold all merged data
df_all = pd.DataFrame()

directory = '/home/ugrads/majors/jenniferchandran/EAGERDataCleanup/2019'

count = 0
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        # Load the file
        df = pd.read_csv(os.path.join(directory, filename))  # File without latitude and longitude
        
        # Clean up the destination column
        df['Destination'] = df['Destination'].apply(clean_abbreviations).apply(rmve_punc).apply(lower_case)
        # Merge the file with the constant file
        merged = pd.merge(df, df_constant[['Destination', 'Latitude', 'Longitude', 'State']], on='Destination', how='left')


        num_matches = merged['Latitude'].notnull().sum()
        merged['Total Shelters'] = num_matches
        count = count + 1
        merged['Person'] = count
        print(f'Number of matches found: {num_matches} {count}')

        # Append the merged data to df_all
        df_all = pd.concat([df_all, merged], ignore_index=True)


df_all = df_all.dropna(subset=['Latitude', 'Longitude'])

# Count occurrence of each shelter (based on 'Destination')
df_all['Occurrence'] = df_all.groupby('Destination')['Destination'].transform('count')

# Rank these occurrences
df_all['Rank'] = df_all['Occurrence'].rank(ascending=False, method='min')

# Sort df_all based on this rank
df_all.sort_values('Rank', inplace=True)

# Save the updated merged data frame to a new Excel file
df_all.to_excel('merged_with_rank.xlsx', index=False)

