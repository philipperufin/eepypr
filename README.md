
## Overview 
A suite of functionalities for mass-processing of satellite imagery in Google Earth Engine. It has been created to facilitate pre-processing and time series analyses of Landsat, Sentinel-2 and NICFI PlanetScope data. 
Key functionalities vary across sensors but include

- cross-sensor collection integration (Landsat C1)
- cloud-masking (Landsat C1, Sentinel-2)
- co-registration using image.displace() (PlanetScope ~ Sentinel-2)
- spectral-temporal metrics (Landsat, Sentinel-2, PlanetScope)
- glcm texture metrics (Landsat, Sentinel-2, PlanetScope)
- facilitated image-wise exports of ee.ImageCollections to Google Drive
- conversion of local vector files to ee.FeatureGeometry or ee.FeatureCollections 

## Structure
- **src/** eepypr core functions
- **app/** application examples
    - **nicfi stm** generate spectral-temporal metrics from NICFI PlanetScope mosaics with optional coregistration based on Sentinel-2
    - **aralsea_stm** spectral-temporal metrics from Landsat Collection 1 data

## References 
The functions in this module were created and used in research conducted at Humboldt-Universität zu Berlin (Germany) and UCLouvain (Belgium), such as a paper on [large-area mapping of smallholder agriculture](https://doi.org/10.1016/j.jag.2022.102937), or [mapping post-Soviet cropping practices upstream of the Aral Sea basin](https://doi.org/10.1088/1748-9326/ac8daa). For further information read the function descriptions or contact philippe.rufin@uclouvain.be.

## Suggested Alternatives
I warmly recommend using the richer and more user-friendly GEEO library developed by my colleague Leon Nill: https://github.com/leonsnill/geeo/