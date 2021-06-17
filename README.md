# landsat_8_collection_2_cloud_mask
Using the QA_PIXEL band to mask clouds in Landsat 8 Collection 2 imagery

With the recent USGS Landsat 8 Collection 2 release, the cloud mask data generated from the *QA_MASK* raster is set up as a set of bit values. In this project, I automate creation of cloud masks for Collection 2. This project calculates all possible cloud-based pixels from the *QA_MASK* and writes the finished cloud mask as a raster file, ready for further manipulation in concert with Landsat 8 spectral bands.

More information on the quality bands for Landsat Collection 2 can be found [here](https://www.usgs.gov/core-science-systems/nli/landsat/landsat-collection-2-quality-assessment-bands).

The USGS lists updates on known issues with Landsat 8 Collection 2 [here](https://www.usgs.gov/core-science-systems/nli/landsat/landsat-collection-2-known-issues), which should be referenced before working on a new project for any changes to the data that you should be aware of. 
