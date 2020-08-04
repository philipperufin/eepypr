# ====================================================================================================#
#
# Title: Landsat and Sentinel-2 Image Compositing Tool
# Author: Leon Nill
# Last modified: 2019-06-20
#
# ====================================================================================================#

'''
This tool allows for creating pixel-based Landsat image composites based on the
approach of Griffiths et al. (2013): "A Pixel-Based Landsat Compositing Algorithm
for Large Area Land Cover Mapping".

Further, the user can specify the calculation of either spectral-temporal metrics (STMs) (e.g. mean, min, ...)
or pixel-based composites based on scoring functions that determine the suitability of each pixel.

-- User Requirements --
SENSOR               [STRING] – Single sensors or combinations (S2_L1C, S2_L2A, LS, L5, L7, L8, SL)

TARGET_YEARS         [INT] – List of integer years.
SURR_YEARS           INT – 'surrounding years', i.e. should adjacent years be considered for compositing
MONTHLY              BOOLEAN – if True, a monthly iteration is used, if False, iteration is over chosen
                     day of years
SCORE                [STRING] – Score paramater used to create image composite in "qualityMosaic()"-function.
                     ('SCORE', 'NDVI') Selection is based on the maximum of the given parameter, e.g. max NDVI
TARGET_MONTHS_client [INT] – List of target months
STMs                 [ee.Reducer] STMs as ee.Reducer object(s), e.g. ee.Reducer.mean()

ROI                  [xMin, yMin, xMax, yMax] – List of corner coordinates, e.g. [22.26, -19.54, 22.94, -18.89]
ROI_NAME             STRING – Name of the study area which will be used for the output filenames
EPSG                 STRING - Coordinate System !Currently disabled and exports are in WGS84!
PIXEL_RESOLUTION     INT/FLOAT – Output pixelsize in meters

CLOUD_COVER          INT/FLOAT – Maximum cloud cover percentage of scenes considered in pre-selection
BANDS                [STRING] – List of string band-names for export image (B,G,R,NIR,SWIR1,SWIR2,NDVI,TCW, ...)

DOY_RANGE            INT – Offset in days to consider around target doy
REQ_DISTANCE_client  INT – Distance from clouds/ c. shadows in pixels at which optimal conditions are expected
MIN_DISTANCE_client  INT - Minimum distance from clouds/ c. shadows in pixels
W_DOYSCORE_client    FLOAT – Weight of day of year in scoring (0-1)
W_YEARSCORE_client   FLOAT – Weight of year in scoring (0-1)
W_CLOUDSCORE_client  FLOAT – Weight of cloud distance in scoring (0-1)

'''

import ee

ee.Initialize()

from learthengine import generals
from learthengine import prepro
from learthengine import composite

import datetime
import numpy as np

# ====================================================================================================#
# USER INPUTS
# ====================================================================================================#

SENSOR = 'LS'  # either (S2_L1C, S2_L2A, LS, L5, L7, L8, SL)
CLOUD_COVER = 60  # maximum Cloud Cover
BANDS = ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']  # 'B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2', 'NDVI
PIXEL_RESOLUTION = 30  # target spatial (pixel) resolution
MASKS = ['cloud', 'cshadow', 'snow']  # !only for Landsat!, default = ['cloud', 'cshadow', 'snow']
EXCLUDE_SLC_OFF = True  # inlclude L7 scenes with defect scan-line corrector (after 31st May 2003)

ROI = ee.Geometry.Rectangle([-39.960000, -11.170000, -37.550000, -7.630000])# [37.755, 1.142, 37.855, 1.172] Kitui

ROI_NAME = 'CAATINGA'
EPSG = 'UTM'  # 'UTM' will automatically find UTM Zone of ROI, otherwise specify EPSG code

NOBS = False  # add layer of number of observations per pixel

SCORE = 'SCORE'  # switch to either process a PBC based on Griffiths et al. (2013) ('SCORE') or
# maximum NDVI composite ('MAX_NDVI') or any string used as name for STMs
STMs = None # [ee.Reducer.percentile([90])]  # None or list of metrics to calculate, e.g. [ee.Reducer.mean()]

TARGET_YEARS = [1985, 1994, 2004, 2014, 2019]  # 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020
SURR_YEARS = 1
TARGET_DOYS = [336]  # [16, 46, 75, 105, 136, 166, 197, 228, 258, 289, 319, 350]
DOY_RANGE = 182  # +- TARGET_DOY
DOY_VS_YEAR = 45  # DOY offset from target DOY at which a one year offset has the same score

MAX_CLOUDDISTANCE = 50
MIN_CLOUDDISTANCE = 5

WEIGHT_DOY = 0.5
WEIGHT_YEAR = 0.2
WEIGHT_CLOUD = 0.3

BANDNAME = 'SPEC'

export_option = "Drive"
asset_path = "users/philipperufin/test/"

RESAMPLE = None  # leave to None
REDUCE_RESOLUTION = None  # leave to None ee.Reducer.mean().unweighted()
NATIVE_RESOLUTION = 30  # leave to None


# ====================================================================================================#
# FUNCTIONS
# ====================================================================================================#

# --------------------------------------------------
# ADD BANDS
# --------------------------------------------------
def fun_add_doy_band(img):
    DOY_value = img.date().getRelative('day', 'year')
    DOY = ee.Image.constant(DOY_value).int().rename('DOY')
    DOY = DOY.updateMask(img.select('R').mask())
    return img.addBands(DOY)


def fun_doys(img):
    return ee.Feature(None, {'doy': img.date().getRelative('day', 'year')})


def fun_addyearband(img):
    YEAR_value = ee.Number.parse((img.date().format("YYYY")))
    YEAR = ee.Image.constant(YEAR_value).int().rename('YEAR')
    YEAR = YEAR.updateMask(img.select('R').mask())
    return img.addBands(YEAR)


def fun_addcloudband(img):
    CLOUD_MASK = img.mask().select('R')
    CLOUD_DISTANCE = CLOUD_MASK.Not() \
        .distance(ee.Kernel.euclidean(radius=REQ_DISTANCE, units='pixels')) \
        .rename('CLOUD_DISTANCE')
    CLIP_MAX = CLOUD_DISTANCE.lte(ee.Image.constant(REQ_DISTANCE))
    CLOUD_DISTANCE = CLOUD_DISTANCE.updateMask(CLIP_MAX)
    CLOUD_DISTANCE = CLOUD_DISTANCE.updateMask(CLOUD_MASK)
    return img.addBands(CLOUD_DISTANCE)


# ====================================================================================================#
# EXECUTE
# ====================================================================================================#
# select bits for mask
'''
dict_mask = {'cloud': ee.Number(2).pow(5).int(),
             'cshadow': ee.Number(2).pow(3).int(),
             'snow': ee.Number(2).pow(4).int()}

sel_masks = [dict_mask[x] for x in MASKS]
bits = ee.Number(1)

for m in sel_masks:
    bits = ee.Number(bits.add(m))
'''
# find epsg
if EPSG == 'UTM':
    EPSG = generals.find_utm(ROI)

for year in TARGET_YEARS:
    for i in range(len(TARGET_DOYS)):

        # time
        iter_target_doy = TARGET_DOYS[i]

        year_min = year - SURR_YEARS
        year_max = year + SURR_YEARS

        temp_filter = []
        for t in range(year_min, year_max + 1):
            temp_target_doy = datetime.datetime(t, 1, 1) + datetime.timedelta(iter_target_doy - 1)
            temp_min_date = (temp_target_doy - datetime.timedelta(DOY_RANGE - 1)).strftime('%Y-%m-%d')
            temp_max_date = (temp_target_doy + datetime.timedelta(DOY_RANGE - 1)).strftime('%Y-%m-%d')
            temp_filter.append(ee.Filter.date(temp_min_date, temp_max_date))

        time_filter = ee.Filter.Or(*temp_filter)

        REQ_DISTANCE = ee.Number(MAX_CLOUDDISTANCE)
        MIN_DISTANCE = ee.Number(MIN_CLOUDDISTANCE)

        # .filter(ee.Filter.calendarRange(year_min, year_max, 'year')) \
        # .filter(ee.Filter.calendarRange(iter_target_doy_min, iter_target_doy_max, 'day_of_year')) \

        # --------------------------------------------------
        # IMPORT ImageCollections
        # --------------------------------------------------
        imgCol_L5_SR = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR') \
            .filterBounds(ROI) \
            .filter(time_filter) \
            .filter(ee.Filter.lt('CLOUD_COVER_LAND', CLOUD_COVER)) \
            .map(prepro.rename_bands_l5) \
            .map(prepro.mask_landsat_sr(MASKS)) \
            .map(prepro.scale_img(0.0001, ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'], ['TIR'])) \
            .map(prepro.scale_img(0.1, ['TIR'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']))

        imgCol_L7_SR = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR') \
            .filterBounds(ROI) \
            .filter(time_filter) \
            .filter(ee.Filter.lt('CLOUD_COVER_LAND', CLOUD_COVER)) \
            .map(prepro.rename_bands_l7) \
            .map(prepro.mask_landsat_sr(MASKS)) \
            .map(prepro.scale_img(0.0001, ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'], ['TIR'])) \
            .map(prepro.scale_img(0.1, ['TIR'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']))

        # check SLC_OFF statement
        if EXCLUDE_SLC_OFF:
            imgCol_L7_SR = imgCol_L7_SR.filter(ee.Filter.date("1999-04-18", "2003-05-31"))

        imgCol_L8_SR = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
            .filterBounds(ROI) \
            .filter(time_filter) \
            .filter(ee.Filter.lt('CLOUD_COVER_LAND', CLOUD_COVER)) \
            .map(prepro.rename_bands_l8) \
            .map(prepro.mask_landsat_sr(MASKS)) \
            .map(prepro.scale_img(0.0001, ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2'], ['TIR'])) \
            .map(prepro.scale_img(0.1, ['TIR'], ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']))

        imgCol_S2_L1C = ee.ImageCollection('COPERNICUS/S2') \
            .filterBounds(ROI) \
            .filter(time_filter) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CLOUD_COVER)) \
            .map(prepro.mask_s2_cdi(-0.5)) \
            .map(prepro.rename_bands_s2) \
            .map(prepro.mask_s2) \
            .map(prepro.scale_img(0.0001, ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']))

        imgCol_S2_L2A = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(ROI) \
            .filter(time_filter) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CLOUD_COVER)) \
            .map(prepro.mask_s2_cdi(-0.5)) \
            .map(prepro.rename_bands_s2) \
            .map(prepro.mask_s2_scl) \
            .map(prepro.scale_img(0.0001, ['B', 'G', 'R', 'NIR', 'SWIR1', 'SWIR2']))

        # --------------------------------------------------
        # MERGE imgCols
        # --------------------------------------------------
        if SENSOR == 'S2_L1C':
            imgCol_SR = imgCol_S2_L1C
        elif SENSOR == 'S2_L2A':
            imgCol_SR = imgCol_S2_L2A
        elif SENSOR == 'LS':
            imgCol_SR = imgCol_L5_SR.merge(imgCol_L7_SR).merge(imgCol_L8_SR)
            imgCol_SR = imgCol_SR.sort("system:time_start")
        elif SENSOR == 'L8':
            imgCol_SR = imgCol_L8_SR
        elif SENSOR == 'L7':
            imgCol_SR = imgCol_L7_SR
        elif SENSOR == 'L5':
            imgCol_SR = imgCol_L5_SR
        elif SENSOR == 'SL8':
            imgCol_SR = imgCol_L8_SR.merge(imgCol_S2_L2A)
        elif SENSOR == 'SL':
            imgCol_SR = imgCol_L5_SR.merge(imgCol_L7_SR).merge(imgCol_L8_SR).merge(imgCol_S2_L2A)
        else:
            imgCol_SR = None
            print('No sensor specified!')

        # --------------------------------------------------
        # Calculate Indices
        # --------------------------------------------------
        imgCol_SR = imgCol_SR.map(prepro.ndvi)
        imgCol_SR = imgCol_SR.map(prepro.ndwi1)
        imgCol_SR = imgCol_SR.map(prepro.ndwi2)
        imgCol_SR = imgCol_SR.map(prepro.ndbi)
        imgCol_SR = imgCol_SR.map(prepro.tcg)
        imgCol_SR = imgCol_SR.map(prepro.tcb)
        imgCol_SR = imgCol_SR.map(prepro.tcw)

        # --------------------------------------------------
        # Add DOY, YEAR & CLOUD Bands to ImgCol
        # --------------------------------------------------
        imgCol_SR = imgCol_SR.map(fun_add_doy_band)
        imgCol_SR = imgCol_SR.map(fun_addyearband)
        imgCol_SR = imgCol_SR.map(fun_addcloudband)

        if SCORE == 'SCORE':
            # --------------------------------------------------
            # SCORING 1: DOY
            # --------------------------------------------------
            # add DOY-band to images in imgCol
            doys = imgCol_SR.map(fun_doys).aggregate_array('doy').getInfo()

            # retrieve target-DOY and DOY-std (client and server side)
            target_doy = ee.Number(iter_target_doy)

            doy_std_client = np.std(doys)

            doy_std = ee.Number(doy_std_client)

            # add Band with final DOY score to every image in imgCol
            imgCol_SR = imgCol_SR.map(composite.doyscore(doy_std, target_doy))

            # --------------------------------------------------
            # SCORING 2: YEAR
            # --------------------------------------------------
            # calculate DOY-score at maximum DOY vs Year threshold
            doyscore_offset = composite.doyscore_offset(iter_target_doy - DOY_VS_YEAR,
                                                        iter_target_doy, doy_std_client)
            doyscore_offset_obj = ee.Number(doyscore_offset)
            target_years_obj = ee.Number(year)

            # add Band with final YEAR score to every image in imgCol
            imgCol_SR = imgCol_SR.map(composite.yearscore(target_years_obj, doyscore_offset_obj))

            # --------------------------------------------------
            # SCORING 3: CLOUD DISTANCE
            # --------------------------------------------------
            imgCol_SR = imgCol_SR.map(composite.cloudscore(REQ_DISTANCE, MIN_DISTANCE))

            # --------------------------------------------------
            # FINAL SCORING
            # --------------------------------------------------
            w_doyscore = ee.Number(WEIGHT_DOY)
            w_yearscore = ee.Number(WEIGHT_YEAR)
            w_cloudscore = ee.Number(WEIGHT_CLOUD)

            imgCol_SR = imgCol_SR.map(composite.score(w_doyscore, w_yearscore, w_cloudscore))

            img_composite = imgCol_SR.qualityMosaic('PBC')
            img_composite = img_composite.select(BANDS)
            img_composite = img_composite.multiply(10000)
            img_composite = img_composite.int16()

            if STMs is not None:
                for i in range(len(STMs)):
                    img_composite = img_composite.addBands(ee.Image(imgCol_SR.select(BANDS) \
                                                                    .reduce(STMs[i])).int16())

        elif SCORE == 'MAXNDVI':
            img_composite = imgCol_SR.qualityMosaic('NDVI')
            img_composite = img_composite.select(BANDS)
            img_composite = img_composite.multiply(10000)
            img_composite = img_composite.int16()

            if STMs is not None:
                for i in range(len(STMs)):
                    img_composite = img_composite.addBands(ee.Image(imgCol_SR.select(BANDS) \
                                                                    .reduce(STMs[i])).int16())

        else:
            if STMs is not None:
                for i in range(len(STMs)):
                    if i == 0:
                        img_composite = ee.Image(imgCol_SR.select(BANDS).reduce(STMs[i]))
                    else:
                        img_composite = img_composite.addBands(ee.Image(imgCol_SR.select(BANDS) \
                                                                        .reduce(STMs[i])))

                img_composite = img_composite.multiply(10000)

        if NOBS:
            nobs = imgCol_SR.select(BANDS[0]).count().rename('NOBS')
            nobs = nobs.int16()
            try:
                img_composite = img_composite.addBands(nobs)
            except Exception:
                img_composite = nobs

        if SURR_YEARS == 0:
            year_filename = str(year)
        else:
            year_filename = str(year) + '-' + str(SURR_YEARS)

        out_file = SENSOR + '_' + SCORE + '_' + BANDNAME + '_' + ROI_NAME + '_' + \
                   str(PIXEL_RESOLUTION) + 'm_' + str(iter_target_doy) + '-' + str(DOY_RANGE) + \
                   '_' + str(year) + '-' + str(SURR_YEARS)

        if export_option == "Drive":
            out = ee.batch.Export.image.toDrive(image=img_composite.toInt16(), description=out_file,
                                                scale=PIXEL_RESOLUTION,
                                                maxPixels=1e13,
                                                region=ROI['coordinates'][0],
                                                crs=EPSG)
        elif export_option == "Asset":
            out = ee.batch.Export.image.toAsset(image=img_composite.toInt16(), description=out_file,
                                                assetId=asset_path + out_file,
                                                scale=PIXEL_RESOLUTION,
                                                maxPixels=1e13,
                                                region=ROI['coordinates'][0],
                                                crs=EPSG)

        process = ee.batch.Task.start(out)

# =====================================================================================================================#
# END
# =====================================================================================================================#