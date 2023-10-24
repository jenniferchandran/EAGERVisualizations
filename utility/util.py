import datetime
import json
import os
from thefuzz import fuzz
from thefuzz import process
import pandas as pd


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


def get_month_from_date(date):
    if is_valid_date(date) == False:
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
    # loop over all the rows in the df
    for index, row in df.iterrows():
        destination = row["Destination"]

        if row["Hiker Journal Link"] in weather_data:
            # check to see if the latitude and longitude data in row we are on is nan or none or empty
            if pd.isna(row["Latitude"]) or pd.isna(row["Longitude"]):
                if Print:
                    print(
                        f'null lat and lon at {destination}, lat = {row["Latitude"]}, lon = {row["Longitude"]}'
                    )
                    print(
                        f"keys in map = {weather_data[row['Hiker Journal Link']].keys()}"
                    )
                if "lat" in weather_data[row["Hiker Journal Link"]]:
                    row["Latitude"] = weather_data[row["Hiker Journal Link"]]["lat"]
                    row["Longitude"] = weather_data[row["Hiker Journal Link"]]["lon"]
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

        # use pandas to check to see if the longitude row has information that isnt "" or is empty
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

        # print(
        #     f"actual destination = {destination}, best_match = {best_match}, score = {score}"
        # )

        if score >= sensitivity:
            if score != 100 and score < 97 and Print:
                print(f"update! total -> {total}")
                print(
                    f"original destination = {destination}, best_match = {best_match}, score = {score}"
                )

            row["Latitude"] = shelter_data[best_match]["cordinates"]["latitude"]
            row["Longitude"] = shelter_data[best_match]["cordinates"]["longitude"]
            # if score != 100 and score < 97 and Print:
            # print(f"new long = {row['Longitude']}, new lat = {row['Latitude']}")
            count += 1
    if Print:
        print(f"final total == {total}")
        print(f"count == {count}")
    return df


def convertMonthYearToMonthYear(monthYear):
    month = (monthYear % 12) + 1
    year = (monthYear // 12) + 2016
    return month, year


def convertMonthAndYeartoMonthYear(month, year):
    monthYear = (year - 2016) * 12 + month - 1
    return monthYear


def count_entries_within_radius(
    target_lon, target_lat, radius_miles, currYear, currMonth, df
):
    if currMonth <= 0:
        print(f"curr month == {currMonth} is not valid")
        return -1
    if (
        target_lat == None
        or target_lon == None
        or target_lon == ""
        or target_lat == ""
        or target_lat == -1
        or target_lon == -1
    ):
        print("target lon == {target_lon} or target lat == {target_lat} is not valid")
        return -1
    # Convert miles to degrees (roughly, considering Earth's radius)
    degrees_per_mile = 1 / 69  # Approximately
    radius_deg = radius_miles * degrees_per_mile

    # Calculate latitude and longitude bounds for the square around the target point
    min_lon = target_lon - radius_deg
    max_lon = target_lon + radius_deg
    min_lat = target_lat - radius_deg
    max_lat = target_lat + radius_deg

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


def contains_alpha(string) -> bool:
    if string != type("asd"):
        return True

    for char in string:
        if char == ".":
            continue
        if char.isalpha():
            print(f"string is {string} and is type string, but its numeric")
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
