import pandas as pd

def most_used_phrase(data_files, location_file):
    # Initialize an empty dataframe to store combined data
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
    
    # Define category mapping
    categories = {
       "trail magic": ["trail angel", "trail magic", "Trail Magic", "trail angels", "Trail Angels", 
                    "trail angel", "Trail Angel", "magic", "angel", "Magic", "Angel"],
        "event": ["fest", "festival", "trail festival", "event", "trail fest", "Trail fest", 
              "Fest", "Festival", "Trail festival", "Event"], 
        "tramily": ["tramily", "trail family", "family", "trail families", "tramilies", 
                "Tramily", "Trail family", "Family", "Trail families", "Tramilies"], 
        "hostel": ["hostel", "Hostel", "hostels", "Hostels"],
    }
    
    # Map the phrases to categories
    def categorize(phrase):
        for category, phrases in categories.items():
            if phrase.lower() in phrases:
                return category
        return phrase

    df_exploded['category'] = df_exploded['phrase'].apply(categorize)
    
    # Group by State and category and get count
    statewise_counts = df_exploded.groupby(['State', 'category']).size().unstack(fill_value=0).reset_index()

    # Filter for only the specified columns and reorder
    statewise_counts = statewise_counts[['State', 'trail magic', 'event', 'tramily', 'hostel']]
    
    # Write the second output to a new .xlsx file
    statewise_counts.to_excel('statePhrases.xlsx', index=False, engine='openpyxl')

# Call the function
most_used_phrase(['clubPhrases2019.xlsx','clubPhrases2020.xlsx', 'clubPhrases2021.xlsx', 'clubPhrases2022.xlsx', 'clubPhrases2023.xlsx'], 'combinedCoords.xlsx')
