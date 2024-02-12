from tkinter import Tk, filedialog
import ee
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

ee.Authenticate()
ee.Initialize(project='ee-kosinova')


def load_data_from_excel(excel_file):
    df = pd.read_excel(excel_file, names=['Date', 'Time', 'Temperature'])
    df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
    return df[['DateTime', 'Temperature']]

def get_temperature_data(coordinates, start_date, end_date, start_time, end_time, satellite, max_distance=10000):
    try:
        start_datetime = ee.Date(datetime.strptime(start_date + ' ' + start_time, '%d.%m.%Y %H:%M').isoformat())
        end_datetime = ee.Date(datetime.strptime(end_date + ' ' + end_time, '%d.%m.%Y %H:%M').isoformat())

        if satellite.lower() == 'landsat':
            collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')
            temperature_band = 'B10'
        elif satellite.lower() == 'aqua':
            collection = ee.ImageCollection('MODIS/006/MOD11A1')
            temperature_band = 'LST_Day_1km'
        else:
            raise ValueError('Invalid satellite selection. Please choose "Landsat" or "Aqua".')

        latitude, longitude = map(float, coordinates.split(','))
        point = ee.Geometry.Point(longitude, latitude)

        # Фильтрация коллекции по времени и расстоянию от заданной точки
        filtered_collection = collection.filterDate(start_datetime, end_datetime) \
            .filterBounds(point) \
            .filter(ee.Filter.lt('system:time_start', end_datetime.millis())) \
            .filter(ee.Filter.gt('system:time_start', start_datetime.millis())) \
            .filter(ee.Filter.lt('CLOUD_COVER', 5))

        image = ee.Image(filtered_collection.first())

        temperature_data = image.reduceRegion(reducer=ee.Reducer.mean(),
                                              geometry=point,
                                              scale=1000)

        print("Temperature data object:")
        print(temperature_data.getInfo())

        temperature_gee = temperature_data.get(temperature_band)
        print("Temperature GEE object:")
        print(temperature_gee.getInfo())

        # Получение времени съемки изображения из метаданных
        system_time_start = image.get('system:time_start').getInfo()
        print("System time start:")
        print(system_time_start)

        return temperature_gee.getInfo() - 273.15, system_time_start  # Перевод из K в C

    except Exception as e:
        print("An error occurred in get_temperature_data:", e)
        return None, None



def compute_rmse_mbe(observed, predicted):
    rmse = np.sqrt(np.mean((observed - predicted) ** 2))
    mbe = np.mean(observed - predicted)
    return rmse, mbe


def plot_temperature_comparison(ground_data, temperature_value, search_time, system_time_start):
    plt.plot(ground_data['DateTime'], ground_data['Temperature'], label='Наземные данные')
    plt.axhline(y=temperature_value, color='r', linestyle='--', label='GEE данные')
    plt.axvline(x=pd.to_datetime(system_time_start / 1000, unit='s', utc=True), color='g', linestyle='--',
                label='Время съемки')
    plt.xlabel('Дата и время')
    plt.ylabel('Температура (°C)')
    plt.title('Сравнение наземных и GEE данных о температуре')
    plt.legend()
    plt.grid(True)
    plt.show()


def select_excel_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    return file_path


def get_coordinates_from_map():
    # New coordinates: Moscow
    return '55.7558, 37.6176'


def main():
    try:
        coordinates = get_coordinates_from_map()
        print(f'Координаты: {coordinates}')

        start_date = input('Введите дату начала (дд.мм.гггг): ')
        if not start_date:
            start_date = '01.01.2021'

        end_date = input('Введите дату окончания (дд.мм.гггг): ')
        if not end_date:
            end_date = '31.12.2021'

        start_time = input('Введите время начала (чч:мм): ')
        if not start_time:
            start_time = '00:00'

        end_time = input('Введите время окончания (чч:мм): ')
        if not end_time:
            end_time = '23:59'

        satellite = input('Выберите спутник (Landsat или Aqua): ')
        if not satellite:
            satellite = 'Landsat'

        print("User inputs collected.")

        excel_file = select_excel_file()
        ground_data = load_data_from_excel(excel_file)
        print("Ground data loaded.")

        temperature_gee, system_time_start = get_temperature_data(coordinates, start_date, end_date, start_time,
                                                                   end_time, satellite)
        print("Temperature GEE object:", temperature_gee)

        if temperature_gee is not None:
            if satellite.lower() == 'aqua':
                temperature_value = temperature_gee
            elif satellite.lower() == 'landsat':
                temperature_band = 'B10' if temperature_gee is not None else 'B11'
                temperature_value = temperature_gee
            else:
                raise ValueError('Invalid satellite selection. Please choose "Landsat" or "Aqua".')

            if temperature_value is not None:
                print(f'Температура (GEE): {temperature_value} °C')
            else:
                print('Ошибка: Данные о температуре отсутствуют в объекте temperature_gee.')

            search_time = None
            if isinstance(temperature_gee, dict) and 'properties' in temperature_gee:
                if system_time_start:
                    search_time = pd.to_datetime(system_time_start, unit='ms', utc=True).strftime('%d.%m.%Y %H:%M')
                else:
                    print('Ошибка: Время съемки не найдено в метаданных.')
            else:
                print('Ошибка: Метаданные о температуре отсутствуют или имеют неверный формат.')

            if search_time:
                idx = ground_data.index[ground_data['DateTime'] == search_time].tolist()
                if idx:
                    idx = idx[0]
                    ground_temperature = ground_data.iloc[idx]['Temperature']
                    rmse, mbe = compute_rmse_mbe(temperature_value, ground_temperature)
                    print(f'RMSE: {rmse}')
                    print(f'MBE: {mbe}')

                    plot_temperature_comparison(ground_data, temperature_value, search_time, system_time_start)
                else:
                    print('Ошибка: Время поиска не найдено в данных наземных измерений.')
            else:
                print('Ошибка: Время поиска не определено.')
        else:
            print('Ошибка: Объект temperature_gee равен None.')

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
