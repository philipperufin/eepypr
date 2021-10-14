import ee
import fct.stm
import fct.txt
import fct.psm
import datetime
import json
import geopandas as gpd

# mask function
def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)

ee.Initialize()


# roi 2 ee geometry
site = 'niassa'
roi_path = r'D:\PRJ_TMP\FSDA\data\vector\adm\niassa_adm1.shp'
roi_shp = gpd.read_file(roi_path)
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

############################################ using registration
# create stm for three seasons
startDate = datetime.datetime(2020, 11, 30)
endDate = datetime.datetime(2021, 3, 31)
stm_s01 = fct.stm.PSM_STM(startDate, endDate, roi_path=roi_path, register=True) \
    .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_ndvi_p50',
            's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_ndvi_std',
            's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_ndvi_p25',
            's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_ndvi_p75',
            's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_ndvi_iqr')

startDate = datetime.datetime(2021, 4, 30)
endDate = datetime.datetime(2021, 8, 31)
stm_s02 = fct.stm.PSM_STM(startDate, endDate, roi_path=roi_path, register=True) \
    .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_ndvi_p50',
            's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_ndvi_std',
            's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_ndvi_p25',
            's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_ndvi_p75',
            's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_ndvi_iqr')

startDate = datetime.datetime(2020, 8, 31)
endDate = datetime.datetime(2021, 8, 31)
stm_s03 = fct.stm.PSM_STM(startDate, endDate, roi_path=roi_path, register=True) \
    .rename('s03_b_p50', 's03_g_p50', 's03_r_p50', 's03_n_p50', 's03_ndvi_p50',
            's03_b_std', 's03_g_std', 's03_r_std', 's03_n_std', 's03_ndvi_std',
            's03_b_p25', 's03_g_p25', 's03_r_p25', 's03_n_p25', 's03_ndvi_p25',
            's03_b_p75', 's03_g_p75', 's03_r_p75', 's03_n_p75', 's03_ndvi_p75',
            's03_b_iqr', 's03_g_iqr', 's03_r_iqr', 's03_n_iqr', 's03_ndvi_iqr')

# create multi-season image and cast to integer!
#stm_image = ee.Image([stm_s01, stm_s02, stm_s03]).toInt16()
#stm_image = ee.Image([stm_s01]).toInt16()
stm_image = ee.Image([stm_s02]).toInt16()
#stm_image = ee.Image([stm_s03]).toInt16()

if False:
    # add textures and texture ndis
    txt_bds = ['s03_ndvi_p25', 's03_ndvi_p75']
    txt_rds = [20, 50, 100]
    for bd in txt_bds:
        for rd in txt_rds:
            stm_image = fct.txt.TXT(stm_image, bd, rd)

# mask
#stm_image = maskInside(stm_image, roi)

# export as asset
task = ee.batch.Export.image.toAsset(**{
    'image': stm_image,
    'scale': 4.77,
    'region': roi,
    'description': 'fsda_' + site + '_psm_coreg_stm_202105-202108',
    'assetId': 'users/philipperufin/fsda_' + site + '_psm_coreg_stm_202105-202108',
    'maxPixels': 1e13
})
task.start()

task.status()