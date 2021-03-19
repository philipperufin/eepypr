import ee
import fct.stm
import datetime
import json
import geopandas as gpd

ee.Initialize()

roi_shp = gpd.read_file(r'P:\SUSADICA\vector\roi\roi_prv_v03.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

years = range(2015, 2020)

for year in years:
        startDate = datetime.datetime(int(year), 4, 1)
        endDate = datetime.datetime(int(year), 10, 31)

        cnt = fct.stm.LND_NUM(startDate, endDate)

        # export to drive
        task = ee.batch.Export.image.toDrive(**{
                'image': cnt,
                'folder': 'SUSADICA_v03',
                'description': 'susadica_cso_apr-nov_' + str(year),
                'scale': 30,
                'region': roi,
                'maxPixels': 1e13
            })
        task.start()