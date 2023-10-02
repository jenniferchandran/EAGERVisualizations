import json
import os
import time
import pandas as pd
from shapely.geometry import shape, Point

# Describe what this code does
# This code takes in a .csv file and adds a column for latitude, longitude, and state, to make it congruent with the other .xlsx files
# It then saves the .csv file as an excel file


# Replace with the path to your U.S. States GeoJSON file
geojson_path = "inputData/us-states.json"

# Load the GeoJSON data
with open(geojson_path, "r") as f:
    geojson_data = json.load(f)

# Initialize a geocoder


def get_state(longitude, latitude):
    point = Point(longitude, latitude)
    for feature in geojson_data["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            return feature["properties"]["NAME"]
    return None


def removeSpaces(string):
    string = string.lower()
    return string


years = ["2022", "2023"]
relative_file_path = "inputData/"


# open the inputData/2019.xlsx file and print out the column names
excel = pd.read_excel("inputData/2021.xlsx")
# print(len(excel.columns))
# print 10 new lines
print("\n")

# open the shelter_data.json file and make a python dictionary called shelters
with open("inputData/shelter_data.json") as json_file:
    shelter_data = json.load(json_file)

shelters = {}
for shelter in shelter_data:
    shelters[removeSpaces(shelter)] = shelter_data.get(shelter)


# print the keys of the shelters dictionary in a pretty way
# print(json.dumps(shelters, indent=4, sort_keys=True))

for year in years:
    df = pd.DataFrame()
    file_path = relative_file_path + f"{year}_csv/"
    count = 0
    # loop over every .csv file in the file path directory
    for file in os.listdir(file_path):
        if file.endswith(".csv"):
            # read the .csv
            csv_file = pd.read_csv(file_path + file)
            print(f"file: {file}\n")
            if "Destination" not in csv_file.columns:
                break
            csv_file["Destination"] = csv_file["Destination"].str.lower()
            count += len(csv_file)
            # print the columns in the .csv
            # print(csv_file.columns)
            # add a column to the .csv named "Latitude"
            csv_file["Latitude"] = ""
            # add a column to the .csv named "Longitude"
            csv_file["Longitude"] = ""
            # add a column to the .csv named "State"
            csv_file["State"] = ""
            # add a column to the .csv named "Total Shelters"
            csv_file["Total Shelters"] = ""
            # add a column to the .csv named "Person #
            csv_file["Person #"] = ""

            # print(csv_file)
        df = pd.concat([df, csv_file])
    stateCount = 1
    for index, row in df.iterrows():
        if row["Destination"] in shelters:
            long, lat = (
                shelters[row["Destination"]]["cordinates"]["longitude"],
                shelters[row["Destination"]]["cordinates"]["latitude"],
            )
            df.loc[index, "Longitude"] = long
            df.loc[index, "Latitude"] = lat
            df.loc[index, "State"] = get_state(long, lat)
            # print what row we are on, and what percentage of the df we have gone through
            print(f"iteration: {stateCount}, {round(stateCount/len(df)*100, 2)}%")
        stateCount += 1
        # print the location, the longitude, and the latitude
        # print(
        #     f"{row['Destination']} is located at {df.loc[index, 'Latitude']}, {df.loc[index, 'Longitude']}"
        # )

    print(df.columns)
    print(f"Number of .csv files: {count}, number of rowns in df: {len(df)}")

    # print the number of rows that have longitude and latitude that are not empty
    print(f"Number of rows with longitude and latitude: {len(df[df['Longitude'] != ''])}")
    # print 5 random lines of the df
    print(df.sample(5))
    # make new file called {year}.xlsx that saves the df, do not save the index
    df.to_excel(f"inputData/{year}.xlsx", index=False)
