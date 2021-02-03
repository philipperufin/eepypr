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
import fct.cld

def SEN(startDate, endDate):

    bands = ee.List(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'QA60', 'SCL', 'cdi'])
    band_names = ee.List(['blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'broadnir', 'swir1', 'swir2', 'QA60', 'SCL', 'CDI'])

    sen = ee.ImageCollection('COPERNICUS/S2_SR')\
                .filter(ee.Filter.date(startDate, endDate))\
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50))\
                .map(fct.cld.maskS2scl) \
                .map(fct.cld.maskS2cdi) \
                .select(bands, band_names)

    sen = sen.map(lambda image: image.addBands(image.normalizedDifference(['broadnir', 'red'])\
                                               .multiply(10000).toInt16().rename('ndvi')))

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