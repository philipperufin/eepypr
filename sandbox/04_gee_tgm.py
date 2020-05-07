import ogr
import ee
import fct.stm
import datetime
import numpy as np
import geopandas as gpd

ee.Initialize()

# local shapefile with grid with tiles
point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\r2\pts_2018\pts_2018.shp'

# GEO JSON?

# from https://gis.stackexchange.com/questions/333791/accessing-a-shapefile-with-googleearthengine-api-invalid-geojson-geometry
shapefile = gpd.read_file(point_shape)

features = []
for i in range(shapefile.shape[0]):
    geom = shapefile.iloc[i:i+1,:]
    jsonDict = eval(geom.to_json())
    geojsonDict = jsonDict['features'][0]
    features.append(ee.Feature(geojsonDict))

fc = ee.FeatureCollection(features)

# stm
startDate = datetime.datetime(2018, 4, 1)
endDate = datetime.datetime(2018, 7, 15)
stm_s01 = fct.stm.LND_STM(startDate, endDate) \
            .rename('s01_blue_med', 's01_green_med', 's01_red_med', 's01_nir_med', 's01_swir1_med', 's01_swir2_med',
                    's01_blue_sd', 's01_green_sd', 's01_red_sd', 's01_nir_sd', 's01_swir1_sd', 's01_swir2_sd',
                    's01_blue_p25', 's01_green_p25', 's01_red_p25', 's01_nir_p25', 's01_swir1_p25', 's01_swir2_p25',
                    's01_blue_p75', 's01_green_p75', 's01_red_p75', 's01_nir_p75', 's01_swir1_p75', 's01_swir2_p75',
                    's01_blue_iqr', 's01_green_iqr', 's01_red_iqr', 's01_nir_iqr', 's01_swir1_iqr', 's01_swir2_iqr',
                    's01_blue_imean', 's01_green_imean', 's01_red_imean', 's01_nir_imean', 's01_swir1_imean', 's01_swir2_imean')

startDate = datetime.datetime(2018, 7, 16)
endDate = datetime.datetime(2018, 10, 30)
stm_s02 = fct.stm.LND_STM(startDate, endDate) \
            .rename('s02_blue_med', 's02_green_med', 's02_red_med', 's02_nir_med', 's02_swir1_med', 's02_swir2_med',
                    's02_blue_sd', 's02_green_sd', 's02_red_sd', 's02_nir_sd', 's02_swir1_sd', 's02_swir2_sd',
                    's02_blue_p25', 's02_green_p25', 's02_red_p25', 's02_nir_p25', 's02_swir1_p25', 's02_swir2_p25',
                    's02_blue_p75', 's02_green_p75', 's02_red_p75', 's02_nir_p75', 's02_swir1_p75', 's02_swir2_p75',
                    's02_blue_iqr', 's02_green_iqr', 's02_red_iqr', 's02_nir_iqr', 's02_swir1_iqr', 's02_swir2_iqr',
                    's02_blue_imean', 's02_green_imean', 's02_red_imean', 's02_nir_imean', 's02_swir1_imean', 's02_swir2_imean')

stm_image = ee.Image([stm_s01, stm_s02])
stm = stm_image.sampleRegions(fc, ['class'], 30)

# classifier
classifier = ee.Classifier.randomForest(150).train(stm, 'class')
print('RF error matrix: ', classifier.confusionMatrix().getInfo())
print('RF accuracy: ', classifier.confusionMatrix().accuracy().getInfo())

# feature collections of ~n points in image tiles

# point-wise / tiles-wise & year stm

# sample regions

# generalize band names

# merge to overall feature collection

# export to asset

# RF classifier

# predict features based on tiles



# testing stuff:

driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(point_shape, 0)
layer = dataSource.GetLayer()
#feat = layer.GetNextFeature()

fc = {"type": "FeatureCollection",
      "features": []}
for feat in layer:
    fc["features"].append(feat.GetGeometryRef().ExportToJson())

fc['features']['type']

x,y,z = feat.GetGeometryRef().GetPoint()
fcp = ee.Geometry.Point([x,y])
fcp = ee.Geometry.Point(pts)
fc = ee.Geometry.Point(fc)
print(fc)
stm



# get coordinates
i = 0
for feat in layer:
    if i == 0:
        #x, y, z = feat.GetGeometryRef().GetPoint()
        #pts = list([[x,y]])
        x = feat.GetGeometryRef().GetPoint()[0]
        y = feat.GetGeometryRef().GetPoint()[1]
        #pts = {'type': 'Point', 'coordinates': [x, y]}
    i =+ 1
    if i > 0:
        #x, y, z = feat.GetGeometryRef().GetPoint()
        #pts.append([x,y])
        x = np.append(x, feat.GetGeometryRef().GetPoint()[0])
        y = np.append(y, feat.GetGeometryRef().GetPoint()[1])
        #pts = np.append(pts,{'type': 'Point', 'coordinates': [x, y]})

id = feat.GetField("ID")
print("point id " + str(id))


geom = {'type': 'Point', 'coordinates': pts}

pts[0].append('class')
pts[1].append(1)


    stm[0].append("ID")
    stm[1].append(id)

    # Append to output then get next feature
    stm_list.append(stm)
    feat = layer.GetNextFeature()
