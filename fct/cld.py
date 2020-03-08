import ee

def getQABit(image, start, end, newName):
    pattern = 0
    for i in range(start, end + 1):
        pattern += 2 ** i
    return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)


def maskClouds(image):

    QA = image.select(['pixel_qa'])
    #wt = getQABit(QA, 2, 2, 'Water').eq(0)
    cs = getQABit(QA, 3, 3, 'CloudShadows').eq(0)
    cd = getQABit(QA, 5, 5, 'Cloud').eq(0)
    si = getQABit(QA, 4, 4, 'SnowIce').eq(0)
    #mc = getQABit(QA, 7, 7, 'MedConfCloud').eq(0)
    #cc = getQABit(QA, 9, 9, 'MedConfCirr').eq(0)

    return image.updateMask(cs).updateMask(cd.updateMask(si))
    #return image.updateMask(cs)\
    #    .updateMask(cd)\
    #    .updateMask(si)\
    #    .updateMask(mc)\
    #    .updateMask(cc)\
    #    .rename('blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'pixel_qa')


def maskQuality(image):
    # Select the QA band.
    QA = image.select('pixel_qa')
    # Get the internal_cloud_algorithm_flag bit.
    shadow = getQABit(QA, 3, 3, 'cloud_shadow')
    cloud = getQABit(QA, 5, 5, 'cloud')
    snow = getQABit(QA, 4, 4, 'snow')
    #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
    # cirrus = getQABit(QA, 9, 9, 'cirrus')
    # Return an image masking out cloudy areas.
    return image.updateMask(cloud.eq(0)).updateMask(shadow.eq(0).updateMask(snow.eq(0)))
