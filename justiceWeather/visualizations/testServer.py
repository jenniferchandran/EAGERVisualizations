import json
import math
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from thefuzz import fuzz
from thefuzz import process


app = Flask(__name__)


dtype_dict = {
    "date": str,
    "Hiker trail name": str,
    "Hiker Journal Link": str,
    "Journal Story": str,
    "Start location": str,
    "Destination": str,
    "Today Miles": str,
    "Latitude": str,
    "Longitude": str,
    "State": str,
    "Total Shelters": str,
    "Occurrence": str,
    "year": str,
    "month": str,
    "label": str,
    # pandas serial object for type of emotion score
    "Unnamed: 0": str,
}

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


def convertIntToColor2(num):
    # make a map that maps ints to colors, have 2 be a deep red, have -4 be a deep blue and have 0 be white, be a gradient the rest inbetween
    return {
        2: [0, 0, 0, 0],
        1: [51, 51, 51, 0],
        0: [255, 255, 255, 0],
        -1: [204, 204, 204, 0],
        -2: [153, 153, 153, 0],
        -3: [102, 102, 102, 0],
        -4: [51, 51, 51, 0],
    }[num]


def labelToInt(label):
    return {
        "surprise": 2,
        "joy": 1,
        "neutral": 0,
        "sadness": -1,
        "anger": -2,
        "disgust": -3,
        "fear": -4,
    }[label]


def custom_scorer(s1, s2):
    s1_tokens = [token for token in s1.split() if token not in exclude_words]
    s2_tokens = [token for token in s2.split() if token not in exclude_words]
    return fuzz.token_set_ratio(s1_tokens, s2_tokens)


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


with open("../weather_data.json") as json_file:
    weather_data = json.load(json_file)

df = pd.read_excel(
    "../sentiment_full_updated_with_coords.xlsx", sheet_name="Sheet1", dtype=dtype_dict
)
df = df.drop(columns=["Unnamed: 0"])

# convert emotion scores to list
df = df[df["Emotion_scores"].apply(lambda x: type(x) == type("string"))]
df["Emotion_scores"] = df["Emotion_scores"].apply(lambda x: eval(x))


invalid_coords = []
# clean long and lat
for i in range(len(df["Latitude"].values)):
    lat = df["Latitude"].values[i]
    long = df["Longitude"].values[i]
    if type(lat) != type("string"):
        if math.isnan(lat) or math.isnan(long):
            invalid_coords.append(i)

            invalid_coords.append(i)
            continue

invalid_coords.sort(reverse=True)

for idx in invalid_coords:
    # grab 3 values from the df, the journal link, the latitude, and the longitude
    journal_link = df["Hiker Journal Link"].values[idx]
    lat = df["Latitude"].values[idx]
    long = df["Longitude"].values[idx]
    if journal_link in weather_data:
        curr_dict = weather_data[journal_link]
        curr_dict_keys = curr_dict.keys()
        if "cod" in curr_dict_keys:
            pass
        else:
            # replace the "Latitude" and "Longitude" in the df with the values in the curr dict from keys with "lat" and "lon" keys
            df["Latitude"].values[idx] = str(curr_dict["lat"])
            df["Longitude"].values[idx] = str(curr_dict["lon"])
            # print(f'found new lat {curr_dict["lat"]} in weather data')
            # print(f'type of "Latitude" is {type(df["Latitude"].values[idx])}')

    else:
        pass

df = df[df["Latitude"].apply(lambda x: type(x) == type("string"))]
df = df[df["year"].apply(lambda x: type(x) == type("string"))]
df = df[df["year"].apply(lambda x: len(x) == len("2016"))]
print(f'unique values in year column {df["year"].unique()}')


def count_entries_within_radius(
    target_lon, target_lat, radius_miles, currYear, currMonth
):
    # Convert miles to degrees (roughly, considering Earth's radius)
    degrees_per_mile = 1 / 69  # Approximately
    radius_deg = radius_miles * degrees_per_mile

    # Calculate latitude and longitude bounds for the square around the target point
    min_lon = target_lon - radius_deg
    max_lon = target_lon + radius_deg
    min_lat = target_lat - radius_deg
    max_lat = target_lat + radius_deg

    # Filter the DataFrame to get entries within the specified latitude and longitude bounds
    filtered_df = df[
        (df["lon"] >= min_lon)
        & (df["lon"] <= max_lon)
        & (df["lat"] >= min_lat)
        & (df["lat"] <= max_lat)
        & (df["year"] == currYear)
        & (df["month"] == currMonth)
    ]

    # Get the count of entries within the radius
    count_within_radius = len(filtered_df)

    return count_within_radius


# convert everything to right type
df["year"] = df["year"].astype(int)
# cast the month column to type int
df["month"] = df["month"].astype(int)

# cast the lat and long columns to type float
df["Latitude"] = df["Latitude"].astype(float)
df["Longitude"] = df["Longitude"].astype(float)

df["label_int"] = df["label"].apply(lambda x: labelToInt(x))
df["color"] = df["label_int"].apply(convertIntToColor2)

# create a new dataframe with the columns we need Latitude, Longitude, and color, and label, and year, and month, and hiker journal link, date
df = df[
    [
        "Latitude",
        "Longitude",
        "color",
        "label",
        "year",
        "month",
        "Hiker Journal Link",
        "date",
    ]
]


@app.route("/get_data", methods=["GET"])
def get_data():
    # turn the df into a valid reuqest object
    response = jsonify(df.to_dict(orient="records"))
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    return response


if __name__ == "__main__":
    CORS(app)  # Enable CORS for all routes
    CORS(app, resources={r"/get_data": {"origins": "http://localhost:5173"}})
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(port=5000)