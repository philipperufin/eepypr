import ee
import fct.exp
import json
import geopandas as gpd
def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)


ee.Initialize()
##########################################################
# fsda
# mask to roi
roi_path = r'D:\PRJ_TMP\FSDA\data\vector\adm\niassa_adm1.shp'
roi_shp = gpd.read_file(roi_path)
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)

# export psm stm
run = range(28,31)
for i in run:
    image = ee.Image('users/philipperufin/fsda_tiles/fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm')
    #image = maskInside(image, roi)
    description = 'fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm'
    folder = 'NICFI_LC/tiles'
    scale = 4.77
    fct.exp.exportDrive(image, description, folder, scale)

#done_tiles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 27, 35, 61]
#if False:
#    done = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 27, 35, 61]
#    for i in done:
#        ee.data.deleteAsset('users/philipperufin/fsda_tiles/fsda_tile_' + f'{int(i):03}' + '_psm_coreg_3season_stm')

image = ee.Image('users/philipperufin/nicfi_lc_tile_03deg_033_psm_coreg_3season_stm')
description = 'nicfi_lc_tile_03deg_033_psm_coreg_3season_stm'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(image, description, folder, scale)



##########################################################
### maps
years = range(1987, 2020)
for y in years:
    image = ee.Image('users/philipperufin/susadica_map_v034_'+ str(y))
    description = 'susadica_map_v034_'+ str(y)
    folder = 'SUSADICA_v03'
    scale = 30
    fct.exp.exportDrive(image, description, folder, scale)

### stm
years = [1998, 2003, 2013, 2018]
for y in years:
    image = ee.Image('users/philipperufin/susadica_sstm_'+str(y))
    description = 'susadica_stm_'+str(y)
    folder = 'SUSADICA'
    scale = 30
    fct.exp.exportDrive(image, description, folder, scale)

features = ['all', 'ndvi', 'sstm', 'astm']
for feats in features:
    #.arrayProject([0]).arrayFlatten([['camp', 'other']])
    image = ee.Image('users/philipperufin/caucasus_camps_v04_prbs').toInt16()
    description = 'caucasus_camps_v04_prbs'
    folder = 'camps'
    scale = 10
    fct.exp.exportDrive(image, description, folder, scale)



# export srtm mask for caucasus
srtm_image = ee.Image("NASA/NASADEM_HGT/001").select('elevation').gt(1000)

# mask to roi
roi_shp = gpd.read_file(r'D:\PRJ_TMP\CAMPS\camps_v4\roi.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)
srtm_image = maskInside(srtm_image, roi)

description = 'caucasus_srtm_mask'
folder = 'camps'
scale = 10
fct.exp.exportDrive(srtm_image.toByte(), description, folder, scale)



### export srtm for susadica
srtm_image = ee.Image("NASA/NASADEM_HGT/001").select('elevation')

# mask to roi
roi_shp = gpd.read_file(r'P:\SUSADICA\vector\roi\roi_prv_v03.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)
srtm_image = maskInside(srtm_image, roi)

description = 'SUSADICA_SRTM'
folder = 'SUSADICA'
scale = 30
fct.exp.exportDrive(srtm_image.toInt16(), description, folder, scale)


### export slope for susadica
srtm_image = ee.Image("NASA/NASADEM_HGT/001").select('elevation')
slope_image = ee.Terrain.slope(srtm_image).multiply(100).toInt16()

# mask to roi
roi_shp = gpd.read_file(r'P:\SUSADICA\vector\roi\roi_prv_v03.shp')
g = json.loads(roi_shp.to_json())
coords = list(g['features'][0]['geometry']['coordinates'])
roi = ee.Geometry.Polygon(coords)
slope_image = maskInside(slope_image, roi)

description = 'SUSADICA_SLOPES'
folder = 'SUSADICA'
scale = 30
fct.exp.exportDrive(slope_image, description, folder, scale)

