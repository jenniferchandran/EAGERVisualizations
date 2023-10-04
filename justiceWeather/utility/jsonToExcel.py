# create a program that opens the weather_data.json file and then creates a new excel file and writes the data to it, that excel file will take all the information from the base 2016, 2017, 2018 excel files and add new columns to the entries based on the hiker journal link as the key identifier, then it will add new columbs that hold the weatehr data
import math
import time
import pandas as pd
import json

folderPath = "inputData/"
file_paths = [
    "2016.xlsx",
    "2017.xlsx",
    "2018.xlsx",
    "2019.xlsx",
    "2020.xlsx",
    "2021.xlsx",
    "2022.xlsx",
    "2023.xlsx",
]

# open the json file
with open("weather_data.json") as json_file:
    weather_data = json.load(json_file)

for key in list(weather_data.keys()):
    if type(weather_data[key]["Destination"]) is float:
        weather_data[key]["Destination"] = "viewentry"

amount_2016 = 0
for key in list(weather_data.keys()):
    year = weather_data[key]["date"].split(", ")[2]
    if year == "2016":
        amount_2016 += 1
print(f"amount of entries in 2016: {amount_2016}")

df = pd.DataFrame()
print("Loading excel files...")
for file_path in file_paths:
    relative_file_path = folderPath + file_path
    data = pd.read_excel(relative_file_path)
    data["year"] = file_path.split(".")[0]
    df = pd.concat([df, data])
    if file_path == "2016.xlsx":
        df.rename(columns={"Date": "date"}, inplace=True)
print("Excel files loaded.")


# add new columns to the excel files, clouds, dew_point, feels_like, humidity, pressure, sunrise, sunset, temp, weather[0]["description"], weather[0]["main"], wind_deg, wind_speed
print("Adding new columns...")
df["clouds"] = ""
df["dew_point"] = ""
df["feels_like"] = ""
df["humidity"] = ""
df["pressure"] = ""
df["sunrise"] = ""
df["sunset"] = ""
df["temp"] = ""
df["weather_description"] = ""
df["weather_main"] = ""
df["wind_deg"] = ""
df["wind_speed"] = ""
print("New columns added.")

# remove any entires in the weatehr_data dictionary that has a has a key called "cod"
print("Removing entries with cod...")
for key in list(weather_data.keys()):
    if "cod" in weather_data[key]:
        del weather_data[key]
print("Entries with cod removed.")

countsPerYear = [0 for x in range(2016, 2024)]
# loop over the df and add the weather data to the new columns, using the information in teh weather_data dictioanry
print("Adding weather data...")
for index, row in df.iterrows():
    if row["Hiker Journal Link"] in weather_data:
        try:
            df.at[index, "clouds"] = weather_data[row["Hiker Journal Link"]]["data"][0][
                "clouds"
            ]
            yearIdx = int(row["year"]) - 2016
            countsPerYear[yearIdx] += 1
        except Exception as e:
            print("clouds error: ", e)
            print("clouds error: ", row["Hiker Journal Link"])
            time.sleep(5)
        df.at[index, "dew_point"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "dew_point"
        ]
        df.at[index, "feels_like"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "feels_like"
        ]
        df.at[index, "humidity"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "humidity"
        ]
        df.at[index, "pressure"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "pressure"
        ]
        df.at[index, "sunrise"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "sunrise"
        ]
        df.at[index, "sunset"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "sunset"
        ]
        df.at[index, "temp"] = weather_data[row["Hiker Journal Link"]]["data"][0]["temp"]
        df.at[index, "weather_description"] = weather_data[row["Hiker Journal Link"]][
            "data"
        ][0]["weather"][0]["description"]
        df.at[index, "weather_main"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "weather"
        ][0]["main"]
        df.at[index, "wind_deg"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "wind_deg"
        ]
        df.at[index, "wind_speed"] = weather_data[row["Hiker Journal Link"]]["data"][0][
            "wind_speed"
        ]
        df.at[index, "Latitude"] = weather_data[row["Hiker Journal Link"]]["lat"]
        df.at[index, "Longitude"] = weather_data[row["Hiker Journal Link"]]["lon"]
        # print the progress
        if index % 100 == 0:
            # clear terminal
            print(f"{index} rows processed.")
print("Weather data added.")
print(f"{sum(countsPerYear)} rows had weather data added to them.")
# print the array in a nice way
print("Counts per year:")
for i in range(len(countsPerYear)):
    print(f"{2016 + i}: {countsPerYear[i]}")

# split the df into 8 different dfs, one for each year
print("Splitting df into 6 dfs...")
df_2016 = df_2016 = df[
    (df["year"] == "2016") & df["Hiker Journal Link"].isin(weather_data.keys())
]
df_2017 = df[(df["year"] == "2017") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2018 = df[(df["year"] == "2018") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2019 = df[(df["year"] == "2019") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2020 = df[(df["year"] == "2020") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2021 = df[(df["year"] == "2021") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2022 = df[(df["year"] == "2022") & df["Hiker Journal Link"].isin(weather_data.keys())]
df_2023 = df[(df["year"] == "2023") & df["Hiker Journal Link"].isin(weather_data.keys())]


# clean each dataframe removing any rows any null instances of longitude, latitude, temperature, and remove the year column
print("Cleaning dfs...")
# print the amount of rows in df_2016 with null values in temp

df_2016 = df_2016[df_2016["temp"] != ""]
df_2016 = df_2016.drop(columns=["year"])
print(f"length of df_2016 after cleaning: {len(df_2016)}")
df_2017 = df_2017[df_2017["temp"] != ""]
df_2017 = df_2017.drop(columns=["year"])
print(f"length of df_2017 after cleaning: {len(df_2017)}")
df_2018 = df_2018.drop(columns=["year"])
df_2018 = df_2018[df_2018["temp"] != ""]
print(f"length of df_2018 after cleaning: {len(df_2018)}")
df_2019 = df_2019.drop(columns=["year"])
df_2019 = df_2019[df_2019["temp"] != ""]
print(f"length of df_2019 after cleaning: {len(df_2019)}")
df_2020 = df_2020.drop(columns=["year"])
df_2020 = df_2020[df_2020["temp"] != ""]
print(f"length of df_2020 after cleaning: {len(df_2020)}")
df_2021 = df_2021.drop(columns=["year"])
df_2021 = df_2021[df_2021["temp"] != ""]
print(f"length of df_2021 after cleaning: {len(df_2021)}")
df_2022 = df_2022.drop(columns=["year"])
df_2022 = df_2022[df_2022["temp"] != ""]
print(f"length of df_2022 after cleaning: {len(df_2022)}")
df_2023 = df_2023.drop(columns=["year"])
df_2023 = df_2023[df_2023["temp"] != ""]
print(f"length of df_2023 after cleaning: {len(df_2023)}")
print("Dfs cleaned.")


# print out the name of each columb in df_2016
# print("Printing column names...")
# for col in df_2016.columns:
#     print(col)
# time.sleep(5)

outputFolderPath = "weather/"
# # save each dataframe to a new excel file
print("Saving dfs to excel files...")
df_2016.to_excel(outputFolderPath + "2016_weather.xlsx", index=False)
df_2017.to_excel(outputFolderPath + "2017_weather.xlsx", index=False)
df_2018.to_excel(outputFolderPath + "2018_weather.xlsx", index=False)
df_2019.to_excel(outputFolderPath + "2019_weather.xlsx", index=False)
df_2020.to_excel(outputFolderPath + "2020_weather.xlsx", index=False)
df_2021.to_excel(outputFolderPath + "2021_weather.xlsx", index=False)
df_2022.to_excel(outputFolderPath + "2022_weather.xlsx", index=False)
df_2023.to_excel(outputFolderPath + "2023_weather.xlsx", index=False)

print("All dfs saved to excel files.")
