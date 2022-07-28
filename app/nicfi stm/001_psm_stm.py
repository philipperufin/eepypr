import ee
import src.psm
import src.vec
import datetime
import geopandas as gpd

ee.Initialize()

############################################
# params
############################################
# file name of training tile grid and tile id field
tiles_shp = 'tiles.shp'
id_field = 'id'

# define temporal bins and reference images for seasons
# order: start date, end date, reference image for coregistration
tempbins = [[datetime.datetime(2020, 9, 1), datetime.datetime(2020, 12, 31)],
            [datetime.datetime(2021, 1, 1), datetime.datetime(2021,  4, 30)],
            [datetime.datetime(2021, 5, 1), datetime.datetime(2021,  8, 31)]]

# should coregistration be done?
do_coreg = True

# if do_coreg = True, provide reference image for each tempbin using their GEE asset IDs
# entries must be corresponding with the tempbins defined above
# these can be generated from a separate script: 000_sen4coreg.py
asset_base = 'users/username/'
ref_imgs = [asset_base + 'sen4reg_cdi_2020-09-12',
            asset_base + 'sen4reg_cdi_2021-01-04',
            asset_base + 'sen4reg_cdi_2021-05-08']

# define percentile reducers
# order: [spectral bands] and percentile to compute
reducers = [[['green', 'red', 'nir', 'ndvi'], 50],
            [['ndvi'], 75]]

# export options
exportAsAsset = True
asset_folder =  asset_base + 'nicfi_stm/' #must exist
description =  'nicfi_stm_tile_' #tile id will be appended

############################################
############################################
# open tile grid and fetch tile ids
tiles_gpd = gpd.read_file(tiles_shp)
fids = tiles_gpd[id_field]
print('Creating STM for ' + str(len(fids)) + ' tiles')

############################################
# loop to create stm task for each tile
for fid in fids:
    print('Tasking tile ' + str(fid))

    # grab tile by id
    tile_gpd = tiles_gpd[tiles_gpd[id_field]==fid]

    # convert to ee.Geometry
    tile = src.vec.feat2ee(tile_gpd)

    ############################################
    # iterate over tembins
    for s, [startDate, endDate] in enumerate(tempbins, start=1):

        print('\nTemporal binning for season ' + str(s))
        print('Starting ' + str(startDate) + ', ending ' + str(endDate))

        if do_coreg:
            # create co-registered image collection for tempbin
            print('Coreg based on reference ' + ref_imgs[s-1])
            col = src.psm.PSM_REG2SEN(startDate, endDate, region_key='africa', roi=tile, ref_img=ref_imgs[s - 1])

        if not do_coreg:
            # create co-registered image collection for tempbin
            print('Coreg disabled')
            col = src.psm.PSM(startDate, endDate, region_key='africa')

        ############################################
        # iterate over reducers
        for r, [bands, perc] in enumerate(reducers):
            print('\nAggregating ' + ' '.join(bands) + ' to ' + str(perc) + 'th percentile')
            print('Output: ' + ' '.join([f's{int(s):02}_' + b + '_p' + str(perc) for b in bands]))

            # reduce and rename to format 'season_band_percentile'
            per = col.select(bands).reduce(ee.Reducer.percentile([perc])) \
                .rename([f's{int(s):02}_' + b + '_p' + str(perc) for b in bands])

            # stack images from reducers
            if r==0:
                stm_s = per
            if r>0:
                stm_s = ee.Image([stm_s, per])

        # stack images from seasons
        if s==1:
            stm = stm_s
        if s>1:
            stm = ee.Image([stm, stm_s])

    ############################################
    # export as asset
    if exportAsAsset:
        print('Tasking export as asset')
        task = ee.batch.Export.image.toAsset(**{
            'image': stm.toInt16(),
            'scale': 4.77,
            'region': tile,
            'description': description + f'{int(fid):03}',
            'assetId': asset_folder + description + f'{int(fid):03}',
            'maxPixels': 1e13
        })
        task.start()