import ee
import datetime
import fct.stm

ee.Initialize()

#### get stm values from point shape
point_shape = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_gh_4326.shp'

startDate = datetime.datetime(2015, 7, 1)
endDate = datetime.datetime(2019, 9, 30)
out_path = r'C:\Users\geo_phru\Desktop\GAP\turkey_val\vali_4326_stm.csv'

fct.stm.STM_CSV(point_shape, startDate, endDate, True, out_path)