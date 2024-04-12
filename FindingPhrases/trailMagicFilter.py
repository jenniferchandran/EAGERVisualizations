import pandas as pd
import os
import string 
#use NLTK library -- use str.lower()

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

# Load the constant Excel file
df_constant = pd.read_excel('fileWith.xlsx')  # File with latitude and longitude

# Rename the 'shelter name' column in df_constant to 'destination' so it matches the other files
df_constant.rename(columns={'Shelter Name': 'Destination'}, inplace=True)
df_constant['Destination'] = df_constant['Destination'].apply(clean_abbreviations).apply(rmve_punc).apply(lower_case)

# Initialize an empty DataFrame to hold all merged data
df_all = pd.DataFrame()

directory = '/home/ugrads/majors/jenniferchandran/EAGERDataCleanup/2023-v2'


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

# Filter rows based on the content of the "Journal Story" column"
search_phrases = ["trail magic", "Trail Magic", "trail angels", "Trail Angels", "trail angel", "Trail Angel", "magic", "angel", "fest", "festival", "trail festival", "tramily", "trail family", "hostel", "event"]
df_all = df_all[df_all['Journal Story'].str.contains('|'.join(search_phrases), na=False, case=False)]

# Drop rows where either Latitude or Longitude is missing
df_all = df_all.dropna(subset=['Latitude', 'Longitude'])

category_dict = {
    "trail magic": ["trail angel", "trail magic", "Trail Magic", "trail angels", "Trail Angels", 
                    "trail angel", "Trail Angel", "magic", "angel", "Magic", "Angel"],
    "event": ["fest", "festival", "trail festival", "event", "trail fest", "Trail fest", 
              "Fest", "Festival", "Trail festival", "Event"], 
    "tramily": ["tramily", "trail family", "family", "trail families", "tramilies", 
                "Tramily", "Trail family", "Family", "Trail families", "Tramilies"], 
    "hostel": ["hostel", "Hostel", "hostels", "Hostels"],
}

def find_phrase(text):
    categories = []  # Use a list instead of a set to allow duplicates
    for category, phrases in category_dict.items():
        for phrase in phrases:
            if phrase.lower() in text.lower():
                categories.append(category)  # Append the category for every occurrence
    return ', '.join(categories)

df_all['phrase'] = df_all['Journal Story'].apply(find_phrase)


df_all.to_excel('magicFiltered.xlsx', index=False)