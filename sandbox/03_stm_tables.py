import ee
import datetime
import fct.stm

ee.Initialize()

#### get stm values from point shape
point_shape = r'C:\Users\geo_phru\Desktop\Field_waypoints\crops_waypoint_Points.shp'

startDate = datetime.datetime(2019, 4, 1)
endDate = datetime.datetime(2019, 6, 30)
out_path = r'C:\Users\geo_phru\Desktop\Field_waypoints\crops_waypoint_stm.csv'

fct.stm.STM_CSV(point_shape, startDate, endDate, True, out_path)