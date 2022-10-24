import ee
import src.vec
import datetime

ee.Initialize()

############################################
# params
############################################
# file path to ROI shapefile
roi_file = 'roi.shp'

# convert to ee.Geometry
roi = src.vec.shape2ee(roi_file)

# define temporal bins and reference image names
# order: start date, end date, reference image name

asset_folder = 'users/username/' # must exist

tempbins = [[datetime.datetime(2021, 9, 1), datetime.datetime(2021, 12, 31), 'sen4reg_cdi_2021-09-12'],
            [datetime.datetime(2022, 1, 1), datetime.datetime(2022,  4, 30), 'sen4reg_cdi_2022-01-04'],
            [datetime.datetime(2022, 5, 1), datetime.datetime(2022,  8, 31), 'sen4reg_cdi_2022-05-08']]

############################################
############################################
# iterate over tembins
for s, [startDate, endDate, ref_img] in enumerate(tempbins, start=1):
    print('\nCreating S2 reference for season ' + str(s))
    print('Starting ' + str(startDate) + ', ending ' + str(endDate))

    # create reference median nir
    ref = src.sen.SEN(startDate, endDate, cdi=True).select('nir')\
                    .reduce(ee.Reducer.percentile([50]))\
                    .rename('nir_med').toInt16()

    # export as asset
    print('Storing reference as ' + ref_img)
    task = ee.batch.Export.image.toAsset(**{
        'image': ref,
        'scale': 10,
        'region': roi,
        'description': ref_img,
        'assetId': asset_folder + ref_img,
        'maxPixels': 1e13
    })
    task.start()