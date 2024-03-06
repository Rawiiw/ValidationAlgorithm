import matplotlib.pyplot as plt
import numpy as np
import imageio

from plot_data import get_image_data


def plot_and_show_data(data, satellite_choice):
    # Вывод графика
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

    # Вывод значений
    print("Time and Temperature Values:")
    print(get_image_data(data, satellite_choice).to_string())
