import geopandas as gpd
import cartopy.io.shapereader as shpreader
import pandas as pd
from shapely.geometry import Point, shape
import pandas

# Mapping of state names to their abbreviations for the US
state_to_abbr = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
    'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}


# Get the geometries of US states
reader = shpreader.Reader(shpreader.natural_earth(
    resolution='110m', category='cultural', name='admin_1_states_provinces'))
states = [state for state in reader.records(
) if state.attributes['iso_a2'] == 'US']

# Convert these states to a GeoDataFrame
data = {
    "name": [state.attributes['name'] for state in states],
    "geometry": [state.geometry for state in states]
}
gdf_states = gpd.GeoDataFrame(data)


def get_state_abbr_from_coords(arg):
    latitude, longitude = arg
    if pandas.isna(latitude) or pandas.isna(longitude):
        return pandas.NA
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except:
        return pandas.NA

    geom = [Point(longitude, latitude)]
    point_gdf = gpd.GeoDataFrame(geometry=geom)

    # Spatial join between point and states to find out which state it belongs to
    point_in_states = gpd.sjoin(
        point_gdf, gdf_states, how="inner", op="within")
    if point_in_states.empty:
        return pd.NA
    else:
        state_name = point_in_states.iloc[0]['name']
        return state_name
