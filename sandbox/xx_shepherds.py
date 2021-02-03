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

def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)

generate_stm = False
model_run = True
maps = False
probs = True
###########################################################
### feature generation
###########################################################
if generate_stm:
    
    year = 2019
    
    ### stm calculation
    
    # create stm for both seasons
    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 6, 30)
    stm_s01 = fct.stm.SEN_STM(startDate, endDate) \
        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_re1_p50', 's01_re2_p50', 's01_re3_p50', 's01_n_p50', 's01_bn_p50', 's01_sw1_p50', 's01_sw2_p50', 's01_ndvi_p50',
                's01_b_std', 's01_g_std', 's01_r_std', 's01_re1_std', 's01_re2_std', 's01_re3_std', 's01_n_std', 's01_bn_std', 's01_sw1_std', 's01_sw2_std', 's01_ndvi_std',
                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_re1_p25', 's01_re2_p25', 's01_re3_p25', 's01_n_p25', 's01_bn_p25', 's01_sw1_p25', 's01_sw2_p25', 's01_ndvi_p25',
                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_re1_p75', 's01_re2_p75', 's01_re3_p75', 's01_n_p75', 's01_bn_p75', 's01_sw1_p75', 's01_sw2_p75', 's01_ndvi_p75',
                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_re1_iqr', 's01_re2_iqr', 's01_re3_iqr', 's01_n_iqr', 's01_bn_iqr', 's01_sw1_iqr', 's01_sw2_iqr', 's01_ndvi_iqr',
                's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_re1_imn', 's01_re2_imn', 's01_re3_imn', 's01_n_imn', 's01_bn_imn', 's01_sw1_imn', 's01_sw2_imn', 's01_ndvi_imn')
    
    startDate = datetime.datetime(int(year), 7, 1)
    endDate = datetime.datetime(int(year), 9, 30)
    stm_s02 = fct.stm.SEN_STM(startDate, endDate) \
        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_re1_p50', 's02_re2_p50', 's02_re3_p50', 's02_n_p50', 's02_bn_p50', 's02_sw1_p50', 's02_sw2_p50', 's02_ndvi_p50',
                's02_b_std', 's02_g_std', 's02_r_std', 's02_re1_std', 's02_re2_std', 's02_re3_std', 's02_n_std', 's02_bn_std', 's02_sw1_std', 's02_sw2_std', 's02_ndvi_std',
                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_re1_p25', 's02_re2_p25', 's02_re3_p25', 's02_n_p25', 's02_bn_p25', 's02_sw1_p25', 's02_sw2_p25', 's02_ndvi_p25',
                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_re1_p75', 's02_re2_p75', 's02_re3_p75', 's02_n_p75', 's02_bn_p75', 's02_sw1_p75', 's02_sw2_p75', 's02_ndvi_p75',
                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_re1_iqr', 's02_re2_iqr', 's02_re3_iqr', 's02_n_iqr', 's02_bn_iqr', 's02_sw1_iqr', 's02_sw2_iqr', 's02_ndvi_iqr',
                's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_re1_imn', 's02_re2_imn', 's02_re3_imn', 's02_n_imn', 's02_bn_imn', 's02_sw1_imn', 's02_sw2_imn', 's02_ndvi_imn')
    
    startDate = datetime.datetime(int(year), 3, 1)
    endDate = datetime.datetime(int(year), 10, 30)
    stm_ann = fct.stm.SEN_STM(startDate, endDate) \
        .rename('ann_b_p50', 'ann_g_p50', 'ann_r_p50', 'ann_re1_p50', 'ann_re2_p50', 'ann_re3_p50', 'ann_n_p50', 'ann_bn_p50', 'ann_sw1_p50', 'ann_sw2_p50', 'ann_ndvi_p50',
                'ann_b_std', 'ann_g_std', 'ann_r_std', 'ann_re1_std', 'ann_re2_std', 'ann_re3_std', 'ann_n_std', 'ann_bn_std', 'ann_sw1_std', 'ann_sw2_std', 'ann_ndvi_std',
                'ann_b_p25', 'ann_g_p25', 'ann_r_p25', 'ann_re1_p25', 'ann_re2_p25', 'ann_re3_p25', 'ann_n_p25', 'ann_bn_p25', 'ann_sw1_p25', 'ann_sw2_p25', 'ann_ndvi_p25',
                'ann_b_p75', 'ann_g_p75', 'ann_r_p75', 'ann_re1_p75', 'ann_re2_p75', 'ann_re3_p75', 'ann_n_p75', 'ann_bn_p75', 'ann_sw1_p75', 'ann_sw2_p75', 'ann_ndvi_p75',
                'ann_b_iqr', 'ann_g_iqr', 'ann_r_iqr', 'ann_re1_iqr', 'ann_re2_iqr', 'ann_re3_iqr', 'ann_n_iqr', 'ann_bn_iqr', 'ann_sw1_iqr', 'ann_sw2_iqr', 'ann_ndvi_iqr',
                'ann_b_imn', 'ann_g_imn', 'ann_r_imn', 'ann_re1_imn', 'ann_re2_imn', 'ann_re3_imn', 'ann_n_imn', 'ann_bn_imn', 'ann_sw1_imn', 'ann_sw2_imn', 'ann_ndvi_imn')
    
    
    # create two-season image and cast to integer!
    stm_image = ee.Image([stm_ann, stm_s01, stm_s02]).toInt16()
    
    
    # mask to roi
    roi_shp = gpd.read_file(r'C:\Users\geo_phru\Desktop\shepherd_camps\camps_v3\roi_subset_210127.shp')
    g = json.loads(roi_shp.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    roi = ee.Geometry.Polygon(coords)
    stm_image = maskInside(stm_image, roi)
    
    # seasonal ndvi percentile differences at 50m
    stm_image = stm_image.addBands(stm_image.select(['s01_ndvi_p25', 's01_ndvi_p75', 's01_ndvi_std',
                                                     's02_ndvi_p25', 's02_ndvi_p75', 's02_ndvi_std',
                                                     'ann_ndvi_p25', 'ann_ndvi_p75', 'ann_ndvi_std'])\
                                   .reduceNeighborhood(ee.Reducer.percentile([50]),ee.Kernel.circle(50, 'meters'))\
                                   .rename(['s01_ndvi_p25_txt_50m', 's01_ndvi_p75_txt_50m', 's01_ndvi_std_txt_50m',
                                            's02_ndvi_p25_txt_50m', 's02_ndvi_p75_txt_50m', 's02_ndvi_std_txt_50m',
                                            'ann_ndvi_p25_txt_50m', 'ann_ndvi_p75_txt_50m', 'ann_ndvi_std_txt_50m']))
    
    stm_image = stm_image.addBands(stm_image.normalizedDifference(['s01_ndvi_p25', 's01_ndvi_p25_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p25_dif_50m']))\
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_p75', 's01_ndvi_p75_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p75_dif_50m'])) \
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_std', 's01_ndvi_std_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_std_dif_50m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p25', 's02_ndvi_p25_txt_50m']) \
                           .multiply(10000).toInt16()\
                           .rename(['s02_ndvi_p25_dif_50m']))\
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p75', 's02_ndvi_p75_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_p75_dif_50m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_std', 's02_ndvi_std_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_std_dif_50m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p25', 'ann_ndvi_p25_txt_50m']) \
                           .multiply(10000).toInt16()\
                           .rename(['ann_ndvi_p25_dif_50m']))\
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p75', 'ann_ndvi_p75_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_p75_dif_50m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_std', 'ann_ndvi_std_txt_50m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_std_dif_50m']))
    
    # seasonal ndvi percentile differences at 200m
    stm_image = stm_image.addBands(stm_image.select(['s01_ndvi_p25', 's01_ndvi_p75', 's01_ndvi_std',
                                                     's02_ndvi_p25', 's02_ndvi_p75', 's02_ndvi_std',
                                                     'ann_ndvi_p25', 'ann_ndvi_p75', 'ann_ndvi_std'])\
                                   .reduceNeighborhood(ee.Reducer.percentile([50]),ee.Kernel.circle(200, 'meters'))\
                                   .rename(['s01_ndvi_p25_txt_200m', 's01_ndvi_p75_txt_200m', 's01_ndvi_std_txt_200m',
                                            's02_ndvi_p25_txt_200m', 's02_ndvi_p75_txt_200m', 's02_ndvi_std_txt_200m',
                                            'ann_ndvi_p25_txt_200m', 'ann_ndvi_p75_txt_200m', 'ann_ndvi_std_txt_200m']))
    
    stm_image = stm_image.addBands(stm_image.normalizedDifference(['s01_ndvi_p25', 's01_ndvi_p25_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p25_dif_200m']))\
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_p75', 's01_ndvi_p75_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p75_dif_200m'])) \
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_std', 's01_ndvi_std_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_std_dif_200m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p25', 's02_ndvi_p25_txt_200m']) \
                           .multiply(10000).toInt16()\
                           .rename(['s02_ndvi_p25_dif_200m']))\
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p75', 's02_ndvi_p75_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_p75_dif_200m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_std', 's02_ndvi_std_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_std_dif_200m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p25', 'ann_ndvi_p25_txt_200m']) \
                           .multiply(10000).toInt16()\
                           .rename(['ann_ndvi_p25_dif_200m']))\
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p75', 'ann_ndvi_p75_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_p75_dif_200m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_std', 'ann_ndvi_std_txt_200m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_std_dif_200m']))
    
    # seasonal ndvi percentile differences at 500m
    stm_image = stm_image.addBands(stm_image.select(['s01_ndvi_p25', 's01_ndvi_p75', 's01_ndvi_std',
                                                     's02_ndvi_p25', 's02_ndvi_p75', 's02_ndvi_std',
                                                     'ann_ndvi_p25', 'ann_ndvi_p75', 'ann_ndvi_std'])\
                                   .reduceNeighborhood(ee.Reducer.percentile([50]),ee.Kernel.circle(500, 'meters'))\
                                   .rename(['s01_ndvi_p25_txt_500m', 's01_ndvi_p75_txt_500m', 's01_ndvi_std_txt_500m',
                                            's02_ndvi_p25_txt_500m', 's02_ndvi_p75_txt_500m', 's02_ndvi_std_txt_500m',
                                            'ann_ndvi_p25_txt_500m', 'ann_ndvi_p75_txt_500m', 'ann_ndvi_std_txt_500m']))
    
    stm_image = stm_image.addBands(stm_image.normalizedDifference(['s01_ndvi_p25', 's01_ndvi_p25_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p25_dif_500m']))\
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_p75', 's01_ndvi_p75_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_p75_dif_500m'])) \
                           .addBands(stm_image.normalizedDifference(['s01_ndvi_std', 's01_ndvi_std_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s01_ndvi_std_dif_500m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p25', 's02_ndvi_p25_txt_500m']) \
                           .multiply(10000).toInt16()\
                           .rename(['s02_ndvi_p25_dif_500m']))\
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_p75', 's02_ndvi_p75_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_p75_dif_500m'])) \
                           .addBands(stm_image.normalizedDifference(['s02_ndvi_std', 's02_ndvi_std_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['s02_ndvi_std_dif_500m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p25', 'ann_ndvi_p25_txt_500m']) \
                           .multiply(10000).toInt16()\
                           .rename(['ann_ndvi_p25_dif_500m']))\
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_p75', 'ann_ndvi_p75_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_p75_dif_500m'])) \
                           .addBands(stm_image.normalizedDifference(['ann_ndvi_std', 'ann_ndvi_std_txt_500m']) \
                           .multiply(10000).toInt16() \
                           .rename(['ann_ndvi_std_dif_500m']))
    
    # export as asset
    task = ee.batch.Export.image.toAsset(**{
        'image': stm_image,
        'scale': 10,
        'region': roi,
        'description': 'caucasus_stm_2019_subset',
        'assetId': 'users/philipperufin/caucasus_stm_sen',
        'maxPixels': 1e13
    })
    task.start()
    task.status()


###########################################################
### train model
###########################################################
# local shapefile with training points
if model_run:

    point_shape = r'C:\Users\geo_phru\Desktop\shepherd_camps\camps_v3\train_sub.shp'
    points = gpd.read_file(point_shape)

    points.crs
    #points = points.to_crs("EPSG:4326")

    pd.unique(points["class"])
    points["class"].value_counts()

    # create geojson from geopandas
    # from https://gis.stackexchange.com/questions/333791/accessing-a-shapefile-with-googleearthengine-api-invalid-geojson-geometry
    point_f = []
    for i in range(points.shape[0]):
        geom = points.iloc[i:i + 1, :]
        jsonDict = eval(geom.to_json())
        geojsonDict = jsonDict['features'][0]
        point_f.append(ee.Feature(geojsonDict))

    # make feature collection
    ptsfc = ee.FeatureCollection(point_f)


    ###########################################################
    ###########################################################
    # classifier
    bands = ['s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_re1_p50', 's01_re2_p50', 's01_re3_p50', 's01_n_p50', 's01_bn_p50', 's01_sw1_p50', 's01_sw2_p50', 's01_ndvi_p50',
            's01_b_std', 's01_g_std', 's01_r_std', 's01_re1_std', 's01_re2_std', 's01_re3_std', 's01_n_std', 's01_bn_std', 's01_sw1_std', 's01_sw2_std', 's01_ndvi_std',
            's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_re1_p25', 's01_re2_p25', 's01_re3_p25', 's01_n_p25', 's01_bn_p25', 's01_sw1_p25', 's01_sw2_p25', 's01_ndvi_p25',
            's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_re1_p75', 's01_re2_p75', 's01_re3_p75', 's01_n_p75', 's01_bn_p75', 's01_sw1_p75', 's01_sw2_p75', 's01_ndvi_p75',
            's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_re1_iqr', 's01_re2_iqr', 's01_re3_iqr', 's01_n_iqr', 's01_bn_iqr', 's01_sw1_iqr', 's01_sw2_iqr', 's01_ndvi_iqr',
            's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_re1_imn', 's01_re2_imn', 's01_re3_imn', 's01_n_imn', 's01_bn_imn', 's01_sw1_imn', 's01_sw2_imn', 's01_ndvi_imn',

            's02_b_p50', 's02_g_p50', 's02_r_p50', 's02_re1_p50', 's02_re2_p50', 's02_re3_p50', 's02_n_p50', 's02_bn_p50', 's02_sw1_p50', 's02_sw2_p50', 's02_ndvi_p50',
            's02_b_std', 's02_g_std', 's02_r_std', 's02_re1_std', 's02_re2_std', 's02_re3_std', 's02_n_std', 's02_bn_std', 's02_sw1_std', 's02_sw2_std', 's02_ndvi_std',
            's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_re1_p25', 's02_re2_p25', 's02_re3_p25', 's02_n_p25', 's02_bn_p25', 's02_sw1_p25', 's02_sw2_p25', 's02_ndvi_p25',
            's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_re1_p75', 's02_re2_p75', 's02_re3_p75', 's02_n_p75', 's02_bn_p75', 's02_sw1_p75', 's02_sw2_p75', 's02_ndvi_p75',
            's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_re1_iqr', 's02_re2_iqr', 's02_re3_iqr', 's02_n_iqr', 's02_bn_iqr', 's02_sw1_iqr', 's02_sw2_iqr', 's02_ndvi_iqr',
            's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_re1_imn', 's02_re2_imn', 's02_re3_imn', 's02_n_imn', 's02_bn_imn', 's02_sw1_imn', 's02_sw2_imn', 's02_ndvi_imn',

            'ann_b_p50', 'ann_g_p50', 'ann_r_p50', 'ann_re1_p50', 'ann_re2_p50', 'ann_re3_p50', 'ann_n_p50', 'ann_bn_p50', 'ann_sw1_p50', 'ann_sw2_p50', 'ann_ndvi_p50',
            'ann_b_std', 'ann_g_std', 'ann_r_std', 'ann_re1_std', 'ann_re2_std', 'ann_re3_std', 'ann_n_std', 'ann_bn_std', 'ann_sw1_std', 'ann_sw2_std', 'ann_ndvi_std',
            'ann_b_p25', 'ann_g_p25', 'ann_r_p25', 'ann_re1_p25', 'ann_re2_p25', 'ann_re3_p25', 'ann_n_p25', 'ann_bn_p25', 'ann_sw1_p25', 'ann_sw2_p25', 'ann_ndvi_p25',
            'ann_b_p75', 'ann_g_p75', 'ann_r_p75', 'ann_re1_p75', 'ann_re2_p75', 'ann_re3_p75', 'ann_n_p75', 'ann_bn_p75', 'ann_sw1_p75', 'ann_sw2_p75', 'ann_ndvi_p75',
            'ann_b_iqr', 'ann_g_iqr', 'ann_r_iqr', 'ann_re1_iqr', 'ann_re2_iqr', 'ann_re3_iqr', 'ann_n_iqr', 'ann_bn_iqr', 'ann_sw1_iqr', 'ann_sw2_iqr', 'ann_ndvi_iqr',
            'ann_b_imn', 'ann_g_imn', 'ann_r_imn', 'ann_re1_imn', 'ann_re2_imn', 'ann_re3_imn', 'ann_n_imn', 'ann_bn_imn', 'ann_sw1_imn', 'ann_sw2_imn', 'ann_ndvi_imn',

            's01_ndvi_p25_txt_50m', 's01_ndvi_p75_txt_50m', 's01_ndvi_std_txt_50m',
            's02_ndvi_p25_txt_50m', 's02_ndvi_p75_txt_50m', 's02_ndvi_std_txt_50m',
            'ann_ndvi_p25_txt_50m', 'ann_ndvi_p75_txt_50m', 'ann_ndvi_std_txt_50m',

            's01_ndvi_p25_dif_50m', 's01_ndvi_p75_dif_50m', 's01_ndvi_std_dif_50m',
            's02_ndvi_p25_dif_50m', 's02_ndvi_p75_dif_50m', 's02_ndvi_std_dif_50m',
            'ann_ndvi_p25_dif_50m', 'ann_ndvi_p75_dif_50m', 'ann_ndvi_std_dif_50m',

            's01_ndvi_p25_txt_200m', 's01_ndvi_p75_txt_200m', 's01_ndvi_std_txt_200m',
            's02_ndvi_p25_txt_200m', 's02_ndvi_p75_txt_200m', 's02_ndvi_std_txt_200m',
            'ann_ndvi_p25_txt_200m', 'ann_ndvi_p75_txt_200m', 'ann_ndvi_std_txt_200m',

            's01_ndvi_p25_dif_200m', 's01_ndvi_p75_dif_200m', 's01_ndvi_std_dif_200m',
            's02_ndvi_p25_dif_200m', 's02_ndvi_p75_dif_200m', 's02_ndvi_std_dif_200m',
            'ann_ndvi_p25_dif_200m', 'ann_ndvi_p75_dif_200m', 'ann_ndvi_std_dif_200m',

            's01_ndvi_p25_txt_500m', 's01_ndvi_p75_txt_500m', 's01_ndvi_std_txt_500m',
            's02_ndvi_p25_txt_500m', 's02_ndvi_p75_txt_500m', 's02_ndvi_std_txt_500m',
            'ann_ndvi_p25_txt_500m', 'ann_ndvi_p75_txt_500m', 'ann_ndvi_std_txt_500m',

            's01_ndvi_p25_dif_500m', 's01_ndvi_p75_dif_500m', 's01_ndvi_std_dif_500m',
            's02_ndvi_p25_dif_500m', 's02_ndvi_p75_dif_500m', 's02_ndvi_std_dif_500m',
            'ann_ndvi_p25_dif_500m', 'ann_ndvi_p75_dif_500m', 'ann_ndvi_std_dif_500m']

    ###########################################################
    ###########################################################
    # stm asset
    stm_image = ee.Image('users/philipperufin/caucasus_stm_sen')
    stm_image = stm_image.select(bands)
    ###########################################################
    ###########################################################
    # sample point locations
    stm = stm_image.sampleRegions(ptsfc, ['class'], 10)

    ###########################################################
    ### predict
    ###########################################################

    # define roi
    roi_shp = gpd.read_file(r'C:\Users\geo_phru\Desktop\shepherd_camps\camps_v3\roi_subset_210127.shp')
    g = json.loads(roi_shp.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    roi = ee.Geometry.Polygon(coords)

    if maps:

        classifier = ee.Classifier.smileRandomForest(200).train(stm, 'class', bands)
        map = stm_image.classify(classifier).toInt8()

        # export as asset
        task = ee.batch.Export.image.toAsset(**{
            'image': map,
            'scale': 10,
            'region': roi,
            'description': 'caucasus_camps_v01_maps',
            'assetId': 'users/philipperufin/caucasus_camps_v01_maps',
            'maxPixels': 1e13
        })
        task.start()

    if probs:

        probabilit = ee.Classifier.smileRandomForest(200).setOutputMode('PROBABILITY').train(stm, 'class', bands)
        prb = stm_image.classify(probabilit)

        task = ee.batch.Export.image.toAsset(**{
            'image': prb,
            'scale': 10,
            'region': roi,
            'description': 'caucasus_camps_v02_prbs',
            'assetId': 'users/philipperufin/caucasus_camps_v02_prbs',
            'maxPixels': 1e13
        })
        task.start()