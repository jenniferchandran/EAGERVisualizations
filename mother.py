import os
import pandas as pd
from utility.util import *


def load_raw_data_to_df(directory_path):
    file_names = os.listdir(directory_path)

    xlsx_file_names = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f)) and f.endswith(".xlsx")
    ]

    full_df = pd.DataFrame()
    for filename in xlsx_file_names:
        data = pd.read_excel(directory_path + "/" + filename)
        data["year"] = int(filename.split(".")[0])
        if filename == "2016.xlsx":
            data.rename(columns={"Date": "date"}, inplace=True)
        full_df = pd.concat([full_df, data])

    return full_df


def update_lat_lon_day_month_in_df(df, sensitivity):
    df["day"] = df["date"].apply(get_day_from_date)
    df["month"] = df["date"].apply(get_month_from_date)

    df = update_locations(df, sensitivity)
    df["Longitude"] = df["Longitude"].apply(
        lambda x: float(x) if not contains_alpha(x) else -1
    )
    df["Latitude"] = df["Latitude"].apply(
        lambda x: float(x) if not contains_alpha(x) else -1
    )
    return df


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
# print(raw_df)
print("starting to update lat lon day month")
full_df = update_lat_lon_day_month_in_df(raw_df, 95)
print("finished updating lat lon day month")
# print(full_df)

print("starting to add density")
add_density(full_df, 10)
print("finished adding density")
print(full_df)

# print the unique densities
print(full_df["density"].unique())
# print the number of rows that dont have -1 for day
print(len(full_df[full_df["day"] != -1]))