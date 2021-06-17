### ----- author: luo xin, date: 2021.6.15 -----

import numpy as np
from osgeo import osr

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
