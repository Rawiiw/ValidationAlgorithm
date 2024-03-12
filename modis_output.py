import ee
import pandas as pd

ee.Authenticate()
ee.Initialize(project='ee-kosinova')

Zotino = [89.3508, 60.8008]
Cherskiy = [161.3392, 68.61472]
Chokurdakh = [147.4943, 70.82914]
Fyodorovskoe = [32.92208, 56.46153]

# Show points on the map
points = ee.Geometry.MultiPoint([
    ee.Geometry.Point(Zotino),
    ee.Geometry.Point(Cherskiy),
    ee.Geometry.Point(Chokurdakh),
    ee.Geometry.Point(Fyodorovskoe)
])


# Declare image collection
lst = ee.ImageCollection('MODIS/006/MYD11A1') \
    .filterBounds(points) \
    .filterDate('2004-01-01', '2004-12-31')

# Sample images with properties as added bands and values scaled appropriately
def sample(image):
    image = image.addBands(image.metadata("system:time_start"))
    image = image.addBands(image.select('LST_Day_1km').multiply(0.02).subtract(273.15), overwrite=True)
    image = image.addBands(image.select('LST_Night_1km').multiply(0.02).subtract(273.15), overwrite=True)
    image = image.addBands(image.select('Night_view_time').multiply(0.1), overwrite=True)
    image = image.addBands(image.select('Day_view_time').multiply(0.1), overwrite=True)
    image = image.addBands(image.select('Night_view_angle').add(-65), overwrite=True)
    image = image.addBands(image.select('Day_view_angle').add(-65), overwrite=True)
    image = image.addBands(image.select('Emis_31').multiply(0.002).add(0.49), overwrite=True)
    image = image.addBands(image.select('Emis_32').multiply(0.002).add(0.49), overwrite=True)
    image = image.addBands(image.select('Clear_day_cov').multiply(0.005), overwrite=True)
    image = image.addBands(image.select('Clear_night_cov').multiply(0.005), overwrite=True)
    return image.sampleRegions(collection=points, scale=1000)

# Generate the table as a feature collection
featureCollection = ee.FeatureCollection(lst.map(sample)).flatten()

# Print time given as floating point number of hours as 'hh:mm'
def as_time_string(v):
    return ee.String(v.floor().int().format('%02d')) \
        .cat(':') \
        .cat(ee.String(v.subtract(v.floor()).multiply(60).int().format('%02d'))) \
        .cat(':00')

# Replace numeric values with formatted strings
def replace_numbers_by_strings(feature):
    d = ee.Date(feature.get('system:time_start'))
    dt = as_time_string(ee.Number(feature.get('Day_view_time')))
    nt = as_time_string(ee.Number(feature.get('Night_view_time')))
    dtemp = ee.Number(feature.get('LST_Day_1km')).format('%6.2f')
    ntemp = ee.Number(feature.get('LST_Night_1km')).format('%6.2f')
    emis31 = ee.Number(feature.get('Emis_31')).format('%6.2f')
    emis32 = ee.Number(feature.get('Emis_32')).format('%6.2f')
    day_cov = ee.Number(feature.get('Clear_day_cov')).format('%6.2f')
    night_cov = ee.Number(feature.get('Clear_night_cov')).format('%6.2f')
    day_angle = ee.Number(feature.get('Day_view_angle')).format('%6.2f')
    night_angle = ee.Number(feature.get('Night_view_angle')).format('%6.2f')
    return feature.set({
        'Night_view_time': nt,
        'Day_view_time': dt,
        'Night_view_angle': night_angle,
        'Day_view_angle': day_angle,
        'LST_Day_1km': dtemp,
        'LST_Night_1km': ntemp,
        'Emis_31': emis31,
        'Emis_32': emis32,
        'Clear_day_cov': day_cov,
        'Clear_night_cov': night_cov,
        'date': d.format('YYYY-MM-dd')
    })

# Declare columns of the output dataset
columns = [
    "LST_Day_1km",
    "QC_Day",
    "Day_view_time",
    "Day_view_angle",
    "LST_Night_1km",
    "QC_Night",
    "Night_view_time",
    "Night_view_angle",
    "Emis_31",
    "Emis_32",
    "Clear_day_cov",
    "Clear_night_cov",
    "date",
    "name"
]
# Select relevant columns and replace numeric values with formatted strings
datatable = featureCollection.map(replace_numbers_by_strings).select(columns)

# Convert feature collection to pandas DataFrame
# Convert feature collection to pandas DataFrame
df = pd.DataFrame([feature['properties'] for feature in datatable.getInfo()['features']])

# Save DataFrame to CSV
df.to_csv("output.csv", index=False)

# Save DataFrame to Excel
excel_file = "output.xlsx"
df.to_excel(excel_file, index=False)

print("CSV and Excel files saved successfully!")
