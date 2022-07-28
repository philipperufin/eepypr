'''
#######################################################
eepypr
Functions converting polygons into ee.Geometry
or points into ee.FeatureCollections
#######################################################
'''

import ee
import json
import geopandas as gpd

def feat2ee(feature):
    g = json.loads(feature.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    return ee.Geometry.Polygon(coords)

def shape2ee(file_path):
    shape = gpd.read_file(file_path)
    g = json.loads(shape.to_json())
    coords = list(g['features'][0]['geometry']['coordinates'])
    return ee.Geometry.Polygon(coords)

def points2ee(file_path):
    points = gpd.read_file(file_path)
    point_f = []
    for i in range(points.shape[0]):
        geom = points.iloc[i:i + 1, :]
        jsonDict = eval(geom.to_json().replace('null', 'None'))
        geojsonDict = jsonDict['features'][0]
        point_f.append(ee.Feature(geojsonDict))
    return ee.FeatureCollection(point_f)
