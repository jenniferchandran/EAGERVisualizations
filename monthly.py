import pandas as pd

def no_spaces(s):
    if isinstance(s, str):
        s = s.replace(' ', '')
    return s 

def clean_abbreviations(s):
    if isinstance(s, str):
        s = s.replace('Sen', 'Sep')
        return s
# Read the .xlsx file
file_name = 'merged_with_rank.xlsx'
df = pd.read_excel(file_name)

df['date'] = df['date'].apply(clean_abbreviations).apply(no_spaces)

def extract_month(date_str):
    # Slice the string to obtain the first 3 characters which represent the month
    return date_str[:3]

# Apply the function to the "date" column
df['date'] = df['date'].apply(extract_month)

# Save the modified dataframe to a new .xlsx file
output_file_name = 'modified_file.xlsx'
df.to_excel(output_file_name, index=False)