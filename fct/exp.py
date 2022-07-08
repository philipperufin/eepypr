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