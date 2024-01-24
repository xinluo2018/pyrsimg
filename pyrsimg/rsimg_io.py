## author: xin luo 
## creat: 2021.6.18; modify: 2023.10.6
## des: .tif image reading and written.


import numpy as np
from osgeo import gdal, osr

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
        RS_Data=gdal.Open(path_in)
        self.geotrans = RS_Data.GetGeoTransform()  # 
        self.row = RS_Data.RasterYSize
        self.col = RS_Data.RasterXSize  # 
        self.bands = RS_Data.RasterCount 
        im_proj = RS_Data.GetProjection()
        self.epsg_code = int(osr.SpatialReference(wkt=im_proj).GetAttrValue('AUTHORITY',1))
        self.array = RS_Data.ReadAsArray(0, 0, self.col, self.row).astype(float)
        if self.bands > 1:
            self.array = np.transpose(self.array, (1, 2, 0)) # 
    @property
    def geoextent(self):
        left = self.geotrans[0]
        up = self.geotrans[3]
        right = left + self.geotrans[1] * self.col + self.geotrans[2] * self.row
        bottom = up + self.geotrans[5] * self.row + self.geotrans[4] * self.col
        extent = (left, right, bottom, up)
        return extent


###  .tiff image write
def writeTiff(im_data, im_geotrans, epsg_code, path_out):
    '''
    input:
        im_data: tow dimentions (order: row, col),or three dimentions (order: row, col, band)
        epsg_code: epsg code correspond to image spatial reference system.
    '''
    im_data = np.squeeze(im_data)
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_Int16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_data = np.transpose(im_data, (2, 0, 1))
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands,(im_height, im_width) = 1,im_data.shape
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path_out, im_width, im_height, im_bands, datatype, options=["TILED=YES", "COMPRESS=LZW"])
    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans)       # 
        dataset.SetProjection("EPSG:" + str(epsg_code))      # 
    if im_bands > 1:
        for i in range(im_bands):
            dataset.GetRasterBand(i+1).WriteArray(im_data[i])
        del dataset
    else:
        dataset.GetRasterBand(1).WriteArray(im_data)
        del dataset

