import ee


def TXT(img, bands, radius, ndi=True):

    img = img.addBands(img.select(bands).reduceNeighborhood(ee.Reducer.percentile([50]), ee.Kernel.circle(radius, 'meters'))\
                .rename(bands + '_p50_' + str(radius))\
                .toInt16())

    if ndi == True:

        img = img.addBands(img.normalizedDifference([bands, bands + '_p50_' + str(radius)]) \
                     .multiply(10000).toInt16() \
                     .rename([bands + '_p50_' + str(radius) + 'ndi']))
    return(img)