import time
from thefuzz import fuzz
from thefuzz import process
import pandas as pd
import json
import os

exclude_words = [
    "shelter",
    "shelters",
    "SHELTER",
    "sheltered",
    "Shelter",
    "Shelters",
    "SHELTERED",
    "SHELTERS",
]

my_data = json.load(open("weather_data.json"))


def custom_scorer(s1, s2):
    s1_tokens = [token for token in s1.split() if token not in exclude_words]
    s2_tokens = [token for token in s2.split() if token not in exclude_words]
    return fuzz.token_set_ratio(s1_tokens, s2_tokens)


# load the shelter_data.json file as a dictionary
shelter_data = json.load(open("inputData/shelter_data.json"))


# opent the sentiment_full.xlsx file and load it as a pd dataframe
sentiment_df = pd.read_excel("sentiment_full.xlsx")

count = 0
total = 0
already_had = 0
# loop over all the rows in the sentiment_df
for index, row in sentiment_df.iterrows():
    destination = row["Destination"]
    print("total = ", total)
    # add logic its Hiker Journal Link" is in my_data, then check to see if the longitude row has information that isnt "" or is empty, if it doesnt, update it
    if row["Hiker Journal Link"] in my_data:
        # check to see if the latitude and longitude data in row we are on is nan or none or empty
        if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
            print(
                f'null lat and lon at {destination}, lat = {row["Latitude"]}, lon = {row["Longitude"]}'
            )
            print(f"keys in map = {my_data[row['Hiker Journal Link']].keys()}")
            if "lat" in my_data[row["Hiker Journal Link"]]:
                row["Latitude"] = my_data[row["Hiker Journal Link"]]["lat"]
                row["Longitude"] = my_data[row["Hiker Journal Link"]]["lon"]
                already_had += 1
        else:
            print(
                f"1 already had longitude and latitude info at {destination}, lat = {row['Latitude']}, lon = {row['Longitude']}"
            )

    if (
        not destination
        or destination == "viewentry"
        or destination == ""
        or destination == "view entry"
        or type(destination) != str
    ):
        print(f"bad destination name = {destination}")
        continue

    # use pandas to check to see if the longitude row has information that isnt "" or is empty
    if pd.notna(row["Longitude"]) and row["Longitude"] != "":
        print(
            f"2 already had longitude and latitude info, lat = {row['Latitude']}, lon = {row['Longitude']}, at destination = {destination} "
        )
        continue

    print(
        f"destination = {destination}, longitude = {row['Longitude']}, latitude = {row['Latitude']}"
    )
    total += 1

    best_match, score = process.extractOne(
        destination, shelter_data.keys(), scorer=custom_scorer
    )
    print(f"original destination = {destination}, best_match = {best_match}, score = {score}")
    # print(
    #     f"actual destination = {destination}, best_match = {best_match}, score = {score}"
    # )

    if score >= 87:
        print("update!")
        print("")
        print("")
        print("")
        row["Latitude"] = shelter_data[best_match]["cordinates"]["latitude"]
        row["Longitude"] = shelter_data[best_match]["cordinates"]["longitude"]
        count += 1

# convert this dataframe to an excel file named sentiment_full_updated_with_coords.xlsx
sentiment_df.to_excel("sentiment_full_updated_with_coords.xlsx")
print(
    f"count = {count}, percentage updated total = {count / len(sentiment_df)}, percentage of nulls updated = {count / total} , already updated {already_had}"
)
