import pandas as pd
import ee
from datetime import datetime

def process_aqua_data(location_point, scale, date_start, date_end):
    variables = ['LST_Day_1km']
    gre = ee.ImageCollection("MODIS/006/MOD11A1").select(variables).filter(ee.Filter.date(date_start, date_end))
    if gre.size().getInfo() == 0:
        print("No data available for the selected satellite and date range.")
        return None

    # Get the time data directly from the ImageCollection
    time_data = gre.aggregate_array('system:time_start').getInfo()

    # Convert time to a datetime object
    time = [datetime.fromtimestamp(x / 1000) for x in time_data]

    data = gre.getRegion(location_point, scale).getInfo()
    data = pd.DataFrame(data[1:], columns=data[0])

    data['datetime'] = time

    data.dropna(inplace=True)
    data.set_index("datetime", inplace=True)
    data.index = data.index.strftime('%Y-%m-%d %H:%M:%S')

    data['LST_Day_1km'] = data['LST_Day_1km'].astype(float) * 0.02 - 273.15

    return data
