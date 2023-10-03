import plotly.express as px
import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# TODO: Add 3D map where height is the number of people at a given location, and the color is the temperature

weather_data_file_path = "../weather_data.json"


# import the data from the weather_data.json file
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


weather_data = json.load(open(weather_data_file_path))
print(len(weather_data))

yearCount = {}

for key in weather_data:
    # find the year for the key
    year = weather_data[key]["date"].split(", ")[2]
    if year not in yearCount:
        yearCount[year] = 1
    else:
        yearCount[year] += 1

maxYear = None

for year in yearCount:
    if maxYear is None or yearCount[year] > yearCount[maxYear]:
        maxYear = year


# find the month in 2017 with the most entries
monthCount = {}

for key in weather_data:
    year = weather_data[key]["date"].split(", ")[2]
    if year == maxYear:
        month = weather_data[key]["date"].split(", ")[0].split(" ")[0]
        if month not in monthCount:
            monthCount[month] = 1
        else:
            monthCount[month] += 1

maxMonth = None

for month in monthCount:
    if maxMonth is None or monthCount[month] > monthCount[maxMonth]:
        maxMonth = month
print(f"maxMonth = {maxMonth}, entreis in month = {monthCount[maxMonth]}")


# create a map that just has the data for the entire month of april in 2017 from our weather_data dictionary that contains only 3 things, the longitude, latitude, and temperature
data_list = []

for key, value in weather_data.items():
    year = value["date"].split(", ")[2]
    month = value["date"].split(", ")[0].split(" ")[0]

    if "lon" in value and year in "20162017201820192020202120222023":
        data_list.append(
            {
                "lon": value["lon"],
                "lat": value["lat"],
                "temp": value["data"][0]["temp"],
                "year": int(year),
                "month": monthToNum(month),
            }
        )

# Create a DataFrame from the filtered data
df = pd.DataFrame(data_list)
available_years = df["year"].unique()

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
        html.Div(
            [
                dcc.Slider(
                    id="month-slider",
                    min=df["month"].min(),
                    max=df["month"].max(),
                    step=1,
                    value=df["month"].min(),
                    marks={
                        i: numTofullMonthName(i)
                        for i in range(df["month"].min(), df["month"].max() + 1)
                    },
                ),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": year, "value": year} for year in available_years],
                    value=available_years[0],  # Default selected year
                ),
            ],
            style={"width": "100%"},  # Adjust the size
        ),
    ],
    style={"display": "flex", "flex-direction": "column", "align-items": "center"},
)


# Define a callback to update the heatmap based on the selected month and year
@app.callback(
    Output("heatmap", "figure"),
    Input("month-slider", "value"),
    Input("year-dropdown", "value"),
)
def update_heatmap(selected_month, selected_year):
    # Filter the DataFrame based on the selected month and year
    filtered_df = df[(df["month"] == selected_month) & (df["year"] == selected_year)]

    # Create the heatmap
    fig = px.density_mapbox(
        filtered_df,
        lat="lat",
        lon="lon",
        z="temp",
        radius=10,  # Adjust the radius as needed
        center=dict(lat=41.90722, lon=-70.0369),  # Center of the United States
        zoom=5,  # Adjust the zoom level as needed
        mapbox_style="stamen-terrain",  # You can choose a different map style
        title=f"Temperature Heatmap for {numTofullMonthName(selected_month)}, {selected_year}",
        color_continuous_scale="Inferno",  # Adjust the color scale
        range_color=[30, 100],  # Set the color scale range
        hover_data={
            "lat": False,
            "lon": False,
            "temp": True,
        },  # Include temperature in hover data
    )

    # Create a custom hover template that displays temperature and the count within a 10-mile radius
    fig.update_traces(
        hovertemplate="<b>Temperature</b>: %{z}<br><b>Entries in 5-Mile Radius</b>: %{customdata}",
        customdata=filtered_df.apply(
            lambda row: count_entries_within_radius(
                row["lon"], row["lat"], 5, row["year"], row["month"]
            ),
            axis=1,
        ),
    )

    fig.update_layout(mapbox=dict(center=dict(lat=38.0902, lon=-77.7129)))

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
