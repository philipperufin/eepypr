import ogr
import ee
import numpy as np
import fct.stm
import datetime

ee.Initialize()

# local shapefile with grid with tiles
point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\r2\pts_2018\pts_2018.shp'
driver = ogr.GetDriverByName("ESRI Shapefile")

dataSource = driver.Open(point_shape, 0)
layer = dataSource.GetLayer()
feat = layer.GetNextFeature()

t = ee.FeatureCollection('users/philipperufin/GAP_extent')
print(t)

# get coordinates
i = 0

for feat in layer:
    if i == 0:
        x, y, z = feat.GetGeometryRef().GetPoint()
        pts = list([[x,y]])
        #x = feat.GetGeometryRef().GetPoint()[-2]
        #y = feat.GetGeometryRef().GetPoint()[1]
        #pts = {'type': 'Point', 'coordinates': [x, y]}
    i =+ 1
    if i > 0:
        x, y, z = feat.GetGeometryRef().GetPoint()
        pts.append([x,y])
        #x = np.append(x, feat.GetGeometryRef().GetPoint())
        #y = np.append(y, feat.GetGeometryRef().GetPoint()[1])
        #pts = np.append(pts,{'type': 'Point', 'coordinates': [x, y]})

id = feat.GetField("ID")
print("point id " + str(id))

geom = {'type': 'Point', 'coordinates': pts}

pts[0].append('class')
pts[1].append(1)

startDate = datetime.datetime(2018, 4, 1)
endDate = datetime.datetime(2018, 6, 30)

stm_image = fct.stm.LND_STM(startDate, endDate)
stm = stm_image.sampleRegions(geom)


    stm[0].append("ID")
    stm[1].append(id)

    # Append to output then get next feature
    stm_list.append(stm)
    feat = layer.GetNextFeature()

# feature collections of ~n points in image tiles
# GEO JSON?

# point-wise / tiles-wise & year stm

# sample regions

# generalize band names

# merge to overall feature collection

# export to asset

# RF classifier

# predict features based on tiles
