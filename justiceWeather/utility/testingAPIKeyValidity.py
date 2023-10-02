# write a for loop to test the validity of the API keys, that thye are giving proper 200 codes, and print out the keys that are not working

import datetime
import json
import requests

printing = True
testingKeys = [
    "5bf8cd2a704c0c7027c23cf77acb79cb",
    "a43e4fa8f4893126918b75676cd106e6",
    "f6f90fd57e86f923624b9cef75cb1d94",
    "baf1e9f73dc9484ae19490582c19099d",
    "dd903cc2648b50119e69dfcfd00c8a7f",
    "059af59e7405830b0365c9fa623335e6",
    "d630ce2596a01ed25c9c92efa16b02bb",
]


def testKeys(keys):
    working = {}

    # get the datetime for sept 5 2023 as a baseline stamp
    dt = 1695410451

    correctPackage = {
        "lat": 10,
        "lon": 10,
        "timezone": "Africa/Lagos",
        "timezone_offset": 3600,
        "data": [
            {
                "dt": 1695410451,
                "sunrise": 1695359354,
                "sunset": 1695402997,
                "temp": 81.79,
                "feels_like": 84.13,
                "pressure": 1009,
                "humidity": 60,
                "dew_point": 66.56,
                "uvi": 0,
                "clouds": 100,
                "visibility": 10000,
                "wind_speed": 6.89,
                "wind_deg": 136,
                "wind_gust": 15.43,
                "weather": [
                    {
                        "id": 804,
                        "main": "Clouds",
                        "description": "overcast clouds",
                        "icon": "04n",
                    }
                ],
            }
        ],
    }

    for key in keys:
        try:
            # get the weather data for the destination and date
            package = requests.get(
                f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat=10&lon=10&dt={dt}&appid={key}&units=imperial"
            )

        except:
            print(f"Error: api call failed on key {key}")
            print(package.json())
            continue
        if package.status_code != 200:
            print(f"Error: api call failed on key {key}")
            print(package.json())
            continue
        if "timezone" not in package.json().keys():
            print(f"Error: api call failed on key {key}")
            print(package.json())
            continue

        if printing:
            print(package.status_code)

        working[key] = package.json()

    # pretty print the working dictionary in a human readble way
    if printing:
        print(json.dumps(working, indent=4, sort_keys=True))
        print("")
        print("")
    # make this more informative and human readble
    print(f"Out of {len(keys)} keys, {len(working)} are working")
    # print which keys are not working
    if len(keys) != len(working):
        print(
            f"The following keys are not working: {list(set(keys) - set(working.keys()))}"
        )
    # return the working keys in an array
    return list(working.keys())


# newKeys = testKeys(testingKeys)
