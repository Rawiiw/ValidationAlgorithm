import pandas as pd
import matplotlib.pyplot as plt

def get_image_data(data, satellite_choice):
    if satellite_choice == "aqua":
        return data[['LST_Day_1km']]
    elif satellite_choice == "landsat":
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

def plot_data(data, satellite_choice):
    if data is not None:
        print("Time and Temperature Values:")
        print(get_image_data(data, satellite_choice).to_string())

        plt.figure(figsize=(10, 6))
        plt.plot(data.index, get_image_data(data, satellite_choice),
                 label='Daytime Land Surface Temperature' if satellite_choice == "aqua" else 'Landsat Band 10')

        plt.ylabel('Temperature (°C)' if satellite_choice == "aqua" else 'Band 10 Value')
        plt.xlabel('Date')
        plt.title('MODIS Aqua Daytime Land Surface Temperature' if satellite_choice == "aqua" else 'Landsat Band 10')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()