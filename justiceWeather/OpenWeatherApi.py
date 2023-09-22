import datetime
import os
import time
import requests
import json
import pandas as pd
from testingAPIKeyValidity import testKeys


# remove all spaces from a string then make it lowercase
def removeSpaces(string):
    string = string.lower()
    return string


def convertDateToTimestamp(date, currYear):
    date = date.split(",")
    date = date[0].split(" ")
    month = date[0]
    monthNum = None
    day = date[1]
    if month == "Jan":
        monthNum = 1
    elif month == "Feb":
        monthNum = 2
    elif month == "Mar":
        monthNum = 3
    elif month == "Apr":
        monthNum = 4
    elif month == "May":
        monthNum = 5
    elif month == "Jun":
        monthNum = 6
    elif month == "Jul":
        monthNum = 7
    elif month == "Aug":
        monthNum = 8
    elif month == "Sep":
        monthNum = 9
    elif month == "Oct":
        monthNum = 10
    elif month == "Nov":
        monthNum = 11
    elif month == "Dec":
        monthNum = 12
    else:
        print("Error: month is not in the range of Jan-Dec")
        return -1

    try:
        day = int(day)
        # add checking to the range of day to make sure its valid for its month
        if month in "JanMarMayJulAugOctDec":
            if day > 31:
                print("Error: day is not in the range of 1-31")
                return -1
        elif month in "AprJunSepNov":
            if day > 30:
                print("Error: day is not in the range of 1-30")
                return -1
        elif month == "Feb":
            if day > 28:
                print("Error: day is not in the range of 1-28")
                return -1

    except:
        print("Error: day is not an int")
        return -1

    return int(datetime.datetime(currYear, monthNum, day).timestamp())


def save_data_to_json(data):
    with open("weather_data.json", "w") as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


# TODO add more api keys
preTestapiKeys = [
    "5bf8cd2a704c0c7027c23cf77acb79cb",
    "a43e4fa8f4893126918b75676cd106e6",
    "f6f90fd57e86f923624b9cef75cb1d94",
    "baf1e9f73dc9484ae19490582c19099d",
    "dd903cc2648b50119e69dfcfd00c8a7f",
    "059af59e7405830b0365c9fa623335e6",
    "d630ce2596a01ed25c9c92efa16b02bb",
]

postTestAPIKeys = testKeys(preTestapiKeys)


def main(apiKeys):
    try:
        apiKey = apiKeys.pop()

        print("READ THIS ABOVE ^^^^^^^^^^^^^^^^^^^^^^")
        time.sleep(1)
        print("sleep over")

        file_paths = [
            "2016.xlsx",
            "2017.xlsx",
            "2018.xlsx",
            "2019.xlsx",
            "2020.xlsx",
            "2021.xlsx",
        ]

        # open the file shelter_data.json and convert it into a python dictionary
        print("Loading shelter data...")
        with open("shelter_data.json") as json_file:
            shelter_data = json.load(json_file)
        print("Shelter data loaded.")

        keys = shelter_data.keys()
        newDict = {}
        for shelter in shelter_data:
            newDict[removeSpaces(shelter)] = shelter_data.get(shelter)

        # create a dataframe from the excel file using pandas using the array of file_paths and add a new column to each row called year and input the year (which is the name of the excel file) into the year column so that we know what year each entry is in as our current date column just gives the month and day and not year
        df = pd.DataFrame()
        print("Loading excel files...")
        for file_path in file_paths:
            data = pd.read_excel(file_path)
            data["year"] = file_path.split(".")[0]
            df = pd.concat([df, data])
            if file_path == "2016.xlsx":
                df.rename(columns={"Date": "date"}, inplace=True)
        print("Excel files loaded.")

        # # loop through all the rows in the excel file, if the destination is in the dictionary then add the longitude and latitude to the row, if added print the destination and the longitude and latitude
        for index, row in df.iterrows():
            if row["Destination"] in newDict:
                df.loc[index, "longitude"] = newDict[row["Destination"]]["cordinates"][
                    "longitude"
                ]
                df.loc[index, "latitude"] = newDict[row["Destination"]]["cordinates"][
                    "latitude"
                ]

            # add that if there are none null values in the Longitude and Latitude columns then add them to the longitude and latitude column, case maters
            elif (
                pd.notnull(row["Longitude"])
                and pd.notnull(row["Latitude"])
                and row["Destination"] not in keys
            ):
                df.loc[index, "longitude"] = row["Longitude"]
                df.loc[index, "latitude"] = row["Latitude"]

        # load the weather_data.json file as a dictionary
        with open("weather_data.json") as json_file:
            weather_data = json.load(json_file)  # load the json file as a dictionary
        # clear terminal
        os.system("clear")
        # print in a pretty way the total number of entries in the weather data dictionary
        print(f"Total number of entries in weather_data.json: {len(weather_data)}")
        # print in a pretty way the total number of entries in the df with a longitude and latitude that are not null and that have unique hikre journal links
        print(
            f"Total number of entries in df with a longitude and latitude that are not null and that have unique hiker journal links: {len(df[df['longitude'].notnull()]['Hiker Journal Link'].unique())}"
        )
        time.sleep(5)

        totalCount = 0
        count = 0
        alreadyCounted = 0
        invalid = 0
        # # print the entire frames column names and row count
        # print(df.columns)
        # print("df longitude == ")
        # print("")
        # print("")
        # print(df["longitude"])
        # print(len(df))
        # # print the number of rows with a longitude and latitude that are not null
        # print(len(df[df["longitude"].notnull()]))
        # # rename the "Date" row in the df to "date"
        # print(df.columns)
        # time.sleep(10)

        # # loop through all the rows in the data frame, if the longitude and latitude are not null then add the weather data to the weather_data dictionary, using the openweather api, if added print the destination and the weather data, use the time from the excel file
        for index, row in df.iterrows():
            if (count + alreadyCounted + invalid) % 100 == 0:
                # clear the
                os.system("clear")
                print("")
                print("")
                print("")
                print("")
                print("")
                print("")
                print("")
                print("")
                print("")
                # print a message that shows all the releveant information about the current state of the program
                print(
                    f"Working on file {totalCount + count} entries in, we've already counted {alreadyCounted} entries"
                )
                # calculate the percentage of the current file that has been processed by totalCount + (len of weather dictionary) by the length of all entreis in the df that have a longitude and latitude
                print(
                    f"Percentage of current file processed: {round((totalCount + count + len(weather_data)) / len(df[df['longitude'].notnull()]), 2) * 100}%"
                )
                print("READ THIS ABOVE ^^^^^^^^^^^^^^^^^^^^^^")
                print("")
                print("")
                print("")
                print("")
                print("")

            if count == 990:
                print(f"NEW KEY!, -> {apiKey} was used up")
                if len(apiKeys) == 0:
                    print("Error: no more api keys")
                    break
                apiKey = apiKeys.pop()
                print(f"NEW KEY!, -> {apiKey} is now being used")
                totalCount += count
                count = 0
            if (
                pd.notnull(row["longitude"])
                and pd.notnull(row["latitude"])
                and row["Hiker Journal Link"] not in weather_data
            ):
                # if row["date"] does not follow the pattern that looks like this Apr 15, Fri then skip this row also add a check if row["date"] is nan
                if pd.isnull(row["date"]):
                    print(
                        f"Error: date is nan at {row['Hiker Journal Link']} in year {row['year']}"
                    )
                    continue
                if len(row["date"].split(",")) != 2:
                    print(
                        f"Error: date is not in the correct format found at -> {row['Hiker Journal Link']}"
                    )
                    continue
                dt = convertDateToTimestamp(row["date"], int(row["year"]))

                if dt == -1:
                    print("Error: dt is -1")
                    continue

                # create a try catch block for this api call, if it fails then print the error and continue if the error from the api is that the key is not authroized, printa  special message then break
                try:
                    package = requests.get(
                        f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={row['latitude']}&lon={row['longitude']}&dt={dt}&appid={apiKey}&units=imperial"
                    )
                except Exception as e:
                    print("Error: api call failed with some exception")
                    print(e)
                    print(f"latitude = {row['latitude']}")
                    print(f"longitude = {row['longitude']}")
                    print(f"dt = {dt}")
                    # print the date time toa human readble format
                    print(datetime.datetime.fromtimestamp(dt))
                    print(f"apiKey = {apiKey}")
                    print(f"row['Hiker Journal Link'] = {row['Hiker Journal Link']}")
                    time.sleep(10)

                    continue
                if package.status_code == 429:
                    print(
                        "Error: api call failed with error code: "
                        + str(package.status_code)
                    )
                    print(f"curr API Key = {apiKey}")
                    print(package.json())
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    if len(apiKeys) == 0:
                        print("Error: no more api keys")
                        break
                    apiKey = apiKeys.pop()
                    continue
                elif package.status_code != 200 and package.status_code != 429:
                    print(
                        "Error: api call failed with error code: "
                        + str(package.status_code)
                    )
                    print(f"curr API Key = {apiKey}")
                    print(package.json())
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    continue

                weather_data[row["Hiker Journal Link"]] = package.json()
                weather_data[row["Hiker Journal Link"]]["Destination"] = row[
                    "Destination"
                ]
                weather_data[row["Hiker Journal Link"]]["date"] = (
                    row["date"] + f", {row['year']}"
                )

                print(package.json())

                count += 1

            if pd.notnull(row["longitude"]) and pd.notnull(row["latitude"]):
                alreadyCounted += 1
            else:
                invalid += 1

        if count != 990:
            print("")
            print("")
            print("")
            print("")
            print("")
            print("")
            print(
                f"Finished file {totalCount} entries in, we've already counted {alreadyCounted} entries"
            )

        # print something showing how many entires were counted and how many were already counted
        print("")
        print("")
        print("")
        print("")
        print("")
        print("")
        print(
            f"Finished file {totalCount} entries in, we've already counted {alreadyCounted} entries"
        )

        # # save the infomration to a json file
        with open("weather_data.json", "w") as outfile:
            json.dump(weather_data, outfile, indent=4, sort_keys=True)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Saving data to JSON...")
        save_data_to_json(weather_data)
        print("Data saved to weather_data.json.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Saving data to JSON before exiting...")
        save_data_to_json(weather_data)
        print("Data saved to weather_data.json.")
        raise  # Re-raise the exception to terminate the program


main(postTestAPIKeys)
