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



## Get the NIR band.
## var nir = image.select('N');

## Compute the gray-level co-occurrence matrix (GLCM), get contrast.
## var glcm = nir.glcmTexture({size: 3}).select('N_contrast').toInt16().rename()
## var contrast = .select('N_contrast')