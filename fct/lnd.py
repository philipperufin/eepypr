# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
#######################################################
# LND function returns quality-masked TM, ETM+, and OLI
# collections, renamed B, G, R, NIR, SWIR1, SWIR2 to
# blue, green, red, nir, swir1, swir2 for consistent use.
#######################################################
# startDate and endDate to be provided as datetime
# mark beginning and end of collection period.
#######################################################


import ee
import datetime
import fct.cld

# function to harmonize l8 surface reflectance with coefficients from Roy et al. 2016
def L8_harmonize(image):
    b = ee.Image(0.0183).add(ee.Image(0.8850).multiply(image.select('blue'))).int16()
    g = ee.Image(0.0123).add(ee.Image(0.9317).multiply(image.select('green'))).int16()
    r = ee.Image(0.0123).add(ee.Image(0.9372).multiply(image.select('red'))).int16()
    nir = ee.Image(0.0448).add(ee.Image(0.8339).multiply(image.select('nir'))).int16()
    swir1 = ee.Image(0.0306).add(ee.Image(0.8639).multiply(image.select('swir1'))).int16()
    swir2 = ee.Image(0.0116).add(ee.Image(0.9165).multiply(image.select('swir2'))).int16()

    out = ee.Image(b.addBands(g).addBands(r).addBands(nir).addBands(swir1).addBands(swir2)
                   .addBands(image.select(['pixel_qa']))
                   .copyProperties(image, image.propertyNames()))
    return out

# todo: make roi optional, if null don´t filter
def LND_roi(roi, startDate, endDate):
    # todo: make sure start and endDate are datetime objects

    l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .filterBounds(roi) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .filterBounds(roi) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .filterBounds(roi) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l8r = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .filterBounds(roi) \
        .select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])
    l8 = l8r.map(L8_harmonize)

    lnd = l8.merge(l7).merge(l5).merge(l4)
    lnd = lnd.map(fct.cld.maskQuality)

    return lnd

def LND(startDate, endDate, addVI=True):
    l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR') \
        .filterDate(startDate, endDate) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
        .filterDate(startDate, endDate)\
        .select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])
    #l8 = l8.map(L8_harmonize)

    lnd = l8.merge(l7).merge(l5).merge(l4)
    lnd = lnd.map(fct.cld.maskQuality)

    if addVI == True:
        lnd = lnd.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red'])\
                                               .multiply(10000).toInt16().rename('ndvi'))) \
                 .map(lambda image: image.addBands(image.expression("2.5 * ((b('nir') - b('red')) / (b('nir') + 6 * b('red') - 7.5 * b('blue') + 1e4))")\
                                               .multiply(10000).toInt16().rename('evi')))

    return lnd
