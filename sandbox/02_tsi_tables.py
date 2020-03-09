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
point_shape = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326.shp'

startDate = datetime.datetime(2014, 7, 1)
endDate = datetime.datetime(2016, 6, 30)
out_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326_tsi.csv'

interval = 16
aggregation = 'median'
write=True

fct.tsi.TSI(point_shape, startDate, endDate, interval, 'median', True, out_path)