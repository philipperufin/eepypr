import ee
import datetime
import fct.lnd
import fct.cld
import csv
import numpy as np
import gdal
import ogr
import fct.tsi

ee.Initialize()

#### get tss from point shape
point_shape = r'C:\Users\geo_phru\Desktop\MAP\NDVI_profiles\points_FE1_4326.shp'

startDate = datetime.datetime(2018, 1, 1)
endDate = datetime.datetime(2018, 12, 31)
out_path = r'C:\Users\geo_phru\Desktop\MAP\NDVI_profiles\points_FE1_4326_tss.csv'

interval = 8
aggregation = 'median'
write=True

fct.tsi.TSI(point_shape, startDate, endDate, 30, 'median', True, out_path)