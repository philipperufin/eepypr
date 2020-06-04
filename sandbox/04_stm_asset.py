import ee
import fct.stm
import datetime
import json
import numpy as np
import ogr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, shape, Point

ee.Initialize()

point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\all\pts.shp'
points = gpd.read_file(point_shape)
years = pd.unique(points ['year'])

roi_shp = gpd.read_file(r'C:\Users\geo_phru\Desktop\SUSADICA\roi\roi_training.shp')

# ee geometry
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

years = [1987, 1996, 2008, 2018]

def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)


# for all defined years
for year in years:
    # create stm for both seasons
#    startDate = datetime.datetime(int(year), 4, 1)
#    endDate = datetime.datetime(int(year), 7, 15)
#    stm_s01 = fct.stm.LND_STM(startDate, endDate) \
#        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
#                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
#                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
#                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
#                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
#                's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn')

#    startDate = datetime.datetime(int(year), 7, 16)
#    endDate = datetime.datetime(int(year), 9, 30)
#    stm_s02 = fct.stm.LND_STM(startDate, endDate) \
#        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
#                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
#                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
#                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
#                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
#                's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn')

    # create two-season image and cast to integer!
#    stm_image = ee.Image([stm_s01, stm_s02]).toInt16()
#    stm_image = maskInside(stm_image, roi)

# annual STMs
    startDate = datetime.datetime(int(year), 1, 1)
    endDate = datetime.datetime(int(year), 12, 31)
    stm_ann = fct.stm.LND_STM(startDate, endDate) \
        .rename('ann_b_p50', 'ann_g_p50', 'ann_r_p50', 'ann_n_p50', 'ann_sw1_p50', 'ann_sw2_p50',
                'ann_b_std', 'ann_g_std', 'ann_r_std', 'ann_n_std', 'ann_sw1_std', 'ann_sw2_std',
                'ann_b_p25', 'ann_g_p25', 'ann_r_p25', 'ann_n_p25', 'ann_sw1_p25', 'ann_sw2_p25',
                'ann_b_p75', 'ann_g_p75', 'ann_r_p75', 'ann_n_p75', 'ann_sw1_p75', 'ann_sw2_p75',
                'ann_b_iqr', 'ann_g_iqr', 'ann_r_iqr', 'ann_n_iqr', 'ann_sw1_iqr', 'ann_sw2_iqr',
                'ann_b_imn', 'ann_g_imn', 'ann_r_imn', 'ann_n_imn', 'ann_sw1_imn', 'ann_sw2_imn')

# create two-season image and cast to integer!
    stm_image = ee.Image([stm_ann]).toInt16()
    stm_image = maskInside(stm_image, roi)

    # export as asset
    task = ee.batch.Export.image.toAsset(**{
        'image': stm_image,
        'scale': 30,
        'region': roi,
        'description': 'susadica_stm_ann_' + str(year),
        'assetId': 'users/philipperufin/susadica_stm_ann_' + str(year),
        'maxPixels': 1e13
    })
    task.start()

task.status()