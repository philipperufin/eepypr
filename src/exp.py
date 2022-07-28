'''
#######################################################
eepypr
Functions wrapping export to drive statements into functions
#######################################################
'''

import ee
ee.Initialize()

def exportDrive(image, description, folder, scale, crs='EPSG:4326'):

    task = ee.batch.Export.image.toDrive(**{
        'image': image,
        'description': description,
        'folder': folder,
        'scale': scale,
        'crs': crs,
        'maxPixels': 1e13
    })
    task.start()

def exportRegionDrive(image, description, folder, scale, region, crs='EPSG:4326'):

    task = ee.batch.Export.image.toDrive(**{
        'image': image,
        'description': description,
        'folder': folder,
        'scale': scale,
        'crs': crs,
        'region': region,
        'maxPixels': 1e13
    })
    task.start()

def exportCollectionItemsDrive(col, id_field, drive_folder, region, scale=30, crs=4326, bands='all'):

    if not bands == 'all':
        col = col.select(bands)

    ids = col.aggregate_array(id_field).getInfo()

    for id in ids:
        print(id)
        image = col.filterMetadata(id_field, 'equals', id).first()
        description = id

        task = ee.batch.Export.image.toDrive(**{
            'image': image,
            'description': description,
            'folder': drive_folder,
            'scale': scale,
            'crs': crs,
            'region': region,
            'maxPixels': 1e13
        })
        task.start()

