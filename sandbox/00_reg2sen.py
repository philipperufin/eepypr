import json
import datetime
import geopandas as gpd
import ee
import fct.psm
import fct.exp
import fct.stm

# define roi
roi_shp = gpd.read_file(r'D:\PRJ_TMP\FSDA\data\vector\roi\subsets\lichinga.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# define collection, clip and get mosaic ids

as_ref = ee.Image('users/philipperufin/sen4reg_cdi_2020-08-12').select('nir_med')
startDate = datetime.datetime(2020, 8, 1)
endDate = datetime.datetime(2020, 12, 31)
# start = (2020, 9, 1), (2021, 1, 1), (2021, 5, 1)
# end = (2020, 12, 31), (2021, 4, 30), (2021, 8, 31)


col = fct.psm.PSM(startDate, endDate)
ids = col.aggregate_array('system:index').getInfo()


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

            displacement = to_reg.displacement(as_ref, maxOffset=100, stiffness=8)

            # use the computed displacement to register all original bands.
            registered = to_reg.displace(displacement, maxOffset=100)

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
description = 'reg2sen_01-04_unregistered_nir'
folder = 'NICFI_LC'
scale = 4.77
#fct.exp.exportDrive(img_unr, description, folder, scale)

description = 'reg2sen_08-12_registered_nir_s8_o100'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(img_reg, description, folder, scale)

task = ee.batch.Export.image.toDrive(**{
    'image': as_ref,
    'description': 'reg2sen_08-12_sen4reg_cdi_nir_med_roi',
    'folder': 'NICFI_LC',
    'scale': 10,
    'region': roi,
    'maxPixels': 1e13
})
task.start()