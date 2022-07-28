'''
#######################################################
eepypr
Functions for returning quality-masked images,
removing cloud, cloud shadow, snow & ice
#######################################################
'''

import ee

def getQABit(image, start, end, newName):
    pattern = 0
    for i in range(start, end + 1):
        pattern += 2 ** i
    return image.select([0], [newName]).bitwiseAnd(pattern).rightShift(start)

# todo: add option to choose QAbits for water / snow & ice / cloud conf
def maskLNDquality(image):
    # Select the QA band.
    QA = image.select('pixel_qa')
    # Get the internal_cloud_algorithm_flag bit.
    shadow = getQABit(QA, 3, 3, 'cloud_shadow')
    cloud = getQABit(QA, 5, 5, 'cloud')
    snow = getQABit(QA, 4, 4, 'snow')
    med_cld = getQABit(QA, 7, 7,  'med_cld_conf')
    cirrus = getQABit(QA, 9, 9, 'cirrus')
    # Return an image masking out cloudy areas.
    return image.updateMask(cloud.eq(0))\
                .updateMask(shadow.eq(0))\
                .updateMask(snow.eq(0))\
                .updateMask(med_cld.eq(0))\
                .updateMask(cirrus.eq(0))


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


# function to mask clouds based on cloud displacement index
# threshold obtained from Qiu et al. 2019
# doi: https://doi.org/10.1016/j.rse.2019.05.024
def maskS2cdi(image):
    cdi = ee.Algorithms.Sentinel2.CDI(image)
    return image.updateMask(cdi.gt(-0.8)).addBands(cdi)