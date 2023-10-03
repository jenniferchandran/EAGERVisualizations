import datetime
import json
import pandas as pd

weather_data = json.load(open("weather_data.json"))
complete_data = []
for key, value in weather_data.items():
    year = value["date"].split(", ")[2]
    if "lon" in value and year in "20162017201820192020202120222023":
        complete_data.append(
            {
                "lon": value["lon"],
                "lat": value["lat"],
                "temp": value["data"][0]["temp"],
                "date": value["date"],
                "link": key,
                "year": int(year),
            }
        )
weather_data_df = pd.DataFrame(complete_data)
# print(weather_data_df.columns)


def monthToNum(shortMonth):
    return {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }[shortMonth]


def numTofullMonthName(num):
    return {
        1: "January",
        2: "Febuary",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "Augest",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }[num]


def getWeatherDataWthinNMiles(key, radius_miles):
    # Convert miles to degrees (roughly, considering Earth's radius)
    degrees_per_mile = 1 / 69  # Approximately
    radius_deg = radius_miles * degrees_per_mile

    target_lon = weather_data[key]["lon"]
    target_lat = weather_data[key]["lat"]

    # Calculate latitude and longitude bounds for the square around the target point
    min_lon = target_lon - radius_deg
    max_lon = target_lon + radius_deg
    min_lat = target_lat - radius_deg
    max_lat = target_lat + radius_deg

    # Filter the DataFrame to get entries within the specified latitude and longitude bounds
    filtered_df = weather_data_df[
        (weather_data_df["lon"] >= min_lon)
        & (weather_data_df["lon"] <= max_lon)
        & (weather_data_df["lat"] >= min_lat)
        & (weather_data_df["lat"] <= max_lat)
    ]

    return filtered_df


# convert a string date to a datetime object when string looks like Jun 20, Tue, 2017
def convertStringDateToDatetimeObject(date):
    if isinstance(date, pd.Series):
        # If the input is a pandas Series, apply the function to each element of the Series
        return date.apply(convertStringDateToDatetimeObject)
    else:
        # print(date)
        # print(type(date))
        # print("")
        # print("")
        # print("")
        year = int(date.split(", ")[2])
        date = date.split(",")
        date = date[0].split(" ")
        month = date[0]
        monthNum = monthToNum(month)
        day = date[1]
        if monthNum == -1:
            print("Error: month is not a string")
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

        return datetime.datetime(year, monthNum, day)


def filterWeatherDataWithinNWeeks(inputData, key, n):
    # get the date of the key
    date = weather_data[key]["date"]
    # convert date which is a string that looks like "Sep 10, Sun, 2023" to a datetime object
    date = convertStringDateToDatetimeObject(date)

    # find the date of n weeks before the date of the key
    # print(
    #     type(date), date, type(datetime.timedelta(weeks=n)), datetime.timedelta(weeks=n)
    # )
    n_weeks_before_date = date - datetime.timedelta(weeks=n)
    # print(n_weeks_before_date.strftime("%b %d, %a, %Y"))
    # find the date of n weeks after the date of the key
    n_weeks_after_date = date + datetime.timedelta(weeks=n)

    # filter the weather data to only include data within the range of n weeks before and after the date of the key
    filtered_df = inputData[
        (convertStringDateToDatetimeObject(inputData["date"]) >= n_weeks_before_date)
        & (convertStringDateToDatetimeObject(inputData["date"]) <= n_weeks_after_date)
    ]

    return filtered_df


# this method should get all the weather data for in a n mile radius of the given key, within +- 1 week of the given key, and output the delta of the temperateure at that key by averaging the temperature of all the data points in the 10 mile radius
def getDeltaTemp(key, nMiles, nWeeks):
    n_mile_data = getWeatherDataWthinNMiles(key, nMiles)

    n_week_data = filterWeatherDataWithinNWeeks(n_mile_data, key, nWeeks)

    avg_temp = n_week_data["temp"].mean()

    target_temp = weather_data[key]["data"][0]["temp"]

    return target_temp - avg_temp


def generateData(nMiles, nWeeks):
    # create a map that just has the data for the entire month of april in 2017 from our weather_data dictionary that contains only 3 things, the longitude, latitude, and temperature
    data_list = {}

    counter = 0
    # make final count the number of entries in weather_data that have a year >= 2020
    final_count = len(weather_data_df)
    for key, value in weather_data.items():
        year = value["date"].split(", ")[2]
        month = value["date"].split(", ")[0].split(" ")[0]
        if counter % 500 == 0:
            # print it as a percentage
            print(f"{counter/final_count*100}%, counter: {counter}")
        if "lon" in value and year in "20162017201820192020202120222023":
            data_list[key] = {
                "lon": value["lon"],
                "lat": value["lat"],
                "deltaTemp": getDeltaTemp(key, nMiles, nWeeks),
                "year": int(year),
                "month": monthToNum(month),
                "Hiker Journal Link": key,
            }

        counter += 1

    return data_list


# Create a DataFrame from the filtered data
# make it so this data generation only happens once and not every time while the app is running
milesSearching = 20
weeksSearching = 1
data_dict = generateData(milesSearching, weeksSearching)
output_data = {"miles": milesSearching, "weeks": weeksSearching, "data": data_dict}
input_folder = "inputData/"
# make a variable called info that has the info {month}_{day}_{hour}_{minute}
info = datetime.datetime.now().strftime("%m_%d_%H_%M")
name_of_file = f"deltaTempData_{info}.json"
final_file_name = input_folder + name_of_file
# dump the data in the converted data dataframe into a json file named {final_file_name}, they key of the json should be the journal link, and the values should be a dict that holds the rest of the info
with open(final_file_name, "w") as outfile:
    json.dump(output_data, outfile, indent=4, sort_keys=True)
