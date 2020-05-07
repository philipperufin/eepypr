import ee
import datetime
import fct.tss

ee.Initialize()

#### Plateau State
path = r'P:\Nigeria\sampled_points'
point_shape = path + r'\sampled_points.shp'

startDate = datetime.datetime(2018, 12, 1)
endDate = datetime.datetime(2020, 3, 30)

out_path = path + r'\sampled_points_sen_toa_tss.csv'
fct.tss.TSS_SEN_TOA(point_shape, 'Name', startDate, endDate, True, out_path)

out_path = path + r'\sampled_points_sen_boa_tss.csv'
fct.tss.TSS_SEN(point_shape, 'Name', startDate, endDate, True, out_path)

out_path = path + r'\sampled_points_lnd_boa_tss.csv'
fct.tss.TSS_LND(point_shape, 'Name', startDate, endDate, True, out_path)



#### BAOBAB OSBie
startDate = datetime.datetime(1984, 1, 1)
endDate = datetime.datetime(2020, 4, 28)

point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs.shp'
out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs_lnd_tss.csv'
fct.tss.TSS_LND(point_shape, 'ID', startDate, endDate, True, out_path)

point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\GPS_baobabs.shp'
out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\GPS_baobabs_lnd_tss.csv'
fct.tss.TSS_LND(point_shape, 'ID', startDate, endDate, True, out_path)


startDate = datetime.datetime(2015, 1, 1)
endDate = datetime.datetime(2020, 4, 28)

point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs.shp'
out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs_sen_tss.csv'
fct.tss.TSS_SEN(point_shape, 'ID', startDate, endDate, True, out_path)