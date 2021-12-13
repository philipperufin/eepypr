import json
import datetime
import geopandas as gpd
import ee
import fct.stm

ee.Initialize()

# define roi
roi_shp = gpd.read_file(r'D:\PRJ_TMP\FSDA\data\vector\adm\north_moz_adm0_sp_buffer_050deg.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# define period
startDate = datetime.datetime(2020, 9, 1)
endDate = datetime.datetime(2020, 12, 31)

# create reference median nir
s1 = fct.sen.SEN(startDate, endDate, cdi=True).select('nir').reduce(ee.Reducer.percentile([50])).rename('nir_med').toInt16()

task = ee.batch.Export.image.toAsset(**{
    'image': s1,
    'scale': 10,
    'region': roi,
    'description': 'sen4coreg_2020-09-12',
    'assetId': 'users/philipperufin/sen4reg_cdi_2020-09-12',
    'maxPixels': 1e13
})
task.start()

# define period
startDate = datetime.datetime(2021, 1, 1)
endDate = datetime.datetime(2021, 4, 30)

# create reference median nir
s2 = fct.sen.SEN(startDate, endDate, cdi=True).select('nir').reduce(ee.Reducer.percentile([50])).rename('nir_med').toInt16()

task = ee.batch.Export.image.toAsset(**{
    'image': s2,
    'scale': 10,
    'region': roi,
    'description': 'sen4coreg_2021-01-04',
    'assetId': 'users/philipperufin/sen4reg_cdi_2021-01-04',
    'maxPixels': 1e13
})
task.start()

# define period
startDate = datetime.datetime(2021, 5, 1)
endDate = datetime.datetime(2021, 8, 31)

# create reference median nir
s3 = fct.sen.SEN(startDate, endDate, cdi=True).select('nir').reduce(ee.Reducer.percentile([50])).rename('nir_med').toInt16()

task = ee.batch.Export.image.toAsset(**{
    'image': s3,
    'scale': 10,
    'region': roi,
    'description': 'sen4coreg_2021-05-08',
    'assetId': 'users/philipperufin/sen4reg_cdi_2021-05-08',
    'maxPixels': 1e13
})
task.start()