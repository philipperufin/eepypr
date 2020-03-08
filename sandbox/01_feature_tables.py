import ee
import datetime
import numpy as np
import gdal
import ogr
from fct.lnd import LND_roi
from fct.stm import STM
from fct.tss import TSS

ee.Initialize()

#### get table from stms
roi = ee.FeatureCollection("users/philipperufin/GAP_extent")

startDate = datetime.datetime(2018, 7, 1)
endDate = datetime.datetime(2018, 9, 30)

collection = LND_roi(roi, startDate, endDate)
#collection.getInfo()

features = STM(collection)
#bands = features.bandNames()
#print(bands)

#### sample regions
if True:
  train = ee.FeatureCollection("users/philipperufin/GAP_train_v2")
  #train.getInfo()

  table = features.sampleRegions(collection=train,
                                 properties=['class'],
                                 scale=30,
                                 tileScale=16)

  geometry = ogr.Open(r'K:\Cerrado_large_scale\Agriculture\samples\new\cerrado_agri_201516_IAEA.shp')
  xCoord = geometry.GetX()
  yCoord = geometry.GetY()
  pts = {'type': 'Point', 'coordinates': [xCoord, yCoord]}
  features.getRegion(pts, 30).getInfo()

#### sample rectangle
if False:
    aoi = ee.Geometry.Polygon(
      [[[40.15, 37.10],
        [40.15, 37.05],
        [40.10, 37.05],
        [40.10, 37.10]]], None, False)

    table = features.sampleRectangle(region=aoi)

# Get individual band arrays.
table_data = table.getInfo()['properties']
print(table_data)

# Transfer the arrays from server to client and cast as np array.
#np_swir1_sd = np.array(swir1_sd.getInfo())
#print(np_swir1_sd.shape)

# Expand the dimensions of the images so they can be concatenated into 3-D.
#np_swir1_sd  = np.expand_dims(np_swir1_sd, 2)
#print(np_swir1_sd.shape)

# Stack the individual bands to make a 3-D array.
#rgb_img = np.concatenate((np_swir1_sd, np_swir1_sd, np_swir1_sd), 2)
#print(rgb_img.shape)
