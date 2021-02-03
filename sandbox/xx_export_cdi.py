import ee
import fct.exp
import fct.sen
import datetime

ee.Initialize()

startDate = datetime.datetime(2020, 1, 1)
endDate = datetime.datetime(2020, 12, 31)

coll = fct.sen.SEN(startDate, endDate)\
        .filterMetadata('MGRS_TILE', 'equals', '36NYF') \
        .filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 20) \
        .select('CDI')
count = coll.size()
print(str(count.getInfo()))

ids = coll.aggregate_array('PRODUCT_ID').getInfo()

for id in ids:
    print(id)
    image = coll.filterMetadata('PRODUCT_ID', 'equals', id)\
        .first()\
        .multiply(10000).toInt16()
    description = id
    folder = 'CDI'
    scale = 10
    fct.exp.exportDrive(image, description, folder, scale)

