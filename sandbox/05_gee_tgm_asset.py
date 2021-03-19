import ee
import fct.stm
import fct.txt
import datetime
import json
import geopandas as gpd
import pandas as pd
import time

sleepytime = False
if sleepytime == True:
    print('sleeping')
    time.sleep(60*60)
    print('starting')

ee.Initialize()

###########################################################
###########################################################
# local shapefile with training points
point_shape = r'P:\SUSADICA\train\v03\final\pts_v03.shp'
points = gpd.read_file(point_shape)

points.crs
points = points.to_crs("EPSG:4326")

pd.unique(points["class"])
points["class"].value_counts()

add_elevation = True
add_latlon = True

# set first iteration
first = True
years = [1987, 1996, 2008, 2018]
predict_years = range(1987, 2020)

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
    stm_image = ee.Image('users/philipperufin/susadica_sstm_' + str(year))

    ###########################################################
    ###########################################################
    # add srtm/slope
    if add_elevation == True:
        srtm = ee.Image("NASA/NASADEM_HGT/001").select('elevation')
        slope = ee.Terrain.slope(srtm).multiply(100).rename('slope')
        stm_image = ee.Image([stm_image, srtm, slope])

    # add lat lon layers
    if add_latlon == True:
        crd_image = ee.Image.pixelLonLat()
        stm_image = ee.Image([stm_image, crd_image])
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
# define band names
bands = ['s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50', 's01_evi_p50',
         #'s01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std', 's01_evi_std',
         's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25', 's01_evi_p25',
         's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75', 's01_evi_p75',
         #'s01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr', 's01_evi_iqr',

         's02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50', 's02_evi_p50',
         's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std', 's02_evi_std',
         's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25', 's02_evi_p25',
         's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75', 's02_evi_p75',
         's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr', 's02_evi_iqr',

         's03_b_p50', 's03_g_p50', 's03_r_p50', 's03_n_p50', 's03_sw1_p50', 's03_sw2_p50', 's03_evi_p50',
         's03_b_std', 's03_g_std', 's03_r_std', 's03_n_std', 's03_sw1_std', 's03_sw2_std', 's03_evi_std',
         's03_b_p25', 's03_g_p25', 's03_r_p25', 's03_n_p25', 's03_sw1_p25', 's03_sw2_p25', 's03_evi_p25',
         's03_b_p75', 's03_g_p75', 's03_r_p75', 's03_n_p75', 's03_sw1_p75', 's03_sw2_p75', 's03_evi_p75',
         's03_b_iqr', 's03_g_iqr', 's03_r_iqr', 's03_n_iqr', 's03_sw1_iqr', 's03_sw2_iqr', 's03_evi_iqr',

         's02_evi_p25_p50_150', 's02_evi_p25_p50_150ndi',
         's02_evi_p25_p50_300', 's02_evi_p25_p50_300ndi',
         's02_evi_p25_p50_900', 's02_evi_p25_p50_900ndi',

         's02_evi_p75_p50_150', 's02_evi_p75_p50_150ndi',
         's02_evi_p75_p50_300', 's02_evi_p75_p50_300ndi',
         's02_evi_p75_p50_900', 's02_evi_p75_p50_900ndi',

         's03_evi_p25_p50_150', 's03_evi_p25_p50_150ndi',
         's03_evi_p25_p50_300', 's03_evi_p25_p50_300ndi',
         's03_evi_p25_p50_900', 's03_evi_p25_p50_900ndi',

         's03_evi_p75_p50_150', 's03_evi_p75_p50_150ndi',
         's03_evi_p75_p50_300', 's03_evi_p75_p50_300ndi',
         's03_evi_p75_p50_900', 's03_evi_p75_p50_900ndi',

         'elevation', 'slope', 'longitude', 'latitude']

classifier = ee.Classifier.randomForest(250).train(tg_stm, 'class', bands)
#print('RF accuracy: ', classifier.confusionMatrix().accuracy().getInfo())
#print('RF error matrix: ', classifier.confusionMatrix().getInfo())

###########################################################
###########################################################

# ee roi geometry
roi_shp = gpd.read_file(r'P:\SUSADICA\vector\roi\roi_prv_v03.shp')

g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# stm features
for year in predict_years:
    print('generating sstm for ' + str(year))
    # create stm for three seasons
    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 7, 31)
    stm_s01 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50', 's01_evi_p50',
                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std', 's01_evi_std',
                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25', 's01_evi_p25',
                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75', 's01_evi_p75',
                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr', 's01_evi_iqr')

    startDate = datetime.datetime(int(year), 8, 1)
    endDate = datetime.datetime(int(year), 10, 31)
    stm_s02 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50', 's02_evi_p50',
                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std', 's02_evi_std',
                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25', 's02_evi_p25',
                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75', 's02_evi_p75',
                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr', 's02_evi_iqr')

    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 10, 31)
    stm_s03 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s03_b_p50', 's03_g_p50', 's03_r_p50', 's03_n_p50', 's03_sw1_p50', 's03_sw2_p50', 's03_evi_p50',
                's03_b_std', 's03_g_std', 's03_r_std', 's03_n_std', 's03_sw1_std', 's03_sw2_std', 's03_evi_std',
                's03_b_p25', 's03_g_p25', 's03_r_p25', 's03_n_p25', 's03_sw1_p25', 's03_sw2_p25', 's03_evi_p25',
                's03_b_p75', 's03_g_p75', 's03_r_p75', 's03_n_p75', 's03_sw1_p75', 's03_sw2_p75', 's03_evi_p75',
                's03_b_iqr', 's03_g_iqr', 's03_r_iqr', 's03_n_iqr', 's03_sw1_iqr', 's03_sw2_iqr', 's03_evi_iqr')

    # create multi-season image and cast to integer!
    stm_image = ee.Image([stm_s01, stm_s02, stm_s03]).toInt16()

    # add textures and texture ndis
    txt_bds = ['s02_evi_p25', 's02_evi_p75', 's03_evi_p25', 's03_evi_p75']
    txt_rds = [150, 300, 900]
    for bd in txt_bds:
        for rd in txt_rds:
            stm_image = fct.txt.TXT(stm_image, bd, rd)

    if add_elevation == True:
        srtm = ee.Image("NASA/NASADEM_HGT/001").select('elevation').toInt16()
        slope = ee.Terrain.slope(srtm).multiply(100).rename('slope').toInt16()
        stm_image = ee.Image([stm_image, srtm, slope])

    # add lat lon layers
    if add_latlon == True:
        crd_image = ee.Image.pixelLonLat()
        stm_image = ee.Image([stm_image, crd_image])

    print('setting up prediction for ' + str(year))
    map = stm_image.classify(classifier).toInt8()

    # export as asset
    task = ee.batch.Export.image.toAsset(**{
        'image': map,
        'scale': 30,
        'region': roi,
        'description': 'susadica_map_v034_' + str(year),
        'assetId': 'users/philipperufin/susadica_map_v034_' + str(year),
        'maxPixels': 1e13
    })
    task.start()