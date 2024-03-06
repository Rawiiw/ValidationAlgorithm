from datetime import timedelta

import ee
import pandas as pd


def process_landsat_data(location_point, scale, date_start, date_end):
    variables = ['B3', 'B4', 'B5', 'B6', 'B10', 'B11']
    gre = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA").select(variables).filter(ee.Filter.date(date_start, date_end))

    if gre.size().getInfo() == 0:
        print("No data available for the selected satellite and date range.")
        return None

    data = gre.getRegion(location_point, scale).getInfo()
    data = pd.DataFrame(data[1:], columns=data[0])
    data['date'] = pd.to_datetime(data['time'], format='%d.%m.%Y %H:%M', errors='coerce')  # Adjust date format
    data.dropna(inplace=True)
    data.set_index("date", inplace=True)

    # Filter data based on time range from Excel
    data = data[(data.index >= date_start) & (data.index <= date_end)]

    return data