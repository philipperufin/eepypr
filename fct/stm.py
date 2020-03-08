import ee

def STM(collection):

    coll = collection.select('blue', 'green', 'red', 'nir', 'swir1', 'swir2')

    median = coll.reduce(ee.Reducer.percentile([50]))\
        .rename('blue_med', 'green_med', 'red_med', 'nir_med', 'swir1_med', 'swir2_med')

    sd = coll.reduce(ee.Reducer.stdDev())\
        .rename('blue_sd', 'green_sd', 'red_sd', 'nir_sd', 'swir1_sd', 'swir2_sd')

    p25 = coll.reduce(ee.Reducer.percentile([25]))\
        .rename('blue_p25', 'green_p25', 'red_p25', 'nir_p25', 'swir1_p25', 'swir2_p25')

    p75 = coll.reduce(ee.Reducer.percentile([75]))\
        .rename('blue_p75', 'green_p75', 'red_p75', 'nir_p75', 'swir1_p75', 'swir2_p75')

    iqr = p75.subtract(p25)\
        .rename('blue_iqr', 'green_iqr', 'red_iqr', 'nir_iqr', 'swir1_iqr', 'swir2_iqr')

    imean = coll.reduce(ee.Reducer.intervalMean(25, 75))\
        .rename('blue_imean', 'green_imean', 'red_imean', 'nir_imean', 'swir1_imean', 'swir2_imean')

    STM_features = ee.Image([median, sd, p25, p75, iqr, imean])

    return STM_features
