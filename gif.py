import pandas as pd
import numpy as np
from shapely import Point
import ee
import datetime
import matplotlib.pyplot as plt

# Authenticate and initialize Google Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-kosinova')

# Function to validate coordinates
def validate_coordinates(coords):
    try:
        if len(coords) != 2:
            return False
        latitude = float(coords[0])
        longitude = float(coords[1])
        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            return True
        else:
            return False
    except ValueError:
        return False

# Function to input coordinates
def input_coordinates():
    while True:
        coordinates_str = input("Enter coordinates (latitude, longitude)").strip()
        if not coordinates_str:
            return '62.241918, 67.926724'
        coordinates = coordinates_str.split(',')
        if validate_coordinates(coordinates):
            return coordinates
        else:
            print("Incorrect coordinates. Please enter correct values.")

def input_date(default_date):
    while True:
        date_str = input("Enter date in YYYY-MM-DD format [Default: {}]: ".format(default_date)).strip()
        if not date_str:
            return default_date
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("Incorrect date format. Please enter date in YYYY-MM-DD format.")


# Function to process Aqua data
def process_aqua_data(location_point, scale, date_start, date_end):
    variables = ['LST_Day_1km']
    gre = ee.ImageCollection("MODIS/006/MOD11A1").select(variables).filter(ee.Filter.date(date_start, date_end))

    if gre.size().getInfo() == 0:
        print("No data available for the selected satellite and date range.")
        return None

    data = gre.getRegion(location_point, scale).getInfo()
    data = pd.DataFrame(data[1:], columns=data[0])
    data['date'] = pd.to_datetime(data['id'], format='%Y_%m_%d', errors='coerce')
    data.dropna(inplace=True)  # Remove rows with NaN values
    data.set_index("date", inplace=True)
    data['LST_Day_1km'] = data['LST_Day_1km'].astype(float) * 0.02 - 273.15

    return data

def get_image_data(data, satellite_choice):
    if satellite_choice == "aqua":
        return data[['LST_Day_1km']]
    elif satellite_choice == "landsat":
        # Check if the Landsat Collection is 1 or 2
        if 'B10' in data.columns:
            return data[['B10']]
        elif 'ST_B10' in data.columns:
            return data[['ST_B10']]
        else:
            print("Band not found in the data. Please check the satellite collection.")
            return None
    else:
        print("Invalid satellite choice. Please choose Aqua or Landsat.")
        return None


def process_landsat_data(location_point, scale, date_start, date_end):
    variables = ['B10'] 
    gre = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").select(variables).filter(ee.Filter.date(date_start, date_end))

    if gre.size().getInfo() == 0:
        print("No data available for the selected satellite and date range.")
        return None

    data = gre.getRegion(location_point, scale).getInfo()
    data = pd.DataFrame(data[1:], columns=data[0])
    data['date'] = pd.to_datetime(data['id'], unit='ms', errors='coerce')
    data.dropna(inplace=True)  # Remove rows with NaN values
    data.set_index("date", inplace=True)

    return data



# Input coordinates
coordinates = input_coordinates()
x = float(coordinates[0])
y = float(coordinates[1])

# Parameters definition
scale = 11132

# Input start and end dates
date_start = input_date('2019-01-01')
date_end = input_date('2019-03-01')


location_point = ee.Geometry.Point(x, y)

# Choose satellite
satellite_choice = input("Choose satellite (Aqua or Landsat) [Default: aqua]: ").lower() or 'aqua'

# Process data based on satellite choice
if satellite_choice == "aqua":
    data = process_aqua_data(location_point, scale, date_start, date_end)
elif satellite_choice == "landsat":
    data = process_landsat_data(location_point, scale, date_start, date_end)
else:
    print("Invalid satellite choice. Please choose Aqua or Landsat.")


# Plotting
if data is not None:
    print("Time and Temperature Values:")
    print(get_image_data(data, satellite_choice).to_string())

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, get_image_data(data, satellite_choice), label='Daytime Land Surface Temperature' if satellite_choice == "aqua" else 'Landsat Band 10')

    plt.ylabel('Temperature (°C)' if satellite_choice == "aqua" else 'Band 10 Value')
    plt.xlabel('Date')
    plt.title('MODIS Aqua Daytime Land Surface Temperature' if satellite_choice == "aqua" else 'Landsat Band 10')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
