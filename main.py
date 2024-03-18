import ee
import pandas as pd

from common_dates import CommonDates
from output_maker import create_csv, create_excel
from aqua_data import get_image_collection, get_feature_collection, get_datatable
from excel_manager import ExcelManager
from rsme_mbe import calculate_rmse_mbe


def authenticate_ee():
    ee.Authenticate()
    ee.Initialize(project='ee-kosinova')


def select_excel_file():
    excel_manager = ExcelManager()
    excel_manager.select_excel_file()
    return excel_manager


def read_excel_data(excel_manager):
    if excel_manager.read_excel():
        excel_manager.print_data()
    else:
        print("Не удалось прочитать данные из файла Excel.")
    return excel_manager


def get_coordinates():
    print("Введите координаты точки в формате 'широта,долгота':")
    coordinates = list(map(float, input("Координаты: ").split(',')))
    return coordinates


def get_image_data(coordinates, date_start, date_end):
    lst = get_image_collection(coordinates, date_start, date_end)
    return lst


def get_feature_data(lst, coordinates):
    point = ee.Geometry.Point(coordinates)
    featureCollection = get_feature_collection(lst, point)
    return featureCollection


def create_dataframe(featureCollection):
    datatable = get_datatable(featureCollection)
    df = pd.DataFrame([feature['properties'] for feature in datatable.getInfo()['features']])
    return df


def match_data(selected_columns, excel_data):
    matcher = CommonDates(selected_columns, excel_data)
    matches = matcher.match_data()
    return matches


def process_data(matches):
    for match in matches:
        print(f"{match['source']} - {match['datetime']} - {match['value']}")
    rmse, mbe = calculate_rmse_mbe(matches)
    print(f"RMSE: {rmse}")
    print(f"MBE: {mbe}")


def save_table(df):
    save_table = input("Хотите ли вы сохранить таблицу со значениями? (да/нет): ")
    if save_table.lower() == "да":
        format_choice = input("Выберите формат для сохранения (csv/excel): ")
        if format_choice.lower() == "csv":
            create_csv(df)
        elif format_choice.lower() == "excel":
            create_excel(df)
        else:
            print("Некорректный выбор формата.")
    elif save_table.lower() == "нет":
        print("Таблица не сохранена.")
    else:
        print("Некорректный ответ.")


if __name__ == "__main__":
    authenticate_ee()
    excel_manager = select_excel_file()
    excel_manager = read_excel_data(excel_manager)
    coordinates = get_coordinates()
    date_start = excel_manager.date_start.strftime('%Y-%m-%d')
    date_end = excel_manager.date_end.strftime('%Y-%m-%d')
    lst = get_image_data(coordinates, date_start, date_end)
    featureCollection = get_feature_data(lst, coordinates)
    df = create_dataframe(featureCollection)
    selected_columns = df[["date", "Night_view_time", "Day_view_time", "LST_Day_1km", "LST_Night_1km"]]
    excel_data = excel_manager.data
    matches = match_data(selected_columns, excel_data)
    process_data(matches)
    save_table(df)
