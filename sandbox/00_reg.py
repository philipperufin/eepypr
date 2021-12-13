import json
import datetime
import geopandas as gpd
import ee
import fct.psm
import fct.exp

# define roi
roi_shp = gpd.read_file(r'D:\PRJ_TMP\FSDA\data\NICFI_LC\lichinga.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# define collection, clip and get mosaic ids
startDate = datetime.datetime(2020, 8, 31)
endDate = datetime.datetime(2021, 8, 31)
col = fct.psm.PSM(startDate, endDate)

ids = col.aggregate_array('system:index').getInfo()

# define reference image
as_ref = ee.Image(col.filterMetadata('system:index', 'equals', 'planet_medres_normalized_analytic_2021-05_mosaic').first()).clip(roi)

# register each image in collection
singleband = True
i = 1
for id in ids:
    print(id)

    to_reg = ee.Image(col.filterMetadata('system:index', 'equals', id).first()).clip(roi)
    if to_reg != as_ref:
        print('do coreg')

        if singleband == True:
            # choose to register using only the 'NIR' band.
            to_reg = to_reg.select('nir')
            as_ref = as_ref.select('nir')

            displacement = to_reg.displacement(as_ref, 100)

            # use the computed displacement to register all original bands.
            registered = to_reg.displace(displacement)

        if singleband == False:
            registered = to_reg.register(as_ref, 100)

    # add reference image as is
    if to_reg == as_ref:
        registered = as_ref

    # add registered image to image list
    if i == 1:
        img_reg = registered
        img_unr = to_reg
    if i > 1:
        img_reg = ee.Image([img_reg, registered])
        img_unr = ee.Image([img_unr, to_reg])
    i = i + 1

# export image to drive
description = 'unregistered nir bands'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(img_unr, description, folder, scale)

description = 'registered nir bands 100m'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(img_reg, description, folder, scale)