import ee

ee.Initialize()

def exportDrive(image, description, folder, scale):

    task = ee.batch.Export.image.toDrive(**{
        'image': image,
        'description': description,
        'folder': folder,
        'scale': scale,
        'maxPixels': 1e13
    })
    task.start()

def exportRegionDrive(image, description, folder, scale, region):

    task = ee.batch.Export.image.toDrive(**{
        'image': image,
        'description': description,
        'folder': folder,
        'scale': scale,
        'region': region,
        'maxPixels': 1e13
    })
    task.start()