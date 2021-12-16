import ee
import fct.lnd
import geopandas as gpd
import datetime
import json
def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)

ee.Initialize()

startDate = datetime.datetime(2014, 1, 1)
endDate = datetime.datetime(2019, 12, 31)

roi_shp = gpd.read_file(r'D:\Seafile\Meine Bibliothek\research\theses\MSc_Franziska_Walther\extent_rough.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

lnd = fct.lnd.LND(startDate, endDate, roi=roi).select('evi')
ids = lnd.aggregate_array('LANDSAT_ID').getInfo()

for id in ids:
    print(id)
    image = lnd.filterMetadata('LANDSAT_ID', 'equals', id)\
        .first()
    description = id
    folder = 'FW_EVI_2014-2020'
    scale = 30
    task = ee.batch.Export.image.toDrive(**{
        'image': image,
        'description': description,
        'folder': folder,
        'scale': scale,
        'crs': 'EPSG:32737',
        'maxPixels': 1e13
    })
    task.start()
