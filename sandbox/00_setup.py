"""Filter an image collection by date and region to make a median composite.
See also: Clipped composite, which crops the output image
instead of filtering the input collection.
"""

import datetime
import ee
#import ee.mapclient

from fct.cld import maskClouds
from fct.stm import LND_merge
from fct.stm import STM


ee.Initialize()

polygon = ee.Geometry.Polygon([[
    [-109.05, 37.0], [-102.05, 37.0], [-102.05, 41.0],   # colorado
    [-109.05, 41.0], [-111.05, 41.0], [-111.05, 42.0],   # utah
    [-114.05, 42.0], [-114.05, 37.0], [-109.05, 37.0]]])

roi = ee.FeatureCollection('users/philipperufin/cerrado_ibge')
roi = ee.FeatureCollection("users/philipperufin/aralsea_poly")

startDate = datetime.datetime(2015, 10, 1)
endDate = datetime.datetime(2015, 12, 31)

collection = LND_merge(roi, startDate, endDate)
features = STM(collection)


train = ee.FeatureCollection("users/philipperufin/SUSADICA_poly_2018")

table = features.sampleRegions({
    'collection': train,
    'properties': ['class'],
    'scale': 30,
    'tileScale': 12
})

path = collection.getDownloadUrl({
    'scale': 30,
    'crs': 'EPSG:4326',
    'region': '[[-120, 35], [-119, 35], [-119, 34], [-120, 34]]'
})
print(path)