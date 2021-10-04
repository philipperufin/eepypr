import ee
import fct.exp
import json
import geopandas as gpd
def maskInside(image, geometry):
    mask = ee.Image.constant(1).clip(geometry).mask().eq(1)
    return image.updateMask(mask)


ee.Initialize()

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



# export srtm for susadica
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


# export psm stm mecurubi
image = ee.Image('users/philipperufin/fsda_lichinga_psm_coreg_100m_ssnl_annl_stm_2021')
description = 'fsda_lichinga_psm_coreg_100m_ssnl_annl_stm_2021'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(image, description, folder, scale)


# export lc map lichinga
image = ee.Image('users/philipperufin/nicfi_lc_lichinga_coreg_100m_ssnl_annl_stm_2021')
description = 'nicfi_lc_lichinga'
folder = 'NICFI_LC'
scale = 4.77
fct.exp.exportDrive(image, description, folder, scale)