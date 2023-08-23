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

def transform_date(date_str):
    # Create a dictionary for month abbreviations
    month_dict = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    # Extract month abbreviation and day from the string
    month_abbr = date_str[:3]
    day = date_str[3:5]
    
    # Return the date in the "m/d" format
    return f"{month_dict[month_abbr]}/{day}"

# Apply the transformation to the "date" column
df['date'] = df['date'].apply(transform_date)

# Save the modified dataframe to a new .xlsx file
output_file_name = 'modified_file.xlsx'
df.to_excel(output_file_name, index=False)