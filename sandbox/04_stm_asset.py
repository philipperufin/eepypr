import ee
import fct.stm
import fct.txt
import datetime
import json
import pandas as pd
import geopandas as gpd

# mask function
def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)

ee.Initialize()

# years from points
#point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\all\pts.shp'
#points = gpd.read_file(point_shape)
#years = pd.unique(points ['year'])
# years from list
years = [1987, 1996, 2008, 2018]

# roi 2 ee geometry
roi_shp = gpd.read_file(r'P:\SUSADICA\vector\roi\roi_training_v03.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# for all years
for year in years:
    # create stm for three seasons
    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 7, 31)
    stm_s01 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50', 's01_ndvi_p50',
                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std', 's01_ndvi_std',
                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25', 's01_ndvi_p25',
                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75', 's01_ndvi_p75',
                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr', 's01_ndvi_iqr')

    startDate = datetime.datetime(int(year), 8, 1)
    endDate = datetime.datetime(int(year), 10, 31)
    stm_s02 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50', 's02_ndvi_p50',
                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std', 's02_ndvi_std',
                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25', 's02_ndvi_p25',
                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75', 's02_ndvi_p75',
                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr', 's02_ndvi_iqr')

    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 10, 31)
    stm_s03 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s03_b_p50', 's03_g_p50', 's03_r_p50', 's03_n_p50', 's03_sw1_p50', 's03_sw2_p50', 's03_ndvi_p50',
                's03_b_std', 's03_g_std', 's03_r_std', 's03_n_std', 's03_sw1_std', 's03_sw2_std', 's03_ndvi_std',
                's03_b_p25', 's03_g_p25', 's03_r_p25', 's03_n_p25', 's03_sw1_p25', 's03_sw2_p25', 's03_ndvi_p25',
                's03_b_p75', 's03_g_p75', 's03_r_p75', 's03_n_p75', 's03_sw1_p75', 's03_sw2_p75', 's03_ndvi_p75',
                's03_b_iqr', 's03_g_iqr', 's03_r_iqr', 's03_n_iqr', 's03_sw1_iqr', 's03_sw2_iqr', 's03_ndvi_iqr')

    # create multi-season image and cast to integer!
    stm_image = ee.Image([stm_s01, stm_s02, stm_s03]).toInt16()

    # add textures and texture ndis
    txt_bds = ['s02_ndvi_p25', 's02_ndvi_p75', 's03_ndvi_p25', 's03_ndvi_p75']
    txt_rds = [150, 300, 900]
    for bd in txt_bds:
        for rd in txt_rds:
            stm_image = fct.txt.TXT(stm_image, bd, rd)

    # mask
    stm_image = maskInside(stm_image, roi)

    # export as asset
    task = ee.batch.Export.image.toAsset(**{
        'image': stm_image,
        'scale': 30,
        'region': roi,
        'description': 'susadica_sstm_' + str(year),
        'assetId': 'users/philipperufin/susadica_sstm_' + str(year),
        'maxPixels': 1e13
    })
    task.start()

task.status()