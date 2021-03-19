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
    b = ee.Image(0.0183).add(ee.Image(0.8850).multiply(image.select('blue'))).int16().rename('blue')
    g = ee.Image(0.0123).add(ee.Image(0.9317).multiply(image.select('green'))).int16().rename('green')
    r = ee.Image(0.0123).add(ee.Image(0.9372).multiply(image.select('red'))).int16().rename('red')
    nir = ee.Image(0.0448).add(ee.Image(0.8339).multiply(image.select('nir'))).int16().rename('nir')
    swir1 = ee.Image(0.0306).add(ee.Image(0.8639).multiply(image.select('swir1'))).int16().rename('swir1')
    swir2 = ee.Image(0.0116).add(ee.Image(0.9165).multiply(image.select('swir2'))).int16().rename('swir2')

    out = ee.Image(b.addBands(g).addBands(r).addBands(nir).addBands(swir1).addBands(swir2)
                   .addBands(image.select(['pixel_qa']))
                   .copyProperties(image, image.propertyNames()))
    return out

# todo: make sure start and endDate are datetime objects
def LND(startDate, endDate, roi=None, addNDVI=False, addEVI=True, cc=70, slc_off_out=False, l8_harmonize=False):
    l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR') \
        .filterDate(startDate, endDate) \
        .filterMetadata('IMAGE_QUALITY', 'equals', 9) \
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cc) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')\
        .filterDate(startDate, endDate) \
        .filterMetadata('IMAGE_QUALITY', 'equals', 9) \
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cc) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
        .filterDate(startDate, endDate) \
        .filterMetadata('IMAGE_QUALITY', 'equals', 9) \
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cc) \
        .select(['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
        .filterDate(startDate, endDate) \
        .filterMetadata('IMAGE_QUALITY_OLI', 'equals', 9) \
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cc) \
        .select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    if slc_off_out == True:
        l7 = l7.filterDate(datetime.datetime(1999, 4, 18), datetime.datetime(2003, 5, 31))

    if l8_harmonize:
        l8 = l8.map(L8_harmonize)

    lnd = l8.merge(l7).merge(l5).merge(l4)
    lnd = lnd.map(fct.cld.maskQuality)

    if addNDVI == True:
        lnd = lnd.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red'])
                                               .multiply(10000).toInt16().rename('ndvi')))
    if addEVI == True:
            lnd = lnd.map(lambda image: image.addBands(image.expression("2.5 * ((b('nir') - b('red')) / (b('nir') + 6 * b('red') - 7.5 * b('blue') + 1e4))")
                                               .multiply(10000).toInt16().rename('evi')))
    if roi != None:
        lnd = lnd.filterBounds(roi)
    # print collection sizes
    print('L4: ' + str(l4.size().getInfo()))
    print('L5: ' + str(l5.size().getInfo()))
    print('L7: ' + str(l7.size().getInfo()))
    print('L8: ' + str(l8.size().getInfo()))

    print('LND: ' + str(lnd.size().getInfo()))

    return lnd


# todo: make sure start and endDate are datetime objects
def OLI(startDate, endDate, roi=None, addNDVI=False, addEVI=True, cc=70, l8_harmonize=False):

    l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
        .filterDate(startDate, endDate) \
        .filterMetadata('IMAGE_QUALITY_OLI', 'equals', 9) \
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cc) \
        .select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
                ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa'])

    if l8_harmonize:
        l8 = l8.map(L8_harmonize)

    # print collection sizes
    lnd = l8
    lnd = lnd.map(fct.cld.maskQuality)
    print('LND: ' + str(lnd.size().getInfo()))

    if addNDVI == True:
        lnd = lnd.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red'])
                                               .multiply(10000).toInt16().rename('ndvi')))
    if addEVI == True:
            lnd = lnd.map(lambda image: image.addBands(image.expression("2.5 * ((b('nir') - b('red')) / (b('nir') + 6 * b('red') - 7.5 * b('blue') + 1e4))")
                                               .multiply(10000).toInt16().rename('evi')))
    if roi != None:
        lnd = lnd.filterBounds(roi)

    return lnd