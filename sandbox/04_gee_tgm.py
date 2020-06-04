import ee
import fct.stm
import datetime
import json
import numpy as np
import ogr
import pandas as pd
import geopandas as gpd


ee.Initialize()

###########################################################
###########################################################
# upper left for FORCE grid

#from pyproj import Proj, transform
#out_crs = Proj('epsg:4326')
#in_crs = Proj('esri:102025')

# lat / lon
#x1,y1 = -2861580, 2509380
#x2,y2 = transform(in_crs, out_crs,x1,y1)
#print(x2,y2)

###########################################################
###########################################################
# local shapefile with training points
point_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\all\pts.shp'
points = gpd.read_file(point_shape)

# local shapefile with grid with tiles
poly_shape = r'C:\Users\geo_phru\Desktop\SUSADICA\grid\3km\shp\grid.shp'
grid = gpd.read_file(poly_shape)

# convert to EPSG:4326
#https://geopandas.org/reference.html
grid.crs
grid.crs = 'ESRI:102025'
grid = grid.to_crs("EPSG:4326")

points.crs
points = points.to_crs("EPSG:4326")

# select tile ids with points
tile_ids = pd.unique(gpd.sjoin(grid, points, op='intersects')['Tile_ID'])
tile_ids = tile_ids[0:300]
print('Considering ' + str(tile_ids.shape[0]) + ' tiles')

# set first iteration
first = True

# iterate over tiles in grid
for tile_id in tile_ids:

    # select points within tile
    print(tile_id)
    tile = grid[grid['Tile_ID'] == tile_id]
    tpts = gpd.sjoin(tile, points, op='intersects')

    # if points found
    if tpts.shape[0] != 0:
        # years included in tile
        years = pd.unique(tpts['year'])

        # iterate over years in tile
        for year in years:
            print(int(year))
            # subset points in year
            typts = tpts.loc[tpts['year'] == year]

            # remove other attributes
            typts = typts.drop(['Tile_ID', 'Tile_X', 'Tile_Y', 'index_right',
                                'poly_ID', 'poly', 'year', 'ID', 'layer', 'path'], axis=1)

            #for col in typts.columns:
            #    print(col)

            ###########################################################
            ###########################################################
            # create geojson from geopandas
            # from https://gis.stackexchange.com/questions/333791/accessing-a-shapefile-with-googleearthengine-api-invalid-geojson-geometry
            point_f = []
            for i in range(typts.shape[0]):
                geom = typts.iloc[i:i+1,:]
                jsonDict = eval(geom.to_json())
                geojsonDict = jsonDict['features'][0]
                point_f.append(ee.Feature(geojsonDict))

            # make feature collection
            ptsfc = ee.FeatureCollection(point_f)

            ###########################################################
            ###########################################################
            # create stm for both seasons and rename
            startDate = datetime.datetime(int(year), 4, 1)
            endDate = datetime.datetime(int(year), 7, 15)
            stm_s01 = fct.stm.LND_STM(startDate, endDate) \
                        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
                                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
                                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
                                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
                                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
                                's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn')

            startDate = datetime.datetime(int(year), 7, 16)
            endDate = datetime.datetime(int(year), 10, 30)
            stm_s02 = fct.stm.LND_STM(startDate, endDate) \
                        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
                                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
                                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
                                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
                                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
                                's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn')

            stm_image = ee.Image([stm_s01, stm_s02])

            ###########################################################
            ###########################################################
            # sample point locations
            #stm = stm_s01.sampleRegions(ptsfc, ['class'], 30)
            stm = stm_image.sampleRegions(ptsfc, ['class'], 30)

            # merge years
            if not first:
                tg_stm = stm.merge(stm)

            if first:
                tg_stm = stm
                first = False


#print(tg_stm.first().getInfo())
#print(stm.size().getInfo())
#print(ptsfc.size().getInfo())
#print(tg_stm.size().getInfo())

###########################################################
###########################################################
# classifier
bands = ['s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
        's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
        's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
        's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
        's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
        's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn',
         
        's02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
        's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
        's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
        's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
        's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
        's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn']

classifier = ee.Classifier.randomForest(200).train(tg_stm, 'class', bands)

#print('RF accuracy: ', classifier.confusionMatrix().accuracy().getInfo())
#print('RF error matrix: ', classifier.confusionMatrix().getInfo())

###########################################################
###########################################################
# stm features
year = 2018
for year in range(1984, 2020):

    startDate = datetime.datetime(int(year), 4, 1)
    endDate = datetime.datetime(int(year), 7, 15)
    stm_s01 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s01_b_p50', 's01_g_p50', 's01_r_p50', 's01_n_p50', 's01_sw1_p50', 's01_sw2_p50',
                's01_b_std', 's01_g_std', 's01_r_std', 's01_n_std', 's01_sw1_std', 's01_sw2_std',
                's01_b_p25', 's01_g_p25', 's01_r_p25', 's01_n_p25', 's01_sw1_p25', 's01_sw2_p25',
                's01_b_p75', 's01_g_p75', 's01_r_p75', 's01_n_p75', 's01_sw1_p75', 's01_sw2_p75',
                's01_b_iqr', 's01_g_iqr', 's01_r_iqr', 's01_n_iqr', 's01_sw1_iqr', 's01_sw2_iqr',
                's01_b_imn', 's01_g_imn', 's01_r_imn', 's01_n_imn', 's01_sw1_imn', 's01_sw2_imn')

    startDate = datetime.datetime(int(year), 7, 16)
    endDate = datetime.datetime(int(year), 10, 30)
    stm_s02 = fct.stm.LND_STM(startDate, endDate) \
        .rename('s02_b_p50', 's02_g_p50', 's02_r_p50', 's02_n_p50', 's02_sw1_p50', 's02_sw2_p50',
                's02_b_std', 's02_g_std', 's02_r_std', 's02_n_std', 's02_sw1_std', 's02_sw2_std',
                's02_b_p25', 's02_g_p25', 's02_r_p25', 's02_n_p25', 's02_sw1_p25', 's02_sw2_p25',
                's02_b_p75', 's02_g_p75', 's02_r_p75', 's02_n_p75', 's02_sw1_p75', 's02_sw2_p75',
                's02_b_iqr', 's02_g_iqr', 's02_r_iqr', 's02_n_iqr', 's02_sw1_iqr', 's02_sw2_iqr',
                's02_b_imn', 's02_g_imn', 's02_r_imn', 's02_n_imn', 's02_sw1_imn', 's02_sw2_imn')

    stm_image = ee.Image([stm_s01, stm_s02])

    map = stm_image.classify(classifier)

    for tile_id in tile_ids:

        # get tile
        tile = grid[grid['Tile_ID'] == tile_id]

        # ee geometry
        g = json.loads(tile.to_json())
        coords = list(g['features'][0]['geometry']['coordinates'])
        map_tile = ee.Geometry.Polygon(coords)

        # export task
        task = ee.batch.Export.image.toDrive(**{
            'image': map,
            'description': tile_id,
            'folder': str(year),
            'scale': 30,
            'region': map_tile
        })
        task.start()
        task.status()



# export to drive
# https://github.com/google/earthengine-api/issues/59
task = ee.batch.Export.table.toDrive(**{
    'collection': tg_stm,
    'folder': 'myFolder',
    'description':'tg_stm_single_tile',
    'fileFormat': 'SHP'
})
task.start()
task.status()

# export to asset
# https://developers.google.com/earth-engine/python_install
export = ee.batch.Export.table.toAsset(**{
    'collection': tg_stm,
    'description':'SUSADICA_tg_stm_test',
    'assetId': 'users/philipperufin/SUSADICA_tg_stm'
})
export.start()
export.status()


print(tg_stm.first().get('s01_b_p50').getInfo())

# merge to overall feature collection

# RF classifier

# predict features based on tiles


###########################################################
###########################################################
#
# testing stuff:

driver = ogr.GetDriverByName("ESRI Shapefile")
dataSource = driver.Open(point_shape, 0)
layer = dataSource.GetLayer()
#feat = layer.GetNextFeature()

fc = {"type": "FeatureCollection",
      "features": []}
for feat in layer:
    fc["features"].append(feat.GetGeometryRef().ExportToJson())

fc['features']['type']

x,y,z = feat.GetGeometryRef().GetPoint()
fcp = ee.Geometry.Point([x,y])
fcp = ee.Geometry.Point(pts)
fc = ee.Geometry.Point(fc)
print(fc)
stm



# get coordinates
i = 0
for feat in layer:
    if i == 0:
        #x, y, z = feat.GetGeometryRef().GetPoint()
        #pts = list([[x,y]])
        x = feat.GetGeometryRef().GetPoint()[0]
        y = feat.GetGeometryRef().GetPoint()[1]
        #pts = {'type': 'Point', 'coordinates': [x, y]}
    i =+ 1
    if i > 0:
        #x, y, z = feat.GetGeometryRef().GetPoint()
        #pts.append([x,y])
        x = np.append(x, feat.GetGeometryRef().GetPoint()[0])
        y = np.append(y, feat.GetGeometryRef().GetPoint()[1])
        #pts = np.append(pts,{'type': 'Point', 'coordinates': [x, y]})

id = feat.GetField("ID")
print("point id " + str(id))


geom = {'type': 'Point', 'coordinates': pts}

pts[0].append('class')
pts[1].append(1)


    stm[0].append("ID")
    stm[1].append(id)

    # Append to output then get next feature
    stm_list.append(stm)
    feat = layer.GetNextFeature()
