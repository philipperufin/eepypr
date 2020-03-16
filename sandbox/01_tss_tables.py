import ee
import datetime
import fct.tss

ee.Initialize()

#### get tss from point shape
point_shape = r'C:\Users\geo_phru\Desktop\olives\training_singlepart_4326_test.shp'

startDate = datetime.datetime(1984, 1, 1)
endDate = datetime.datetime(2018, 12, 31)
out_path = r'C:\Users\geo_phru\Desktop\olives\training_singlepart_4326_test_tss.csv'

fct.tss.TSS(point_shape, startDate, endDate, True, out_path)