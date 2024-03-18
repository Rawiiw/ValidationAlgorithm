import ee


def get_image_collection(coordinates, date_start, date_end):
    point = ee.Geometry.Point(coordinates)
    lst = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
        .filterBounds(point) \
        .filterDate(date_start, date_end)
    return lst


def sample_image(image, point):
    image = image.addBands(image.metadata("system:time_start"))
    return image.sampleRegions(collection=point, scale=30)


def get_feature_collection(lst, point):
    featureCollection = ee.FeatureCollection(lst.map(lambda image: sample_image(image, point))).flatten()
    return featureCollection


def replace_numbers_by_strings(feature):
    def as_time_string(v):
        return ee.String(v.floor().int().format('%02d')) \
            .cat(':') \
            .cat(ee.String(v.subtract(v.floor()).multiply(60).int().format('%02d'))) \
            .cat(':00')

    d = ee.Date(feature.get('system:time_start'))
    return feature.set({
        'date': d.format('YYYY-MM-dd'),
        'B1': ee.Number(feature.get('B1')).format('%6.2f'),
        'B2': ee.Number(feature.get('B2')).format('%6.2f'),
        'B3': ee.Number(feature.get('B3')).format('%6.2f'),
        'B4': ee.Number(feature.get('B4')).format('%6.2f'),
        'B5': ee.Number(feature.get('B5')).format('%6.2f'),
        'B6': ee.Number(feature.get('B6')).format('%6.2f'),
        'B7': ee.Number(feature.get('B7')).format('%6.2f')
    })


def get_datatable(featureCollection):
    columns = [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "date",
    ]
    datatable = featureCollection.map(replace_numbers_by_strings).select(columns)
    return datatable
