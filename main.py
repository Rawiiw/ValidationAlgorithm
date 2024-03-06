import ee

import plot_data
from aqua_data import process_aqua_data
from excel_manager import ExcelManager
from landsat_data import process_landsat_data
from rsme_mbe import calculate_rmse_mbe

ee.Authenticate()
ee.Initialize(project='ee-kosinova')

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

def main():
    excel_manager = ExcelManager()
    # Choose the Excel file
    excel_manager.select_excel_file()
    # Read the data from the Excel file
    if excel_manager.read_excel():
        # Use date_start and date_end from ExcelManager for processing data from Earth Engine
        date_start = excel_manager.date_start
        date_end = excel_manager.date_end

        coordinates = input_coordinates()
        x = float(coordinates[0])
        y = float(coordinates[1])

        # Parameters definition
        scale = 11132

        location_point = ee.Geometry.Point(x, y)

        # Choose the satellite
        satellite_choice = input("Choose satellite (Aqua or Landsat) [Default: aqua/landsat]: ").lower() or 'aqua'

        # Process data depending on the selected satellite
        if satellite_choice == "aqua":
            data = process_aqua_data(location_point, scale, date_start, date_end)
        elif satellite_choice == "landsat":
            data = process_landsat_data(location_point, scale, date_start, date_end)
        else:
            print("Invalid satellite choice. Please choose Aqua or Landsat.")
            return

        # Print the data
        plot_data.plot_data(data, satellite_choice)

        # Load data from the Excel file
        excel_data = excel_manager.data.set_index('datetime')['value']

        # Choose only dates that match in both datasets
        common_dates = excel_data.index.intersection(data.index)

        print("Dates in satellite data:", data.index.strftime('%Y-%m-%d %H:%M:%S'))
        print("Dates in Excel data:", excel_data.index.strftime('%Y-%m-%d %H:%M:%S'))

        print("Common dates:", common_dates)

        if len(common_dates) == 0:
            print("No common dates found between satellite and Excel data.")
            return

        satellite_data = data.loc[common_dates]
        excel_data = excel_data.loc[common_dates]

        # Calculate RMSE and MBE
        rmse, mbe = calculate_rmse_mbe(satellite_data, excel_data)
        print("RMSE:", rmse)
        print("MBE:", mbe)
        print("Number of missing values in satellite data:", satellite_data.isnull().sum())
        print("Number of missing values in Excel data:", excel_data.isnull().sum())
        print("First date in satellite data:", satellite_data.index[0])
        print("Last date in satellite data:", satellite_data.index[-1])
        print("First date in Excel data:", excel_data.index[0])
        print("Last date in Excel data:", excel_data.index[-1])

    else:
        print("Failed to read Excel file.")


if __name__ == "__main__":
    main()