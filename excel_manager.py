import pandas as pd
import tkinter as tk
from tkinter import filedialog

class ExcelManager:
    def __init__(self):
        self.file_path = None
        self.data = None
        self.date_start = None
        self.date_end = None

    def select_excel_file(self):
        root = tk.Tk()
        root.withdraw()
        self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        return self.file_path

    def read_excel(self):
        if self.file_path:
            try:
                df = pd.read_excel(self.file_path, names=['date', 'time', 'value'])

                # Convert date and time columns to strings
                df['date'] = df['date'].astype(str)
                df['time'] = df['time'].astype(str)

                # Concatenate date and time columns into a datetime column
                df['datetime'] = df['date'] + ' ' + df['time']

                # Convert the datetime column to datetime objects
                df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')

                # Set date_start and date_end
                self.date_start = df['datetime'].iloc[0]
                self.date_end = df['datetime'].iloc[-1]

                # Drop the original date and time columns
                df.drop(['date', 'time'], axis=1, inplace=True)

                self.data = df

                return True
            except Exception as e:
                print("Error reading Excel file:", e)
                return False
        else:
            print("No Excel file selected.")
            return False

    def print_data(self):
        if self.data is not None:
            print("Data from Excel:")
            print(self.data.to_string(index=False))
        else:
            print("No data available.")