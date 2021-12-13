import ee
import numpy as np
import fct.txt
import fct.psm
import fct.exp
import datetime
import json
import geopandas as gpd

ee.Initialize()

############################################
# open grid and get cell ids
roi_path = r'D:\PRJ_TMP\FSDA\data\vector\roi\grid\grid_space_030deg_buffer_001deg.shp'
roi_shp = gpd.read_file(roi_path)
fids = roi_shp['id']

# update completed tile ids
done = [22, 46, 53, 54, 74]
done = [61, 81, 87, 95, 109, 116, 130, 150, 170, 175, 177, 186, 201, 213, 216, 217, 221, 228, 236,
        255, 266, 280, 282, 321, 322, 330, 333, 335, 340, 347, 350, 352, 362, 381, 389, 404, 410]
fids = fids[~np.in1d(fids, done)]
fids = [53, 74, 109]
############################################
# loop to create stm and store as asset
for i in fids:
    # read tile by id
    tile = roi_shp[roi_shp['id']==i]
    g = json.loads(tile.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    roi_poly = ee.Geometry.Polygon(coords)

    ############################################
    # create co-registered NICFI collection
    # define time ranges for three seasons following Bey et al. 2020

    # create first season stm
    s1_startDate = datetime.datetime(2020, 9, 1)
    s1_endDate = datetime.datetime(2020, 12, 31)
    s1_coll = fct.psm.PSM_REG2SEN(s1_startDate, s1_endDate, roi=roi_poly, ref_img='users/philipperufin/sen4reg_cdi_2020-09-12').select('green', 'red', 'nir', 'ndvi')

    s1_p50 = s1_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s1_green_p50', 's1_red_p50', 's1_nir_p50', 's1_ndvi_p50')
    s1_p75 = s1_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s1_ndvi_p75')

    # create second season stm
    s2_startDate = datetime.datetime(2021, 1, 1)
    s2_endDate = datetime.datetime(2021, 4, 30)
    s2_coll = fct.psm.PSM_REG2SEN(s2_startDate, s2_endDate, roi=roi_poly, ref_img='users/philipperufin/sen4reg_cdi_2021-01-04').select('green', 'red', 'nir', 'ndvi')

    s2_p50 = s2_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s2_green_p50', 's2_red_p50', 's2_nir_p50', 's2_ndvi_p50')
    s2_p75 = s2_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s2_ndvi_p75')

    # create third season stm
    s3_startDate = datetime.datetime(2021, 5, 1)
    s3_endDate = datetime.datetime(2021, 8, 31)
    s3_coll = fct.psm.PSM_REG2SEN(s3_startDate, s3_endDate, roi=roi_poly, ref_img='users/philipperufin/sen4reg_cdi_2021-05-08').select('green', 'red', 'nir', 'ndvi')

    s3_p50 = s3_coll.reduce(ee.Reducer.percentile([50])) \
        .rename('s3_green_p50', 's3_red_p50', 's3_nir_p50', 's3_ndvi_p50')
    s3_p75 = s3_coll.select('ndvi').reduce(ee.Reducer.percentile([75])) \
        .rename('s3_ndvi_p75')


    # create multi-season image and cast to integer!
    image = ee.Image([s1_p50, s1_p75, s2_p50, s2_p75, s3_p50, s3_p75]).toInt16()

    ############################################
    # add texture and ndi metrics
    # based on dry-season NDVI median
    if True:
        # add textures and texture ndis
        txt_bds = ['s3_ndvi_p50']
        txt_rds = [20, 100]
        for bd in txt_bds:
            for rd in txt_rds:
                image = fct.txt.TXT(image, bd, rd)

    ############################################
    # export as asset
    if True:
        task = ee.batch.Export.image.toAsset(**{
            'image': image,
            'scale': 4.77,
            'region': roi_poly,
            'description': 'fsda_tile_03deg_' + f'{int(i):03}' + '_psm_reg2sen_3season_stm',
            'assetId': 'users/philipperufin/fsda_tiles/fsda_tile_03deg_' + f'{int(i):03}' + '_psm_reg2sen_3season_stm',
            'maxPixels': 1e13
        })
        task.start()

        task.status()

############################################
# move to drive
if False:
    # export to drive
    for i in done:
        image = ee.Image('users/philipperufin/fsda_tiles/fsda_tile_03deg_' + f'{int(i):03}' + '_psm_coreg_3season_stm')
        # image = maskInside(image, roi)
        description = 'fsda_tile_03deg_' + f'{int(i):03}' + '_psm_coreg_3season_stm'
        folder = 'NICFI_LC_03deg_tiles'
        scale = 4.77
        fct.exp.exportDrive(image, description, folder, scale)

############################################
# delete assets
if False:
    #done = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 27, 35, 61]
    for i in done:
        ee.data.deleteAsset('users/philipperufin/fsda_tiles/fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm')
