import numpy as np
from sklearn.metrics import mean_squared_error


def calculate_rmse_mbe(matches):
    # Prepare lists to calculate RMSE and MBE
    satellite_values = []
    ground_values = []

    # Output the matches
    for match in matches:
        print(f"{match['source']} - {match['datetime']} - {match['value']}")

        # Convert the value to numeric
        value = float(match['value'])  # Assuming the value is convertible to float

        if match['source'] == 'Satellite':
            satellite_values.append(value)
        elif match['source'] == 'Ground':
            ground_values.append(value)

    rmse = np.sqrt(mean_squared_error(satellite_values, ground_values))
    mbe = np.mean(np.array(satellite_values) - np.array(ground_values))

    return rmse, mbe
