# ee.pypr, philippe rufin 2020
# philippe.rufin@googlemail.com
#######################################################
# maskQuality function returns quality-masked image,
# removes cloud, cloud shadow, snow & ice
#######################################################

import ee

def getQABit(image, start, end, newName):
    pattern = 0
    for i in range(start, end + 1):
        pattern += 2 ** i
    return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)

# todo: add option to choose QAbits for water / snow & ice / cloud conf
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


def maskS2scl(image):
    # Select scene classification
    scl = image.select('SCL')
    sat = scl.neq(1)
    shadow = scl.neq(3)
    cloud_lo = scl.neq(7)
    cloud_md = scl.neq(8)
    cloud_hi = scl.neq(9)
    cirrus = scl.neq(10)
    snow = scl.neq(11)
    return image.updateMask(sat.eq(1)).updateMask(shadow.eq(1).updateMask(cloud_lo.eq(1).updateMask(cloud_md.eq(1).updateMask(cloud_hi.eq(1).updateMask(cirrus.eq(1).updateMask(snow.eq(1)))))))

#def maskS2qa(image):
#  qa = image.select('QA60')

#  // Bits 10 and 11 are clouds and cirrus, respectively.
#  var cloudBitMask = 1 << 10;
#  var cirrusBitMask = 1 << 11;

#  // Both flags should be set to zero, indicating clear conditions.
#  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
#      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

#  return image.updateMask(mask).divide(10000);
#}

# function to mask clouds based on cdi threshold
#def maskS2cdi(image):
#  cdi = ee.Algorithms.Sentinel2.CDI(image)
#  cdi_mask = cdi.lt(-0.5).rename("CDI")
#  return image.addBands(cdi).addBands(cdi_mask)

# function to mask additional clouds based on cloud displacement index
# threshold obtained from Qiu et al. 2019
# doi: https://doi.org/10.1016/j.rse.2019.05.024
def maskS2cdi(image):
    cdi = ee.Algorithms.Sentinel2.CDI(image)
    return image.updateMask(cdi.gt(-0.8)).addBands(cdi)
