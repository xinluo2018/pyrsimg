## author: xin luo
## create: 2026.3.23   
## des: Functions for raster transformation, including reprojection, resampling, cropping, etc.


import numpy as np
import rasterio as rio
from rasterio.warp import reproject, Resampling
from rasterio.warp import calculate_default_transform
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds

def raster_reproj(src, target_crs="EPSG:4326", resample_method=Resampling.nearest):
    """
    Reproject a raster to a specified CRS.
    Parameters:
        src (rasterio.io.DatasetReader): Source raster.
        target_crs (str): Target CRS in EPSG format.
        resample_method (Resampling): Resampling method to use.        
    Returns:
        src_reproj (rasterio.io.DatasetReader): Reprojected raster dataset.
    """
    transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height, *src.bounds)    
    kwargs = src.profile.copy()
    kwargs.update({
        'crs': target_crs, 'transform': transform,
        'width': width, 'height': height})
    
    memfile = rio.io.MemoryFile()
    with memfile.open(**kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rio.band(src, i),
                destination=rio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=target_crs,
                resampling=resample_method
            )
        src_reproj = memfile.open()  # Open the memory file as a rasterio dataset
    return src_reproj


## require modification.
class crop2extent():
    '''  
    des: crop image with specific geographical extent.
    args:
        extent: list (left, right, down, up), extent for image cropping. \
                              the extent should agree with the projection of input image.
    '''
    def __init__(self, extent, size_target=None):
        self.extent = extent
        self.size_target = size_target

    def img2extent(self, path_img, path_save=None):
        '''
        crop image to given extent/size.
        arg:
            path_img: string, the image path to be croped.
            size_target: size to which image should be croped 
                  list/tuple, (row, col)
            path_save: string, the path for output saving.    
        return: 
            img_croped: the croped image, np.array()
        '''
        with rio.open(path_img) as src:
            src_crs = src.crs
            src_nodata = src.nodata
            src_transform = src.transform
            nbands = src.count

            dx_src = src_transform[0]
            dy_src = src_transform[4] 

            xmin, xmax, ymin, ymax = self.extent
            if self.size_target is None:
                npix_x = int(np.round((xmax - xmin) / float(dx_src)))
                npix_y = int(np.round((ymin - ymax) / float(dy_src)))
            else:
                npix_x = self.size_target[1] # col
                npix_y = self.size_target[0] # row

            dst_transform = from_bounds(xmin, ymin, xmax, ymax, npix_x, npix_y)
            dst_array = np.zeros((nbands, npix_y, npix_x), dtype=src.profile['dtype'])

            if src_nodata is not None:
                dst_array.fill(src_nodata)
            else:
                dst_array.fill(0)

            reproject(
                source=rio.band(src, list(range(1, nbands + 1))),
                destination=dst_array,
                src_transform=src_transform,
                src_crs=src_crs,
                dst_transform=dst_transform,
                dst_crs=src_crs, 
                resampling=Resampling.bilinear,
                src_nodata=src_nodata,
                dst_nodata=src_nodata
            )

            if path_save is not None:
                kwargs = src.meta.copy()
                kwargs.update({
                    'driver': 'GTiff',
                    'height': npix_y,
                    'width': npix_x,
                    'transform': dst_transform
                })
                with rio.open(path_save, 'w', **kwargs) as dst:
                    dst.write(dst_array)
            if src_nodata is not None:
                dst_array = np.ma.masked_where(dst_array == src_nodata, dst_array)
                if hasattr(dst_array, 'data'):
                    pass 
            out_array = np.transpose(dst_array, (1, 2, 0))
            if nbands == 1:
                out_array = out_array[:, :, 0]

            return out_array
