import plotly.express as px
import json
import pandas as pd
import dash
import os
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


global currMonthYear
currMonthYear = 0
TIME_INTERVAL = 5
years_showing = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
range_of_colors = [-5, 5]


def convertMonthYearToMonthYear(monthYear):
    month = (monthYear % 12) + 1
    year = (monthYear // 12) + 2016
    return month, year



def count_entries_within_radius(target_lon, target_lat, radius_miles):
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


folder_path = "../inputData/"
max_date = None
# open the file and load the data into a dictionary
for filename in os.listdir(folder_path):
    # find the json file that looks like deltaTempData_x_x_x_x.json where x_x_x_ is month_day_hour_minute, find the file that has the most recent date
    if filename.startswith("deltaTempData_"):
        numArr = filename.split("_")
        numbers = (numArr[1], numArr[2], numArr[3], numArr[4].split(".")[0])
        if not max_date:
            max_date = numbers
        else:
            # first compare the month numbres[0], if theyre the same, compare the month, if theyre the same, compare the hour, and after all that comapre the minute
            if numbers[0] > max_date[0]:
                max_date = numbers
            elif numbers[0] == max_date[0]:
                if numbers[1] > max_date[1]:
                    max_date = numbers
                elif numbers[1] == max_date[1]:
                    if numbers[2] > max_date[2]:
                        max_date = numbers
                    elif numbers[2] == max_date[2]:
                        if numbers[3] > max_date[3]:
                            max_date = numbers
                        elif numbers[3] == max_date[3]:
                            print("ERROR: Two files have the same name")
                            exit()


file_name = (
    folder_path
    + f"deltaTempData_{max_date[0]}_{max_date[1]}_{max_date[2]}_{max_date[3]}.json"
)
print(f"file_name = {file_name}")

# open that file_name and convert it to a pandas dataframe
all_data = json.load(open(file_name))
weeksSearched = all_data["weeks"]
milesSearched = all_data["miles"]
weather_data = all_data["data"]
complete_data = []

for key, value in weather_data.items():
    year = str(value["year"])
    if year in years_showing:
        complete_data.append(
            {
                "lon": value["lon"],
                "lat": value["lat"],
                "deltaTemp": value["deltaTemp"],
                "link": key,
                "year": int(year),
                "month": int(value["month"]),
            }
        )

# create a dataframe from the list of dictionaries
df = pd.DataFrame(complete_data)
available_years = df["year"].unique()
print(f"available_years = {available_years}")
# sort the available years in ascending order
available_years.sort()

app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        dcc.Graph(
            id="heatmap",
            style={
                "width": "100%",
                "height": "80vh",
            },  # Make the heatmap take up most of the screen
        ),
        dcc.Interval(
            id="interval-component",
            interval=1000,  # Update every 1000 seconds (1000 milliseconds)
            n_intervals=0,
        ),
    ],
    style={"display": "flex", "flex-direction": "column", "align-items": "center"},
)


# Define a callback to update the heatmap based on the selected month and year
@app.callback(Output("heatmap", "figure"), Input("interval-component", "n_intervals"))
def update_heatmap(n_intervals):
    global currMonthYear
    currMonthYear = (currMonthYear + 1) % (len(years_showing) * 12)
    selected_month, selected_year = convertMonthYearToMonthYear(currMonthYear)
    print(f"selected_month = {selected_month}, selected_year = {selected_year}"")
    # Filter the DataFrame based on the selected month and year
    filtered_df = df[(df["month"] == (selected_month)) & (df["year"] == selected_year)]

    # Create the heatmap
    fig = px.density_mapbox(
        filtered_df,
        lat="lat",
        lon="lon",
        z="deltaTemp",
        radius=10,  # Adjust the radius as needed
        center=dict(lat=41.90722, lon=-70.0369),  # Center of the United States
        zoom=5,  # Adjust the zoom level as needed
        mapbox_style="stamen-terrain",  # You can choose a different map style
        title=f"Delta from Avereage Temperature Heatmap for {numTofullMonthName(selected_month)}, {selected_year}",
        color_continuous_scale="Inferno",  # Adjust the color scale
        range_color=[range_of_colors[0], range_of_colors[1]],  # Set the color scale range
        hover_data={
            "lat": False,
            "lon": False,
            "deltaTemp": True,
        },  # Include temperature in hover data
    )
    # Create a custom hover template that displays temperature and the count within a milesSearched-mile radius
    fig.update_traces(
        hovertemplate="<b>Delta of Temperature</b>: %{z}<br><b>Entries in 10-Mile Radius</b>: %{customdata}",
        customdata=filtered_df.apply(
            lambda row: count_entries_within_radius(
                row["lon"], row["lat"], milesSearched
            ),
            axis=1,
        ),
    )
    fig.update_layout(mapbox=dict(center=dict(lat=38.0902, lon=-77.7129)))

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
