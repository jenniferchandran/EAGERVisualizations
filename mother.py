import os
import pandas as pd
from utility.util import *


# TODO: fix bug that is causing everything from 30k -> end to uncompleted (maybe it is because of the way I am parsing the data)
# TODO: Add years 2013 - 2015
#     - find in google drive
# TODO: add weather data to the dataframe
# TODO: add campsites
# TODO: find katadin
# TODO: what does occurances mean? @Aladdin
#   - Delete Rank and Occurance
# TODO: Rename "label" to emotional label


def update_lat_lon_day_month_in_df(df, sensitivity):
    copyDf = df.copy()
    copyDf["day"] = copyDf["date"].apply(get_day_from_date)
    copyDf["month"] = copyDf["date"].apply(get_month_from_date)

    update_locations(copyDf, sensitivity)
    print(f"number of entries that are -1 {len(copyDf[copyDf['Latitude'] == -1])}")
    copyDf["Longitude"] = copyDf["Longitude"].apply(
        lambda x: float(x) if not contains_alpha(x) else -1
    )
    copyDf["Latitude"] = copyDf["Latitude"].apply(
        lambda x: float(x) if not contains_alpha(x) else -1
    )
    return copyDf


def add_density(df, radius):
    df["density"] = df.apply(
        lambda x: count_entries_within_radius(
            x["Longitude"], x["Latitude"], radius, x["year"], x["month"], df
        ),
        axis=1,
    )


print("starting to load data")
raw_df = load_raw_data_to_df("raw_trail_journal_data/xlsx")
print("finished loading data")


aladdin_df = pd.read_excel("raw_trail_journal_data/Aladdin_data_full.xlsx")

aladdin_df = aladdin_df[
    [
        "Hiker Journal Link",
        "label",
        "Emotion_scores",
        "state_added",
        "Trail club",
        "Acronym",
        "Occurrence",
    ]
]
# print(raw_df)
print("starting to update lat lon day month")
full_df = pd.merge(raw_df, aladdin_df, on="Hiker Journal Link")
full_df = update_lat_lon_day_month_in_df(full_df, 95)
print("finished updating lat lon day month")


# print count of each row that has Latitude == -1
# print(f"number of entries that are -1 {len(full_df[full_df['Latitude'] == -1])}")


print("starting to add density")
add_density(full_df, 10)
print("finished adding density")
# print(full_df)
print(full_df.columns)

# # print the unique densities
# print(full_df["density"].unique())
# print the number of rows that dont have -1 for day
# print(len(full_df[full_df["day"] != -1]))

weather_df = load_weather_data()

merged = merge_weather_data(full_df, weather_df)

# print(merged)

print(merged.columns)

# find the columns that are in either df but not both
print("find ones that in either df but not both")
print(set(full_df.columns).symmetric_difference(set(merged.columns)))

# create a df of rows where the density is not -1 and the wind_speed is not nan
filtered_df = merged[(merged["density"] != -1) & (merged["wind_speed"].notnull())]

# sample = filtered_df.sample(1)

# print out the column name and the value of said column in sample
# for col in sample.columns:
#     print(col, sample[col].values[0])

# find the number of unique Hiker Journal Links in the merged df
# print(merged["Hiker Journal Link"].unique())

print(
    f"as percetange that is {(len(merged['Hiker Journal Link'].unique())/len(merged))*100}"
)

# merged.set_index("Hiker Journal Link").to_json("output.json", orient="index")

# get the current day, month, year using the DT library
day = str(datetime.datetime.now().day)
month = str(datetime.datetime.now().month)
year = str(datetime.datetime.now().year)
minutes = str(datetime.datetime.now().minute)
convert_df_to_xlsx(
    merged, "mother_data_" + day + "_" + month + "_" + year + "_" + minutes
)
