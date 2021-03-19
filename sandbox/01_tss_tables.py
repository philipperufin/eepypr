import ee
import datetime
import fct.tss
from multiprocessing import Pool

ee.Initialize()

#startDate = datetime.datetime(1985, 1, 1)
#endDate = datetime.datetime(2020, 1, 1)
#id_string = 'ID'

#pnt = [r'D:\Seafile\Meine Bibliothek\share\schwieder\SPLIT_0.gpkg',
#       r'D:\Seafile\Meine Bibliothek\share\schwieder\SPLIT_1.gpkg',
#       r'D:\Seafile\Meine Bibliothek\share\schwieder\SPLIT_2.gpkg',
#       r'D:\Seafile\Meine Bibliothek\share\schwieder\SPLIT_3.gpkg']

#def f(x):
#    fct.tss.TSS(point_shape=x, id_string=id_string, startDate=startDate, endDate=endDate, driver='GPKG')

#if __name__ == '__main__':
#       with Pool(4) as p:
#              print(p.map(f, pnt))

startDate = datetime.datetime(1985, 1, 1)
endDate = datetime.datetime(2020, 1, 1)
id_string = 'id'
pnt = r'C:\Users\geo_phru\Desktop\MOZ\mozamb.shp'
fct.tss.TSS(point_shape=pnt, id_string=id_string, startDate=startDate, endDate=endDate)

fct.tss.TSS_PR(r'C:\Users\geo_phru\Desktop\MOZ\mozamb_TSS_LND_1985-2020.csv', index='NDVI')

# #### KITUI WEST
# startDate = datetime.datetime(1984, 1, 1)
# endDate = datetime.datetime(2020, 1, 1)
# id_string = 'ID'
# point_shape = r'P:\KenyaSandDams\Kitui West2 Points\Kitui_West2.shp'
# fct.tss.TSS(point_shape, 'ID', startDate, endDate, True)
#
# def f(arch):
#     fct.tss.TSS(point_shape, 'ID', startDate, endDate, True, archive=arch)
#
# if __name__ == '__main__':
#     with Pool(5) as p:
#         print(p.map(f, ['LND', 'SEN']))
#
#
# #### LUCAS TREE CROPS
# startDate = datetime.datetime(2016, 1, 1)
# endDate = datetime.datetime(2020, 1, 1)
#
# point_shape = r'M:\00_data\02_vector\lucas 2018\EU_2018_B81_ONPOINT.gpkg'
#
# #out_path = r'M:\00_data\02_vector\lucas 2018\EU_2018_B81_ONPOINT_TSS_SEN.csv'
# #fct.tss.TSS_SEN(point_shape, 'POINT_ID', startDate, endDate, True, out_path, driver='GPKG')
#
# out_path = r'M:\00_data\02_vector\lucas 2018\EU_2018_B81_ONPOINT_TSS_LND.csv'
# fct.tss.TSS_LND(point_shape, 'POINT_ID', startDate, endDate, True, out_path, driver='GPKG')
#
#
# #### Plateau State
# path = r'P:\Nigeria\sampled_points'
# point_shape = path + r'\sampled_points.shp'
#
# startDate = datetime.datetime(2018, 12, 1)
# endDate = datetime.datetime(2020, 3, 30)
#
# out_path = path + r'\sampled_points_sen_toa_tss.csv'
# fct.tss.TSS_SEN_TOA(point_shape, 'Name', startDate, endDate, True, out_path)
#
# out_path = path + r'\sampled_points_sen_boa_tss.csv'
# fct.tss.TSS_SEN(point_shape, 'Name', startDate, endDate, True, out_path)
#
# out_path = path + r'\sampled_points_lnd_boa_tss.csv'
# fct.tss.TSS_LND(point_shape, 'Name', startDate, endDate, True, out_path)
#
#
# #### BAOBAB OSBie
# startDate = datetime.datetime(1984, 1, 1)
# endDate = datetime.datetime(2020, 4, 28)
#
# point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs.shp'
# out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs_lnd_tss.csv'
# fct.tss.TSS_LND(point_shape, 'ID', startDate, endDate, True, out_path)
#
# point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\GPS_baobabs.shp'
# out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\GPS_baobabs_lnd_tss.csv'
# fct.tss.TSS_LND(point_shape, 'ID', startDate, endDate, True, out_path)
#
#
# startDate = datetime.datetime(2015, 1, 1)
# endDate = datetime.datetime(2020, 4, 28)
#
# point_shape = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs.shp'
# out_path = r'C:\Users\geo_phru\Desktop\OSBie\baobabs\google_baobabs_sen_tss.csv'
# fct.tss.TSS_SEN(point_shape, 'ID', startDate, endDate, True, out_path)
#
#
# #### NASA LCLUC
# startDate = datetime.datetime(2015, 1, 1)
# endDate = datetime.datetime(2020, 4, 30)
#
# point_shape = r'D:\Seafile\Meine Bibliothek\research\proposals\NASA_LCLUC_2020\shp\IND.shp'
# out_path = r'D:\Seafile\Meine Bibliothek\research\proposals\NASA_LCLUC_2020\shp\IND_tss.csv'
# fct.tss.TSS_LND(point_shape, 'id', startDate, endDate, True, out_path)
#
# out_path = r'D:\Seafile\Meine Bibliothek\research\proposals\NASA_LCLUC_2020\shp\IND_S2_tss.csv'
# fct.tss.TSS_SEN(point_shape, 'ID', startDate, endDate, True, out_path)
#
