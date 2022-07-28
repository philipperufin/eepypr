'''
#######################################################
eepypr
Functions returning collections of NICFI PlanetScope mosaics. 
For more information and licensing visit 
https://www.planet.com/nicfi/

Accessing NICFI PlanetScope collections requires registration: 
https://developers.planet.com/docs/integrations/gee/nicfi/

startDate / endDate must be provided as datetime object
mark beginning and end of collection period.

region_key must be one of the following: 
'africa', 'americas', 'asia'

bands B, G, R, NIR renamed to blue, green, red, nir.
ndvi band added
#######################################################
'''

import ee
import datetime
import json
import geopandas as gpd

def PSM(startDate, endDate, region_key='africa'):

    bands = ee.List(['B', 'G', 'R', 'N'])
    band_names = ee.List(['blue', 'green', 'red', 'nir'])

    psm = ee.ImageCollection("projects/planet-nicfi/assets/basemaps/"+region_key)\
                .filter(ee.Filter.date(startDate, endDate))\
                .select(bands, band_names)

    psm = psm.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red'])\
                                               .multiply(10000).toInt16().rename('ndvi')))

    return psm


def PSM_REG2SEN(startDate, endDate, roi, region_key='africa',ref_img='users/philipperufin/sen4reg_cdi_2020-09-12',
                                   ref_bnd='nir_med', trg_bnd='nir', mo=100, st=5):

    if isinstance(roi, str):
        # define roi
        roi_shp = gpd.read_file(roi)
        g = json.loads(roi_shp.to_json())
        coords = list(g['features'][0]['geometry']['coordinates'])
        roi = ee.Geometry.Polygon(coords)

    bands = ee.List(['B', 'G', 'R', 'N'])
    band_names = ee.List(['blue', 'green', 'red', 'nir'])

    # fetch collection and rename bands
    psm = ee.ImageCollection("projects/planet-nicfi/assets/basemaps/"+region_key)\
                .select(bands, band_names)

    psm = psm.map(lambda image: image.addBands(image.normalizedDifference(['nir', 'red'])\
                                               .multiply(10000).toInt16().rename('ndvi')))

    # define reference image
    as_ref = ee.Image(ref_img).clip(roi)

    # filter date range
    psm = psm.filter(ee.Filter.date(startDate, endDate))

    # register each image in collection
    i = 1
    ids = psm.aggregate_array('system:index').getInfo()

    for id in ids:

        to_reg = ee.Image(psm.filterMetadata('system:index', 'equals', id).first()).clip(roi)

        #print(id)
        #print('do coreg')

        # choose to register using only the 'NIR' band.
        to_reg_nir = to_reg.select(trg_bnd)
        as_ref_nir = as_ref.select(ref_bnd)

        displacement = to_reg_nir.displacement(as_ref_nir, maxOffset=mo, stiffness=st)

        # use the computed displacement to register all original bands.
        registered = to_reg.displace(displacement)

        # add registered image to image list
        if i == 1:
            images = ee.List([registered])
        if i > 1:
            images = images.add(registered)
        i = i + 1

    # convert image list to image collection
    psm_reg = ee.ImageCollection(images)
    return psm_reg
