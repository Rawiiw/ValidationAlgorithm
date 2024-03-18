from datetime import datetime, timedelta

class CommonDates:
    def __init__(self, selected_columns, excel_data):
        self.selected_columns = selected_columns
        self.excel_data = excel_data

    def _parse_date(self, date_string):
        """Parse date string into datetime object."""
        return datetime.strptime(date_string, '%Y-%m-%d')

    def _find_matching_rows(self, satellite_datetime):
        """Find matching rows in Excel data within a window of +/- 15 minutes."""
        return self.excel_data[
            (self.excel_data['datetime'] >= satellite_datetime - timedelta(minutes=15)) &
            (self.excel_data['datetime'] <= satellite_datetime + timedelta(minutes=15))
        ]

    def match_data(self):
        """Match satellite and ground data based on common dates and times."""
        matches = []

        for index, row in self.selected_columns.iterrows():
            satellite_datetime = self._parse_date(row['date'])

            matching_rows = self._find_matching_rows(satellite_datetime)

            if not matching_rows.empty:
                for _, match_row in matching_rows.iterrows():
                    matches.append({
                        'source': 'Satellite',
                        'datetime': satellite_datetime,
                        'value': row['LST_Day_1km']  # Adjust column name as necessary
                    })
                    matches.append({
                        'source': 'Ground',
                        'datetime': match_row['datetime'],
                        'value': match_row['value']
                    })

        return matches
