import ee
import fct.stm
import datetime
import json
import geopandas as gpd
import pandas as pd
ee.Initialize()

###########################################################
###########################################################
# local shapefile with training points
point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\all\pts.shp'
points = gpd.read_file(point_shape)

points.crs
points = points.to_crs("EPSG:4326")

pd.unique(points["class"])
points["class"].value_counts()

# set first iteration
first = True
years = [1987, 1996, 2008, 2018]
year = 2018
# iterate over years in tile
for year in years:
    print(int(year))
    # subset points in year
    typts = points.loc[points['year'] == year]
    print(typts["class"].value_counts())
    #for col in typts.columns:
    #    print(col)
    #typts.head()
    # remove other attributes
    typts = typts.drop(['poly_ID', 'poly', 'year', 'ID', 'layer', 'path'], axis=1)

    ###########################################################
    ###########################################################
    # create geojson from geopandas
    # from https://gis.stackexchange.com/questions/333791/accessing-a-shapefile-with-googleearthengine-api-invalid-geojson-geometry
    point_f = []
    for i in range(typts.shape[0]):
        geom = typts.iloc[i:i + 1, :]
        jsonDict = eval(geom.to_json())
        geojsonDict = jsonDict['features'][0]
        point_f.append(ee.Feature(geojsonDict))

    # make feature collection
    ptsfc = ee.FeatureCollection(point_f)

    ###########################################################
    ###########################################################
    # stm asset
    stm_sea = ee.Image('users/philipperufin/susadica_stm_' + str(year))
    stm_ann = ee.Image('users/philipperufin/susadica_stm_ann_' + str(year))
    stm_image = ee.Image([stm_sea, stm_ann])
    ###########################################################
    ###########################################################
    # sample point locations
    stm = stm_image.sampleRegions(ptsfc, ['class'], 30)

    # merge years
    if not first:
        tg_stm = stm.merge(stm)

    if first:
        tg_stm = stm
        first = False

###########################################################
###########################################################
# classifier
bands = ['s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
         's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
         's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
         's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
         's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
         's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn',

         's02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
         's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
         's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
         's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
         's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
         's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn',

         'ann_b_p50', 'ann_g_p50', 'ann_r_p50', 'ann_n_p50', 'ann_sw1_p50', 'ann_sw2_p50',
         'ann_b_std', 'ann_g_std', 'ann_r_std', 'ann_n_std', 'ann_sw1_std', 'ann_sw2_std',
         'ann_b_p25', 'ann_g_p25', 'ann_r_p25', 'ann_n_p25', 'ann_sw1_p25', 'ann_sw2_p25',
         'ann_b_p75', 'ann_g_p75', 'ann_r_p75', 'ann_n_p75', 'ann_sw1_p75', 'ann_sw2_p75',
         'ann_b_iqr', 'ann_g_iqr', 'ann_r_iqr', 'ann_n_iqr', 'ann_sw1_iqr', 'ann_sw2_iqr',
         'ann_b_imn', 'ann_g_imn', 'ann_r_imn', 'ann_n_imn', 'ann_sw1_imn', 'ann_sw2_imn']

classifier = ee.Classifier.randomForest(250).train(tg_stm, 'class', bands)
#print('RF accuracy: ', classifier.confusionMatrix().accuracy().getInfo())
print('RF error matrix: ', classifier.confusionMatrix().getInfo())

###########################################################
###########################################################

# ee roi geometry
roi_shp = gpd.read_file(r'C:\Users\geo_phru\Desktop\SUSADICA\roi\roi_buffer.shp')

g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# stm features
for year in range(1987, 2020):

    startDate = datetime.datetime(year, 4, 1)
    endDate = datetime.datetime(year, 7, 15)
    stm_s01 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
                's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn')

    startDate = datetime.datetime(year, 7, 16)
    endDate = datetime.datetime(year, 10, 30)
    stm_s02 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
                's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn')

    startDate = datetime.datetime(int(year), 1, 1)
    endDate = datetime.datetime(int(year), 12, 31)
    stm_ann = fct.stm.LND_STM(startDate, endDate) \
        .rename('ann_b_p50', 'ann_g_p50', 'ann_r_p50', 'ann_n_p50', 'ann_sw1_p50', 'ann_sw2_p50',
                'ann_b_std', 'ann_g_std', 'ann_r_std', 'ann_n_std', 'ann_sw1_std', 'ann_sw2_std',
                'ann_b_p25', 'ann_g_p25', 'ann_r_p25', 'ann_n_p25', 'ann_sw1_p25', 'ann_sw2_p25',
                'ann_b_p75', 'ann_g_p75', 'ann_r_p75', 'ann_n_p75', 'ann_sw1_p75', 'ann_sw2_p75',
                'ann_b_iqr', 'ann_g_iqr', 'ann_r_iqr', 'ann_n_iqr', 'ann_sw1_iqr', 'ann_sw2_iqr',
                'ann_b_imn', 'ann_g_imn', 'ann_r_imn', 'ann_n_imn', 'ann_sw1_imn', 'ann_sw2_imn')

    stm_image = ee.Image([stm_s01, stm_s02, stm_ann])

    map = stm_image.classify(classifier).toInt8()
    prb = stm_image.classify(classifier.setOutputMode('PROBABILITY')).toInt8()

    # export to drive
#    task = ee.batch.Export.image.toDrive(**{
#        'image': map,
#        'folder': 'SUSADICA_maps',
#        'description': 'susadica_tgm_' + str(year),
#        'scale': 30,
#        'region': roi,
#        'maxPixels': 1e13
#    })
#    task.start()

    # export as asset
    task = ee.batch.Export.image.toAsset(**{
        'image': map,
        'scale': 30,
        'region': roi,
        'description': 'susadica_map_v02_' + str(year),
        'assetId': 'users/philipperufin/susadica_map_v02_' + str(year),
        'maxPixels': 1e13
    })
    task.start()

    task = ee.batch.Export.image.toAsset(**{
        'image': prb,
        'scale': 30,
        'region': roi,
        'description': 'susadica_prb_v02_' + str(year),
        'assetId': 'users/philipperufin/susadica_prb_v02_' + str(year),
        'maxPixels': 1e13
    })
    task.start()


task.status()