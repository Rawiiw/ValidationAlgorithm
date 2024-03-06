import imageio
from matplotlib import pyplot as plt

from plot_data import get_image_data


def create_gif(data_list, satellite_choice, output_filename='output.gif'):
    images = []
    for data in data_list:
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

        # Сохранение графика в виде изображения
        filename = 'temp_image.png'
        plt.savefig(filename)
        images.append(imageio.imread(filename))
        plt.close()

    # Создание GIF из изображений
    imageio.mimsave(output_filename, images, duration=1)  # duration - задержка между кадрами в секундах
