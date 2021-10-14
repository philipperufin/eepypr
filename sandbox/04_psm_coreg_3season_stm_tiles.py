import ee
import fct.stm
import fct.txt
import fct.psm
import fct.exp
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
roi_path = r'D:\PRJ_TMP\FSDA\data\vector\roi\grid\grid_space_100deg_overlay_005deg.shp'
roi_shp = gpd.read_file(roi_path)
fids = roi_shp['id']
i=1
for i in fids:
    tile = roi_shp[roi_shp['id']==i]
    g = json.loads(tile.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    roi = ee.Geometry.Polygon(coords)

    # coreg collection
    startDate = datetime.datetime(2020, 8, 31)
    endDate = datetime.datetime(2021, 8, 31)
    collection = fct.psm.PSM_COREG(startDate, endDate, roi_path, property='system:index',
                                   reference_id='planet_medres_normalized_analytic_2021-05_mosaic')
    coll = collection.select('green', 'red', 'nir', 'ndvi')

    ############################################
    # define time ranges for three seasons following Bey et al. 2020

    s1_startDate = datetime.datetime(2020, 8, 30)
    s1_endDate = datetime.datetime(2020, 12, 31)

    s2_startDate = datetime.datetime(2020, 12, 31)
    s2_endDate = datetime.datetime(2021, 4, 30)

    s3_startDate = datetime.datetime(2021, 4, 30)
    s3_endDate = datetime.datetime(2021, 8, 31)

    ############################################
    # create stm for three seasons

    s1_coll = coll.filter(ee.Filter.date(s1_startDate, s1_endDate))
    s1_p50 = s1_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s1_green_p50', 's1_red_p50', 's1_nir_p50', 's1_ndvi_p50')
    s1_p75 = s1_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s1_ndvi_p75')

    s2_coll = coll.filter(ee.Filter.date(s2_startDate, s2_endDate))
    s2_p50 = s2_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s2_green_p50', 's2_red_p50', 's2_nir_p50', 's2_ndvi_p50')
    s2_p75 = s2_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s2_ndvi_p75')

    s3_coll = coll.filter(ee.Filter.date(s3_startDate, s3_endDate))
    s3_p50 = s3_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s3_green_p50', 's3_red_p50', 's3_nir_p50', 's3_ndvi_p50')
    s3_p75 = s3_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s3_ndvi_p75')

    # create multi-season image and cast to integer!
    image = ee.Image([s1_p50, s1_p75, s2_p50, s2_p75, s3_p50, s3_p75]).toInt16()

    if True:
        # add textures and texture ndis
        txt_bds = ['s3_ndvi_p50']
        txt_rds = [20, 100]
        for bd in txt_bds:
            for rd in txt_rds:
                image = fct.txt.TXT(image, bd, rd)


    # export as asset
    if True:
        task = ee.batch.Export.image.toAsset(**{
            'image': image,
            'scale': 4.77,
            'region': roi,
            'description': 'fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm',
            'assetId': 'users/philipperufin/fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm',
            'maxPixels': 1e13
        })
        task.start()

        task.status()

    if False:
        # export to drive
        ### if task.status() == :
        description = 'fsda_' + site + '_psm_coreg_3season_stm',
        folder = 'NICFI_LC'
        scale = 4.77
        fct.exp.exportDrive(image, description, folder, scale)

