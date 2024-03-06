import json

def write_to_json(satellite_data, excel_data, common_dates, output_file):
    """
    Write satellite and Excel data to a JSON file.

    Args:
    - satellite_data (pd.DataFrame): DataFrame containing satellite data.
    - excel_data (pd.DataFrame): DataFrame containing Excel data.
    - common_dates (pd.DatetimeIndex): DatetimeIndex containing common dates between satellite and Excel data.
    - output_file (str): Path to the output JSON file.
    """

    # Convert dataframes to dictionaries
    satellite_dict = satellite_data.reset_index().to_dict(orient='list')
    excel_dict = excel_data.reset_index().to_dict(orient='list')

    # Convert common dates to list of strings
    common_dates_list = common_dates.strftime('%Y-%m-%d %H:%M:%S').tolist()

    # Create JSON structure
    json_data = {
        "Satellite Data": {
            "Columns": list(satellite_data.columns),
            "Data": satellite_dict
        },
        "Excel Data": {
            "Columns": list(excel_data.columns),
            "Data": excel_dict
        },
        "Common Dates": common_dates_list
    }

    # Write JSON to file
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"Data written to {output_file} successfully.")
