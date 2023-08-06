This Python package is BUilding Footprint Extractor Test

This of example of an how you can run your code

```python
import LasBuildSeg as lasb
import numpy as np

input_laz = '<input>.laz'
epsg_code = <epsg_code>
dsm_resolution = <resolution>

lasb.generate_dsm(input_laz, epsg_code, dsm_resolution)
lasb.generate_dtm(input_laz, epsg_code , dsm_resolution)
lasb.generate_ndhm('dtm.tif', 'dsm.tif')

img, profile = lasb.read_geotiff('ndhm.tif')
lasb.DSM_Transform('dsm.tif')

dem, _ = lasb.read_geotiff('dsm3857.tif')
img_8bit = lasb.to_8bit(img)
constant = 3.6
block_size = 51
img_thresh = lasb.threshold(img_8bit, block_size, constant)
kernel_size = 3
img_open = lasb.morphopen(img_thresh, kernel_size)
min_size=35
max_size=5000
tri_threshold=3
building_mask = lasb.filter_contours(img_open, dem, profile, min_size, max_size, tri_threshold=tri_threshold)
kernel_size = 3
CloseKernel_size=15
building_mask_closed = lasb.close(building_mask, CloseKernel_size)
# Invert the building mask to make buildings appear as white ground pixels
inverted_building_mask = np.ones_like(building_mask, dtype=np.uint8) - building_mask_closed
lasb.write_geotiff('buildings.tif', building_mask_closed, profile)
lasb.building_footprints_to_geojson('buildings.tif', 'building.geojson')
print('All of our steps are done.')