## author: luo xin, sun chenyu
## creat: 2021.6.15, modify: 2025.11.29
## des: image location transform between different coordinate system. 

import numpy as np
import rasterio
from rasterio.transform import Affine
from pyproj import transformer, CRS

def get_utm_zone(lon):
    '''
    des: get utm zone from the given wgs84 coordinates. 
    lon: the given longitute, should be in the range of [-180, 180].  
    return: utm_zone number. 
    '''
    utm_zone = np.floor(lon/6)+31  
    return int(utm_zone)

def coor2coor(srs_from, srs_to, x, y):
    """ Transform coordinates from srs_from to srs_to
    args:
        srs_from and srs_to: EPSG number, (e.g., 4326, 3031)
        x and y are x-coord and y-coord corresponding to srs_from and srs_to    
    return:
        x-coord and y-coord in srs_to
    """
    crs_from = CRS.from_epsg(int(srs_from)) 
    crs_to = CRS.from_epsg(int(srs_to))
    transformer_obj = transformer.Transformer.from_crs(crs_from, crs_to, always_xy=True)
    x_to, y_to = transformer_obj.transform(x, y)
    return x_to, y_to

def geo2imagexy(x, y, transform, shape= None):
    '''
    des: from georeferenced location (i.e., lon, lat) to image location(col,row). 
    note: the coordinate system should be same between x/y and transform.
    args:
        transform: rasterio Affine object or GDAL tuple
        x: project or georeferenced x, i.e.,lon
        y: project or georeferenced y, i.e., lat
        shape: (optional) tuple (height, width) for boundary check.
               Default is None (no check).
    return: 
        row, col: image row and col (integer)
    '''
    if isinstance(transform, Affine):
        aff = transform
    elif isinstance(transform, (tuple, list)):
        aff = Affine.from_gdal(*transform)
    else:
        raise TypeError("Transform must be an Affine object or GDAL tuple.")
    row_img, col_img = rasterio.transform.rowcol(aff, x, y)
    ## Mask out the points outside the image.
    if shape is not None:
        h, w = shape[:2]
        if np.any((row_img < 0) | (row_img >= h) | (col_img < 0) | (col_img >= w)):
            raise IndexError('The x and y out of image range')
    return row_img, col_img

def imagexy2geo(row, col, transform):
    '''
    des: image location(row, col) to georeferenced location.
    args:
        row, col: pixel row and column
        transform: rasterio Affine object or GDAL tuple
    return:
        x, y: georeferenced coordinates
    '''
    if isinstance(transform, Affine):
        aff = transform
    elif isinstance(transform, (tuple, list)):
        aff = Affine.from_gdal(*transform)
    else:
        raise TypeError("Transform must be an Affine object or GDAL tuple.")
    x, y = aff * (col, row)
    return x, y

def deg2meter_resolution(degree_res, center_lat=0):
    """
    des: convert degree resolution to meter resolution
    args:
        degree_res: resolution in degree
        center_lat: the center latitude where the resolution is calculated
    return:
        tuple: (resolution in meters along longitude, and for latitude)
    """
    R = 6371000  # mean radius of the Earth in meters
    lat_res_m = degree_res * (np.pi * R / 180)  # convert latitude resolution (constant)
    lon_res_m = degree_res * (np.pi * R / 180) * np.cos(np.radians(center_lat))  # convert longitude resolution (varies with latitude)
    return (lon_res_m, lat_res_m)   

def meter2deg_resolution(meter_res, center_lat=0):
    """
    des: convert meter resolution to degree resolution
    args:
        meter_res: resolution in meters
        center_lat: the reference latitude where the resolution is calculated
    return:
        tuple: (resolution in degrees for longitude, and for latitude)  
    """
    R = 6371000
    lat_res_deg = (meter_res * 180) / (np.pi * R)  # convert latitude resolution (constant)
    lon_res_deg = (meter_res * 180) / (np.pi * R * np.cos(np.radians(center_lat)))  # convert longitude resolution (varies with latitude)
    return (lon_res_deg, lat_res_deg)

   