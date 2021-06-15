## author: luo xin, date: 2021.6.15

import numpy as np
from osgeo import osr

def get_srs_proj(gdal_proj):
    '''
    input:
        gdal_proj: obtained by gdal.Open() and .GetProjection(), or by tiff_io.readTiff()['geoproj']
    return: 
        projection and georeference information
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(gdal_proj)
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def proj_to_wgs84(x, y, gdal_proj):
    '''
    des: convet projection coordinate to wgs84 coordinate
    input:
        x: projection coor x
        y: projection coor y
        gdal_proj: obtained by gdal.Open() and .GetProjection(), or by tiff_io.readTiff()['geoproj']
    return: 
        wgs84 coor lon lat which corresponding to projection coor x and y.
    '''
    prosrs, geosrs = get_srs_proj(gdal_proj)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def wgs82_to_proj(lon, lat, gdal_proj):
    '''
    des: convet wgs84 coordinate to projection coordinate 
    input:
        gdal_proj: obtained by gdal.Open() and .GetProjection(), or by tiff_io.readTiff()['geoproj']
        lon: wgs84 lon
        lat: wgs84 lat
    return: 
        projection coor x and y which corresponding to wgs84 lon lat.
    '''
    prosrs, geosrs = get_srs_proj(gdal_proj)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)


def geo2imagexy(lon, lat, gdal_trans):
    '''
    des: from georeferenced location (i.e., lon, lat) to image location(col,row).
    input:
        gdal_proj: obtained by gdal.Open() and .GetGeoTransform(), or by tiff_io.readTiff()['geotrans']
        lon: project or georeferenced x, i.e.,lon
        lat: project or georeferenced y, i.e., lat
    return: 
        image col and row corresponding to the georeferenced location.
    '''
    a = np.array([[gdal_trans[1], gdal_trans[2]], [gdal_trans[4], gdal_trans[5]]])
    b = np.array([lon - gdal_trans[0], lat - gdal_trans[3]])
    col_fps, row_fps = np.linalg.solve(a, b)
    col_fps, row_fps = np.floor(col_fps).astype('int'), np.floor(row_fps).astype('int')
    return row_fps, col_fps

def imagexy2geo(row, col, gdal_trans):
    '''
    input: 
        img_gdal: GDAL data (read by gdal.Open()
        row and col are corresponding to input image (dataset)
    :return:  
        geographical coordinates
    '''
    px = gdal_trans[0] + col * gdal_trans[1] + row * gdal_trans[2]
    py = gdal_trans[3] + col * gdal_trans[4] + row * gdal_trans[5]
    return px, py

