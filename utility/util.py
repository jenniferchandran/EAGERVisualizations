import datetime
import json
import os
from thefuzz import fuzz
from thefuzz import process
import pandas as pd


# TODO fix snow in cleaning weather


def removeSpaces(string):
    string = string.lower()
    return string


def convertDateToTimestamp(date, currYear, Print=False):
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
        if Print:
            print("Error: month is not in the range of Jan-Dec")
        return -1

    try:
        day = int(day)
        # add checking to the range of day to make sure its valid for its month
        if month in "JanMarMayJulAugOctDec":
            if day > 31:
                if Print:
                    print("Error: day is not in the range of 1-31")
                return -1
        elif month in "AprJunSepNov":
            if day > 30:
                if Print:
                    print("Error: day is not in the range of 1-30")
                return -1
        elif month == "Feb":
            if day > 28:
                if Print:
                    print("Error: day is not in the range of 1-28")
                return -1

    except:
        print("Error: day is not an int")
        return -1

    return int(datetime.datetime(currYear, monthNum, day).timestamp())


def fuzzy_match(search_token, reference_set):
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

    def custom_scorer(s1, s2):
        s1_tokens = [token for token in s1.split() if token not in exclude_words]
        s2_tokens = [token for token in s2.split() if token not in exclude_words]
        return fuzz.token_set_ratio(s1_tokens, s2_tokens)

    best_match, score = process.extractOne(
        search_token, reference_set, scorer=custom_scorer
    )

    return best_match, score


def save_dictionary_to_json(dictionary, filename):
    # create a new dictionary that will be returned at the end of the method
    newDict = {}
    # loop through all the keys in the data dictionary
    for key in dictionary:
        # if the value of the key is not none or NaN, add it to the newDict
        if dictionary[key] == None or dictionary[key] == "NaN":
            newDict[key] = "viewentry"
        else:
            newDict[key] = dictionary[key]
    # save the newDict to the weather_data.json file
    with open(f"{filename}.json", "w") as outfile:
        json.dump(newDict, outfile, indent=4, sort_keys=True)


def is_valid_date(date, Print=False):
    if type(date) != str:
        if Print:
            print(f"not a string! -> {date}")
        return False
    if date == "NaN":
        if Print:
            print(f"this string is NaN! -> {date}")
        return False
    date = date.split(" ")
    month = date[0]
    day = date[1]
    day = day[:2]
    if day.isnumeric() == False:
        if Print:
            print(f"this day is not numeric! -> {date} -> {day}")
        return False
    if (
        month
        not in "JanuaryFebruaryMarchAprilMayJuneJulyAugustSeptemberOctoberNovemberDecember"
    ):
        if Print:
            print(f"this month is not valid! -> {date} -> {month}")
        return False
    return True


def get_day_from_date(date):
    if is_valid_date(date) == False:
        return -1
    date = date.split(" ")
    day = date[1]
    day = day[:2]
    return int(day)


def get_month_from_date(date, Print=False):
    if not is_valid_date(date, Print=Print):
        return -1
    date = date.split(" ")
    month = date[0]
    if month == "Jan":
        return 1
    elif month == "Feb":
        return 2
    elif month == "Mar":
        return 3
    elif month == "Apr":
        return 4
    elif month == "May":
        return 5
    elif month == "Jun":
        return 6
    elif month == "Jul":
        return 7
    elif month == "Aug":
        return 8
    elif month == "Sep":
        return 9
    elif month == "Oct":
        return 10
    elif month == "Nov":
        return 11
    elif month == "Dec":
        return 12
    else:
        if Print:
            print(
                f"Erorr: month is not in the range of Jan-Dec -> (date: {date}) -> (month: {month})"
            )
        return -1


def update_locations(df, sensitivity, Print=False):
    shelter_data = json.load(open("justiceWeather/inputData/shelter_data.json"))
    weather_data = json.load(open("justiceWeather/weather_data.json"))

    count = 0
    total = 0
    already_had = 0

    for index, row in df.iterrows():
        destination = row["Destination"]

        if row["Hiker Journal Link"] in weather_data:
            if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
                if Print:
                    print(
                        f'null lat and lon at {destination}, lat = {row["Latitude"]}, lon = {row["Longitude"]}'
                    )
                    print(
                        f"keys in map = {weather_data[row['Hiker Journal Link']].keys()}"
                    )
                if "lat" in weather_data[row["Hiker Journal Link"]]:
                    df.at[index, "Latitude"] = weather_data[row["Hiker Journal Link"]][
                        "lat"
                    ]
                    df.at[index, "Longitude"] = weather_data[row["Hiker Journal Link"]][
                        "lon"
                    ]
                    already_had += 1

        if (
            not destination
            or destination == "viewentry"
            or destination == ""
            or destination == "view entry"
            or type(destination) != str
        ):
            if Print:
                print(f"bad destination name = {destination}")
            continue

        if pd.notna(row["Longitude"]) and row["Longitude"] != "":
            if Print:
                print(
                    f"2 already had longitude and latitude info, lat = {row['Latitude']}, lon = {row['Longitude']}, at destination = {destination} "
                )
            continue

        if Print:
            print(
                f"destination = {destination}, longitude = {row['Longitude']}, latitude = {row['Latitude']}"
            )
        total += 1

        best_match, score = fuzzy_match(destination, shelter_data.keys())

        if score >= sensitivity:
            if score != 100 and score < 97 and Print:
                print(f"update! total -> {total}")
                print(
                    f"original destination = {destination}, best_match = {best_match}, score = {score}"
                )

            df.at[index, "Latitude"] = shelter_data[best_match]["cordinates"]["latitude"]
            df.at[index, "Longitude"] = shelter_data[best_match]["cordinates"][
                "longitude"
            ]
            if score != 100 and score < 97 and Print:
                print(
                    f"new long = {df.at[index, 'Longitude']}, new lat = {df.at[index, 'Latitude']}"
                )
            count += 1

        if isinstance(row["Latitude"], float) or isinstance(row["Latitude"], int):
            count_after_decimal = str(row["Latitude"])[::-1].find(".")
            if count_after_decimal < 2:
                if Print:
                    print(f"short lat = {row['Latitude']}")
                df.at[index, "Latitude"] = -1
                df.at[index, "Longitude"] = -1
                if Print:
                    print(f"new lat and long = {row['Latitude']}, {row['Longitude']}")

    if Print:
        print(f"final total == {total}")
        print(f"count == {count}")
        print(f"number of entries that are -1 {len(df[df['Latitude'] == -1])}")


def convertMonthYearToMonthYear(monthYear):
    month = (monthYear % 12) + 1
    year = (monthYear // 12) + 2016
    return month, year


def convertMonthAndYeartoMonthYear(month, year):
    monthYear = (year - 2016) * 12 + month - 1
    return monthYear


def count_entries_within_radius(
    target_lon, target_lat, radius_miles, currYear, currMonth, df, Print=False
):
    if (
        target_lat == None
        or target_lon == None
        or target_lon == ""
        or target_lat == ""
        or target_lat == -1
        or target_lon == -1
    ):
        if Print:
            print(
                f"target lon == {target_lon} or target lat == {target_lat} is not valid"
            )
        return -1
    # Convert miles to degrees (roughly, considering Earth's radius)
    degrees_per_mile = 1 / 69  # Approximately
    radius_deg = radius_miles * degrees_per_mile

    # Calculate latitude and longitude bounds for the square around the target point
    min_lon = target_lon - radius_deg
    max_lon = target_lon + radius_deg
    min_lat = target_lat - radius_deg
    max_lat = target_lat + radius_deg

    if Print:
        print(f"min_lon = {min_lon}")
        print(f"max_lon = {max_lon}")
        print(f"target_lon = {target_lon}")
        print(f"target_lat = {target_lat}")
        print(
            f'type that is lon = {type(df["Longitude"].values[0])}, that value is {df["Longitude"].values[0]}'
        )

    # Filter the DataFrame to get entries within the specified latitude and longitude bounds
    filtered_df = df[
        (df["Longitude"] >= min_lon)
        & (df["Longitude"] <= max_lon)
        & (df["Latitude"] >= min_lat)
        & (df["Latitude"] <= max_lat)
        & (df["year"] == currYear)
        & (df["month"] == currMonth)
    ]

    # Get the count of entries within the radius
    count_within_radius = len(filtered_df)

    return count_within_radius


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


def contains_alpha(string, Print=False) -> bool:
    if Print:
        print(f"input is {string} and is type {type(string)}")
    # if string is a number or float
    if isinstance(string, int) or isinstance(string, float):
        # at this point we can assume that string is either a number or float, return false if the float is NaN
        if string == float("NaN"):
            if Print:
                print(f"string is {string} and is type {type(string)}, but its NaN")
            return True
        return False

    for char in string:
        if char == ".":
            continue
        if char.isalpha():
            if Print:
                print(
                    f"string is {string} and is type string, but it has an alphabetical char"
                )
            return True
    return False


def load_raw_data_to_df(directory_path, version_number=3):
    file_names = os.listdir(directory_path)

    xlsx_file_names = [
        f
        for f in file_names
        if os.path.isfile(os.path.join(directory_path, f))
        and f.endswith(".xlsx")
        and f"v{version_number}" in f
    ]

    full_df = pd.DataFrame()
    for filename in xlsx_file_names:
        data = pd.read_excel(directory_path + "/" + filename)
        data["year"] = int(filename.split(".")[0].split("_")[0])
        if filename == "2016.xlsx":
            data.rename(columns={"Date": "date"}, inplace=True)
        full_df = pd.concat([full_df, data])

    return full_df


def convert_df_to_xlsx(df, filename):
    df.to_excel("mother_data/" + filename + ".xlsx", index=False)


def load_weather_data(Print=False):
    weather_data = json.load(open("justiceWeather/weather_data.json"))
    count = 0
    cleaned_data = {}
    for key in weather_data.keys():
        if "cod" in weather_data[key]:
            if Print:
                print(f"deleting {key} that contains {weather_data[key]}")
                print(" ")
            count += 1
        else:
            cleaned_data[key] = weather_data[key]["data"][0]
    if Print:
        print(f"number of entries that were deleted = {count}")

    cCount = 0
    added_weather_data = {}
    for key in cleaned_data.keys():
        added_weather_data[key] = cleaned_data[key]

        added_weather_data[key]["weather_description"] = "N/A"
        added_weather_data[key]["weather_icon"] = "N/A"
        added_weather_data[key]["weather_id"] = "N/A"
        added_weather_data[key]["weather_main"] = "N/A"

        if "weather" in added_weather_data[key]:
            weather = added_weather_data[key]["weather"][0]
            for weather_key in weather:
                added_weather_data[key]["weather_" + weather_key] = weather[weather_key]
            del added_weather_data[key]["weather"]

        if "rain" in cleaned_data[key]:
            rain = added_weather_data[key]["rain"]
            added_weather_data[key]["rain"] = rain[list(rain.keys())[0]]
            if Print:
                print(f'rain = {added_weather_data[key]["rain"]}')
        else:
            added_weather_data[key]["rain"] = -1
            if Print:
                print(f'rain = {added_weather_data[key]["rain"]}')

        # if "snow" in cleaned_data[key]:
        #     rain = added_weather_data[key]["snow"]
        #     added_weather_data[key]["snow"] = rain[list(snow.keys())[0]]
        #     if Print:
        #         print(f'snow = {added_weather_data[key]["snow"]}')
        # else:
        #     added_weather_data[key]["snow"] = -1
        #     if Print:
        #         print(f'snow = {added_weather_data[key]["snow"]}')

    if Print:
        print(f"number of entries that were deleted = {cCount}")
    print(f"len of added weather data = {len(added_weather_data)}")

    added_df = pd.DataFrame.from_dict(added_weather_data, orient="index")
    added_df = added_df.reset_index()
    added_df = added_df.rename(columns={"index": "Hiker Journal Link"})

    # replace any nan values with -1
    added_df = added_df.fillna(-1)

    #

    # rename the row called Name to Hiker Journal Link
    return added_df


def merge_weather_data(df, weather_df, Print=False):
    if Print:
        print(f"len of df = {len(df)}")
        print(f"len of weather_df = {len(weather_df)}")
    # if the link is not present in the weather df, set those columns to -1
    merged_df = pd.merge(df, weather_df, on="Hiker Journal Link", how="outer")

    if Print:
        print(f"len of merged_df = {len(merged_df)}")
    return merged_df
