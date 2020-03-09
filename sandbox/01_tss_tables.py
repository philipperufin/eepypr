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
point_shape = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326.shp'

startDate = datetime.datetime(2014, 7, 1)
endDate = datetime.datetime(2016, 6, 30)
out_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326_tss.csv'

fct.tss.TSS(point_shape, startDate, endDate, True, out_path)