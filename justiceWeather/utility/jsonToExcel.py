# create a program that opens the weather_data.json file and then creates a new excel file and writes the data to it, that excel file will take all the information from the base 2016, 2017, 2018 excel files and add new columns to the entries based on the hiker journal link as the key identifier, then it will add new columbs that hold the weatehr data
import time
import pandas as pd
import json

folderPath = "input_files/"
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

# open the excel files and add new columns to hold all the information present in the weather_data.json file
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

count = 0
# loop over the df and add the weather data to the new columns, using the information in teh weather_data dictioanry
print("Adding weather data...")
for index, row in df.iterrows():
    if row["Hiker Journal Link"] in weather_data:
        try:
            df.at[index, "clouds"] = weather_data[row["Hiker Journal Link"]]["data"][0][
                "clouds"
            ]
            # print(
            #     str(weather_data[row["Hiker Journal Link"]]["data"][0]["clouds"])
            #     + f" -> {row['Hiker Journal Link']}"
            # )
            count += 1
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
        # print the progress
        if index % 100 == 0:
            # clear terminal
            print(f"{index} rows processed.")
print("Weather data added.")
print(f"{count} rows had weather data added to them.")

# split the df into 8 different dfs, one for each year
print("Splitting df into 6 dfs...")
df_2016 = df[df["year"] == "2016"]
df_2017 = df[df["year"] == "2017"]
df_2018 = df[df["year"] == "2018"]
df_2019 = df[df["year"] == "2019"]
df_2020 = df[df["year"] == "2020"]
df_2021 = df[df["year"] == "2021"]
df_2022 = df[df["year"] == "2022"]
df_2023 = df[df["year"] == "2023"]


# clean each dataframe removing any rows any null instances of longitude, latitude, temperature, and remove the year column
print("Cleaning dfs...")
df_2016 = df_2016.dropna(subset=["Longitude", "Latitude", "temp"])
# drop any row that has an empty value for temp
df_2016 = df_2016[df_2016["temp"] != ""]
df_2016 = df_2016.drop(columns=["year"])
df_2017 = df_2017.dropna(subset=["Longitude", "Latitude", "temp"])
df_2017 = df_2017[df_2017["temp"] != ""]
df_2017 = df_2017.drop(columns=["year"])
df_2018 = df_2018.dropna(subset=["Longitude", "Latitude", "temp"])
df_2018 = df_2018.drop(columns=["year"])
df_2018 = df_2018[df_2018["temp"] != ""]
df_2019 = df_2019.dropna(subset=["Longitude", "Latitude", "temp"])
df_2019 = df_2019.drop(columns=["year"])
df_2019 = df_2019[df_2019["temp"] != ""]
df_2020 = df_2020.dropna(subset=["Longitude", "Latitude", "temp"])
df_2020 = df_2020.drop(columns=["year"])
df_2020 = df_2020[df_2020["temp"] != ""]
df_2021 = df_2021.dropna(subset=["Longitude", "Latitude", "temp"])
df_2021 = df_2021.drop(columns=["year"])
df_2021 = df_2021[df_2021["temp"] != ""]
df_2022 = df_2022.dropna(subset=["Longitude", "Latitude", "temp"])
df_2022 = df_2022.drop(columns=["year"])
df_2022 = df_2022[df_2022["temp"] != ""]
df_2023 = df_2023.dropna(subset=["Longitude", "Latitude", "temp"])
df_2023 = df_2023.drop(columns=["year"])
df_2023 = df_2023[df_2023["temp"] != ""]
print("Dfs cleaned.")


# print out the name of each columb in df_2016
print("Printing column names...")
for col in df_2016.columns:
    print(col)
time.sleep(5)


# # save each dataframe to a new excel file
# print("Saving dfs to excel files...")
df_2016.to_excel(folderPath + "2016_weather.xlsx", index=False)
df_2017.to_excel(folderPath + "2017_weather.xlsx", index=False)
df_2018.to_excel(folderPath + "2018_weather.xlsx", index=False)
df_2019.to_excel(folderPath + "2019_weather.xlsx", index=False)
df_2020.to_excel(folderPath + "2020_weather.xlsx", index=False)
df_2021.to_excel(folderPath + "2021_weather.xlsx", index=False)
df_2022.to_excel(folderPath + "2022_weather.xlsx", index=False)
df_2023.to_excel(folderPath + "2023_weather.xlsx", index=False)

print("All dfs saved to excel files.")
