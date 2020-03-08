import ee
import datetime

import fct.lnd
import fct.cld
import csv
import numpy as np
import gdal
import ogr

import fct.tss


ee.Initialize()

#### get tss from point shape
point_shape = r'C:\Users\geo_phru\Desktop\MAP\NDVI_profiles\points_FE1_4326.shp'

startDate = datetime.datetime(1984, 1, 1)
endDate = datetime.datetime(2018, 12, 31)
out_path = r'C:\Users\geo_phru\Desktop\MAP\NDVI_profiles\points_FE1_4326_tss.csv'

fct.tss.TSS(point_shape, startDate, endDate, True, out_path)