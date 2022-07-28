'''
#######################################################
eepypr
Functions for calculating texture features from image
#######################################################
'''

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


def GLCM(img, bands, sizes, metrics):

    it = 1

    for b in bands:
        base = img.select(b)

        for k in sizes:
            glcm = base.glcmTexture(size = k)

            for m in metrics:

                if it == 1:
                    glcm_img = glcm.select(b + '_' + m).rename(b + '_' + m + '_'+f'{int(k):02}')
                if it > 1:
                    glcm_img = glcm_img.addBands(glcm.select(b + '_' + m).rename(b + '_' + m + '_'+f'{int(k):02}'))

                it += 1
    return(glcm_img)

