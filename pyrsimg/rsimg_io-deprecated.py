## author: xin luo 
## creat: 2021.6.18; modify: 2023.10.6
## des: .tif image reading and written.


import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
### tiff image reading
class readTiff():
    '''
    des: read in .tiff image.
    arg:
        path_in: image path
    return: 
        img: numpy array of image
        bands: number of bands. 
        geoexent: tuple, (x_min, x_max, y_min, y_max) 
        row: number of rows of the image
        col: number of cols of the image
    '''
    def __init__(self, path_in):
        with rasterio.open(path_in) as src:
            self.transform = src.transform  
            self.row = src.height
            self.col = src.width
            self.bands = src.count

            if src.crs:
                self.epsg_code = src.crs.to_epsg()
            else:
                self.epsg_code = None
            
            self.array = src.read().astype(float)
            if self.bands > 1:
                self.array = np.transpose(self.array, (1, 2, 0))
            else:
                self.array = self.array[0, :, :]
    @property
    def geoextent(self):
        bounds = rasterio.transform.array_bounds(self.row, self.col, self.transform)
        return (bounds[0], bounds[2], bounds[1], bounds[3])


###  .tiff image write
def writeTiff(im_data, im_geotrans, epsg_code, path_out):
    '''
    input:
        im_data: tow dimentions (order: row, col),or three dimentions (order: row, col, band)
        epsg_code: epsg code correspond to image spatial reference system.
    '''
    im_data = np.squeeze(im_data)
    if 'int8' in im_data.dtype.name:
        dtype = 'uint8'  
    elif 'int16' in im_data.dtype.name:
        dtype = 'int16'
    else:
        dtype = 'float32'

    if im_data.ndim == 3:
        im_data = np.transpose(im_data, (2, 0, 1))
        count, height, width = im_data.shape
    else:
        height, width = im_data.shape
        count = 1
        im_data = im_data[np.newaxis, :, :]

    if not isinstance(im_transform, Affine):
        im_transform = Affine.from_gdal(*im_transform)

    profile = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': count,
        'dtype': dtype,
        'crs': CRS.from_epsg(epsg_code) if epsg_code else None,
        'transform': im_transform,
        'tiled': True,
        'compress': 'lzw'
    }

    with rasterio.open(path_out, 'w', **profile) as dst:
        dst.write(im_data)