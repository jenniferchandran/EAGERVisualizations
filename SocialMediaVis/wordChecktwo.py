from fuzzywuzzy import fuzz
import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('motherSmall.csv')

# Define a mapping of keywords to their variations
keywords = {
    "Fest": ["Fest", "Festival", "Feste", "Trail Fest", "Trail Festival", "trailfest", "Trailfest"],
    "Event": ["Event", "Events"],
    "Magic": ["Magic", "trail angel", "trail magic", "Trail Magic", "trail angels", "Trail Angels", 
                    "trail angel", "Trail Angel", "magic", "angel", "Magic", "Angel", "trailangel", "trailmagic", "TrailAngels", "TrailMagic"],
    "Tramily": ["Tramily", "Trailfamily", "trailfamily", "trail family", "Trail family", "trailfamilies", "Trailfamilies"],
    "Hostel": ["Hostel", "Hostels", "hostel", "hostels"],
    "Shelter": ["Shelter", "Shelters", "shelter", "shelters"],
    "Family": ["Family", "Fam", "Families", "families", "fam"],
    "Friend": ["Friend", "Friends", "Friendship"]
}

MIN_SCORE = 80


# Function to count occurrences of similar keywords in the two columns
def count_keyword_occurrences(row, keyword_variations):
    tags = str(row['Journal Story']).lower()
    count = 0
    for variation in keyword_variations:
        # Using token_set_ratio for more flexible matching
        if (fuzz.token_set_ratio(tags, variation.lower()) > MIN_SCORE):
            count += 1
    return count

# Create a new column for each keyword with the count of occurrences
for keyword, variations in keywords.items():
    df[keyword + '_Count'] = df.apply(count_keyword_occurrences, axis=1, args=(variations,))

# Keep only the required columns
columns_to_keep = ['Hiker trail name', 'Year', 'Journal Story', 'Latitude', 'Longitude', 'State', 'state_added', 'Trail club', 'Acronym', 'emotion_label'] + [k + '_Count' for k in keywords]
df = df[columns_to_keep]

# Save the updated DataFrame to a new CSV file
df.to_csv('mother_tester.csv', index=False)