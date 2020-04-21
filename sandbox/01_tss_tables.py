import ee
import datetime
import fct.tss

ee.Initialize()

#### get tss from point shape
point_shape = r'C:\Users\geo_phru\Desktop\LND_tss_SI\maize_potato\potato_training.shp'

startDate = datetime.datetime(2017, 1, 1)
endDate = datetime.datetime(2020, 3, 30)

out_path = r'C:\Users\geo_phru\Desktop\LND_tss_SI\maize_potato\potato_training_lnd_tss.csv'
fct.tss.TSS_LND(point_shape, 'Name', startDate, endDate, True, out_path)

out_path = r'C:\Users\geo_phru\Desktop\LND_tss_SI\maize_potato\potato_training_sen_tss.csv'
fct.tss.TSS_SEN(point_shape, 'Name', startDate, endDate, True, out_path)