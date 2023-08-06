This Python package is BUilding Footprint Extractor Test

This of example of an how you can run your code

```python
import LasBuildSeg as Lasb
import numpy as np
 


Lasb.generate_dsm('USGS_LPC_IL_HicksDome_FluorsparDistrict_2019_D19_2339_5650.laz', 8734, 1)
Lasb.generate_dtm('USGS_LPC_IL_HicksDome_FluorsparDistrict_2019_D19_2339_5650.laz', 8734, 1)
Lasb.generate_ndhm('dtm.tif', 'dsm.tif')
img, profile = Lasb.read_geotiff('ndhm.tif')
img_8bit = Lasb.to_8bit(img)
constant = 4.6
block_size = 51
img_thresh = Lasb.threshold(img_8bit, block_size, constant)
kernel_size = 3
img_open = Lasb.morphopen(img_thresh, kernel_size)
min_size=35
max_size=5000
building_mask = Lasb.filter_contours(img_open, profile, min_size, max_size)
kernel_size = 3
CloseKernel_size=15
building_mask_closed = Lasb.close(building_mask, CloseKernel_size)
# Invert the building mask to make buildings appear as white ground pixels
inverted_building_mask = np.ones_like(building_mask, dtype=np.uint8) - building_mask_closed
Lasb.write_geotiff('buildings.tif', inverted_building_mask, profile)
print('All of our steps are done.')