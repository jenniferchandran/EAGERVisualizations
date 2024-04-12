import pandas as pd

def most_used_phrase(data_files, location_file):
    dfs = []

    # Loop through each data file and read its content into a list of dataframes
    for data_file in data_files:
        df = pd.read_excel(data_file, engine='openpyxl')
        dfs.append(df)

# Concatenate all dataframes in the list
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Read the location .xlsx file
    df_location = pd.read_excel(location_file, engine='openpyxl')
    
    # A function to clean and split the phrases from a cell
    def clean_and_split(phrases):
        return [phrase.strip().lower() for phrase in str(phrases).split(",")]

    # Apply the function to each cell in the 'phrase' column to get a list of phrases
    df['phrase'] = df['phrase'].apply(clean_and_split)
    
    # Explode the dataframe on 'phrase' so that each phrase gets its own row
    df_exploded = df.explode('phrase')
    
    # Group by Region, State, Acronym and get the most common phrase for each group
    result = df_exploded.groupby(['Region', 'State', 'Acronym'])['phrase'].apply(lambda x: x.value_counts().idxmax()).reset_index()
    
    # Merge the result with df_location to get the matching start and end latitudes and longitudes based on Acronym
    merged_result = pd.merge(result, df_location[['Acronym', 'latitude_start', 'longitude_start', 'latitude_end', 'longitude_end']], on='Acronym', how='left')
    
    # Rename columns
    merged_result.rename(columns={'phrase': 'MostUsedPhrase'}, inplace=True)
    
    # Write the result to a new .xlsx file
    merged_result.to_excel('mostUsedClubPhrases.xlsx', index=False, engine='openpyxl')

    # Generating second output
    # Group by State to get the most common phrase and a list of all unique phrases
    statewise_phrases = df_exploded.groupby('State')['phrase'].agg(
        MostUsedPhrase=lambda x: x.value_counts().idxmax(),
        ListOfPhrases=lambda x: ', '.join(sorted(set(x)))
    ).reset_index()
    
    statewise_phrases['NumPhrases'] = statewise_phrases['ListOfPhrases'].apply(lambda x: len(x.split(', ')))

    # Write the second output to a new .xlsx file
    statewise_phrases.to_excel('statePhrases1.xlsx', index=False, engine='openpyxl')

# Call the function
most_used_phrase(['clubPhrases2019.xlsx','clubPhrases2020.xlsx', 'clubPhrases2021.xlsx', 'clubPhrases2022.xlsx', 'clubPhrases2023.xlsx'], 'combinedCoords.xlsx')
