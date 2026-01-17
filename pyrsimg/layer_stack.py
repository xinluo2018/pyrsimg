'''
author: xin luo
create: 2025.7.3
des: remote sensing images stacking
'''

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.coords import BoundingBox

def resample_to_match(target_src, reference_src):
    """
    des: resample a target raster to match the spatial reference and resolution to a reference raster
    args:
      target_src: target rasterio dataset to be resampled
      reference_src: reference rasterio dataset to match
    returns:
      resampled: resampled image array (bands, rows, cols)
    exceptions:
      ValueError: if the spatial references are different or there is no common area
    """

    # 1. check spatial reference
    if target_src.crs != reference_src.crs:
        raise ValueError("两幅影像的空间参考(CRS)不同")
    
    # 2. check spatial extent
    target_bounds = target_src.bounds
    reference_bounds = reference_src.bounds
    
    # obtain the intersection of the two bounding boxes
    intersect_bounds = BoundingBox(
        left=max(target_bounds.left, reference_bounds.left),
        right=min(target_bounds.right, reference_bounds.right),
        bottom=max(target_bounds.bottom, reference_bounds.bottom),
        top=min(target_bounds.top, reference_bounds.top)
    )
    
    # check if the intersection is valid
    if (intersect_bounds.left >= intersect_bounds.right or 
        intersect_bounds.bottom >= intersect_bounds.top):
        raise ValueError("两幅影像没有共同区域")
    
    # 3. initialize the output array
    resampled = np.empty(
        (target_src.count, reference_src.height, reference_src.width),
        dtype=target_src.dtypes[0]
    )
    
    # 4. reproject each band of the source raster to the reference raster
    reproject(
        source=rasterio.band(target_src, range(1, target_src.count + 1)),
        destination=resampled,
        src_transform=target_src.transform,
        src_crs=target_src.crs,
        dst_transform=reference_src.transform,
        dst_crs=reference_src.crs,
        dst_resolution=reference_src.res,
        resampling=Resampling.nearest
    )
    
    return resampled

def stack_imgs(src1, src2, intersect=False):
    """
    des: stack two raster images' bands into a single numpy array
    args:
      src1, src2: rasterio dataset objects representing the two images
      intersect: whether to use the intersection of the two images' extents (default is False, meaning use the union of the extents)
    returns:
      stacked: numpy array containing the stacked bands of both images
      out_meta: metadata for the output image
      out_transform: the geographic transformation for the output image 
    """
    
    if intersect:
        # use the union of the bounding boxes
        bounds = BoundingBox(
            left=min(src1.bounds.left, src2.bounds.left),
            bottom=min(src1.bounds.bottom, src2.bounds.bottom),
            right=max(src1.bounds.right, src2.bounds.right),
            top=max(src1.bounds.top, src2.bounds.top)
        )
    else:
        # use the intersection of the bounding boxes
        bounds = BoundingBox(
            left=max(src1.bounds.left, src2.bounds.left),
            bottom=max(src1.bounds.bottom, src2.bounds.bottom),
            right=min(src1.bounds.right, src2.bounds.right),
            top=min(src1.bounds.top, src2.bounds.top)
        )
        # check if the intersection is valid
        if bounds.left >= bounds.right or bounds.bottom >= bounds.top:
            raise ValueError("no common area between the two images")

    # calculate the output width and height based on the bounds and resolution
    res = src1.res  # use the resolution of the first image
    width = int((bounds.right - bounds.left) / res[0])
    height = int((bounds.top - bounds.bottom) / res[1])
    
    # create the output transform based on the bounds and resolution
    out_transform = rasterio.transform.from_origin(
        bounds.left, bounds.top, res[0], res[1]
    )
    
    # initialize the output array
    total_bands = src1.count + src2.count
    stacked = np.empty((total_bands, height, width), dtype=float)
    
    # reproject and stack the first image
    for band in range(src1.count):
        reproject(
            source=rasterio.band(src1, band + 1),
            destination=stacked[band],
            src_transform=src1.transform,
            src_crs=src1.crs,
            dst_transform=out_transform,
            dst_crs=src1.crs,
            resampling=Resampling.nearest
        )
    
    # resample the second image to and stack it
    for band in range(src2.count):
        reproject(
            source=rasterio.band(src2, band + 1),
            destination=stacked[src1.count + band],
            src_transform=src2.transform,
            src_crs=src2.crs,
            dst_transform=out_transform,
            dst_crs=src1.crs,  # use the coordinate system of src1
            resampling=Resampling.nearest
        )
    
    # prepare the output metadata
    out_meta = src1.meta.copy()
    out_meta.update({
        'height': height,
        'width': width,
        'transform': out_transform,
        'count': total_bands
    })
    
    return stacked, out_meta
