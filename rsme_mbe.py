from math import sqrt

import pandas as pd


def calculate_rmse_mbe(satellite_value, excel_value):
    squared_diff = (satellite_value - excel_value) ** 2
    rmse = sqrt(squared_diff.mean())
    mbe = (satellite_value - excel_value).mean()
    return rmse, mbe

def calculate_results(data, excel_data, common_dates):
    results = []

    for date in common_dates:
        satellite_value = data.loc[date]['LST_Day_1km']
        excel_values = excel_data.loc[date]
        avg_excel_value = excel_values.mean()
        rmse, mbe = calculate_rmse_mbe(satellite_value, avg_excel_value)
        results.append({'date': date, 'satellite_value': satellite_value, 'excel_value': avg_excel_value, 'rmse': rmse, 'mbe': mbe})

    return pd.DataFrame(results)

