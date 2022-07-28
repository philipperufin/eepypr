
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

## References 
The functions in this module were created and used in research conducted at Humboldt-Universität zu Berlin (Germany) and UCLouvain (Belgium), such as a paper on [large-area mapping of smallholder agriculture](https://eartharxiv.org/repository/dashboard/3174/), or [mapping post-Soviet cropping practices upstream of the Aral Sea basin](https://meetingorganizer.copernicus.org/EGU21/EGU21-16266.html). For further information read the function descriptions or contact philippe.rufin@uclouvain.be.

