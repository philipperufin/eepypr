# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
#######################################################
# SEN function returns quality-masked S2AB
# collections, renamed B, G, R, NIR, SWIR1, SWIR2 to
# blue, green, red, nir, swir1, swir2 for consistent use.
#######################################################
# startDate and endDate to be provided as datetime
# mark beginning and end of collection period.
#######################################################


import ee
import datetime
import geopandas as gpd
import json
import fct.cld

def SEN(startDate, endDate, cdi=True):
    if cdi==False:
        bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'QA60', 'SCL'])
        band_names = ee.List(['blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'broadnir', 'swir1', 'swir2', 'QA60', 'SCL'])

        sen = ee.ImageCollection('COPERNICUS/S2_SR')\
                    .filter(ee.Filter.date(startDate, endDate))\
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50))\
                    .map(fct.cld.maskS2scl)\
                    .select(bands, band_names)

    if cdi==True:
        bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'QA60', 'SCL', 'cdi'])
        band_names = ee.List(
            ['blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'broadnir', 'swir1', 'swir2', 'QA60',
             'SCL', 'CDI'])

        sen = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filter(ee.Filter.date(startDate, endDate)) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)) \
            .map(fct.cld.maskS2scl) \
            .map(fct.cld.maskS2cdi) \
            .select(bands, band_names)

    sen = sen.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red']) \
                                               .multiply(10000).toInt16().rename('ndvi')))
    sen = sen.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'swir1']) \
                                               .multiply(10000).toInt16().rename('ndmi')))
    return sen


def SEN_TOA(startDate, endDate):

    bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'QA60', 'CDI'])
    band_names = ee.List(['blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'broadnir', 'swir1', 'swir2', 'QA60', 'CDI'])

    sen = ee.ImageCollection('COPERNICUS/S2')\
                .filter(ee.Filter.date(startDate, endDate)) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)) \
                .map(fct.cld.maskS2cdi) \
                .select(bands, band_names)
    return sen

def SEN4REG(startDate, endDate, roi_shape, band, assetName):
    # startDate / endDate in datetime format
    # roi_shape as filepath to extent shapefile with one feature
    # assetname without path

    print('create seasonal median ' + band + ' from S2 L2A')
    # open roi
    roi_shp = gpd.read_file(roi_shape)
    g = json.loads(roi_shp.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    print('bounding box: ')
    print(coords)
    roi = ee.Geometry.Polygon(coords)

    # create reference median nir
    sen4reg = fct.sen.SEN(startDate, endDate, cdi=True).select(band)\
        .reduce(ee.Reducer.percentile([50]))\
        .rename(band+'_med').toInt16()

    task = ee.batch.Export.image.toAsset(**{
        'image': sen4reg,
        'scale': 10,
        'region': roi,
        'description': assetName,
        'assetId': 'users/philipperufin/'+assetName,
        'maxPixels': 1e13
    })
    print('initiating export to asset:')
    print('users/philipperufin/'+assetName)

    task.start()