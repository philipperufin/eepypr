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
point_shape = r'D:\PRJ_TMP\FSDA\data\NICFI_LC\train_lichinga_stratrand_fnds_40.shp'
points = gpd.read_file(point_shape)

points.crs
points = points.to_crs(epsg=4326)

pd.unique(points["class"])
points["class"].value_counts()

add_elevation = True
add_latlon = True


# subset points in year


for col in points.columns:
    print(col)
points.head()
# remove other attributes
points = points.drop(['cell', 'x', 'y', 'f___201', 'id', 'texture', 'vhr_date', 'comment'], axis=1)
points = points[points['class'].notna()]
###########################################################
###########################################################
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
# stm asset
stm_image = ee.Image('users/philipperufin/fsda_lichinga_psm_coreg_100m_ssnl_annl_stm_2021')

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
stm = stm_image.sampleRegions(ptsfc, ['class'], 4.77)

###########################################################
# classifier
# define band names
bands = ['s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_ndvi_p50',
         's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_ndvi_std',
         's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_ndvi_p25',
         's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_ndvi_p75',
         's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_ndvi_iqr',

         's02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_ndvi_p50',
         's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_ndvi_std',
         's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_ndvi_p25',
         's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_ndvi_p75',
         's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_ndvi_iqr',

         's03_b_p50', 's03_g_p50', 's03_r_p50', 's03_n_p50', 's03_ndvi_p50',
         's03_b_std', 's03_g_std', 's03_r_std', 's03_n_std', 's03_ndvi_std',
         's03_b_p25', 's03_g_p25', 's03_r_p25', 's03_n_p25', 's03_ndvi_p25',
         's03_b_p75', 's03_g_p75', 's03_r_p75', 's03_n_p75', 's03_ndvi_p75',
         's03_b_iqr', 's03_g_iqr', 's03_r_iqr', 's03_n_iqr', 's03_ndvi_iqr',

         's03_ndvi_p25_p50_20', 's03_ndvi_p25_p50_20ndi',
         's03_ndvi_p25_p50_50', 's03_ndvi_p25_p50_50ndi',
         's03_ndvi_p25_p50_100', 's03_ndvi_p25_p50_100ndi',

         's03_ndvi_p75_p50_20', 's03_ndvi_p75_p50_20ndi',
         's03_ndvi_p75_p50_50', 's03_ndvi_p75_p50_50ndi',
         's03_ndvi_p75_p50_100', 's03_ndvi_p75_p50_100ndi',

         'elevation', 'slope', 'longitude', 'latitude']

classifier = ee.Classifier.smileRandomForest(250).train(stm, 'class', bands)
#print('RF accuracy: ', classifier.confusionMatrix().accuracy().getInfo())
#print('RF error matrix: ', classifier.confusionMatrix().getInfo())

###########################################################
###########################################################

# ee roi geometry
roi_shp = gpd.read_file(r'D:\PRJ_TMP\FSDA\data\NICFI_LC\lichinga.shp')

g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)


print('setting up prediction')
map = stm_image.classify(classifier).toInt8()

# export as asset
task = ee.batch.Export.image.toAsset(**{
    'image': map,
    'scale': 4.77,
    'region': roi,
    'description': 'nicfi_lc_lichinga_coreg_100m_ssnl_annl_stm_2021',
    'assetId': 'users/philipperufin/nicfi_lc_lichinga_coreg_100m_ssnl_annl_stm_2021',
    'maxPixels': 1e13
})
task.start()