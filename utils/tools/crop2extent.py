## author: xin luo
## create: 2021.11.27; modify: 2023.5.10
## des: crop one image/multiple tiled images to specific image size. usually used for alignment to 
##      another image.

import numpy as np
import pyproj
from glob import glob
import os
from osgeo import gdal, osr


def coor2coor(srs_from, srs_to, x, y):
    """
    Transform coordinates from srs_from to srs_to
    input:
        srs_from and srs_to: EPSG number, (e.g., 4326, 3031)
        x and y are x-coord and y-coord corresponding to srs_from and srs_to    
    return:
        x-coord and y-coord in srs_to 
    """
    transformer = pyproj.Transformer.from_crs(int(srs_from), int(srs_to), always_xy=True)
    return transformer.transform(x,y)

def get_img_extent(path_img):
      RS_Data=gdal.Open(path_img)
      im_col = RS_Data.RasterXSize  # 
      im_row = RS_Data.RasterYSize  # 
      im_geotrans = RS_Data.GetGeoTransform()  # 
      im_proj = RS_Data.GetProjection()  # 
      west = im_geotrans[0]
      north = im_geotrans[3]
      east = west + im_geotrans[1] * im_col + im_geotrans[2] * im_row
      south = north + im_geotrans[5] * im_row + im_geotrans[4] * im_col
      espg_code = osr.SpatialReference(wkt=im_proj).GetAttrValue('AUTHORITY',1)
      extent = (west, east, south, north)
      return extent, espg_code

def imgs_in_extent(paths_img, extent):
  '''
  des: selected imgs that in the given extent.
  arg:
    paths_img: list, images paths;
    extent: the given extent(wgs84). list -> [left, right, bottom, up]
  '''
  paths_imgs_extent = []
  for path_img in paths_img:
    extent_img, espg_code = get_img_extent(path_img)    
    xs = (extent_img[0], extent_img[1])
    ys = (extent_img[2], extent_img[3])
    if espg_code != '4326':
      lons_img, lats_img = coor2coor(srs_from=espg_code, srs_to='4326', x=xs, y=ys)
    else: 
      lons_img, lats_img = xs, ys

    lon_in_left = lons_img[1]<extent[0]       ### the case that image is on the left of the extent
    lon_in_right = lons_img[0]>extent[1]
    lat_in_up = lats_img[0]>extent[3]
    lat_in_down = lats_img[1]<extent[2]
    img_in = lon_in_left or lon_in_right or lat_in_up or lat_in_down    ## for each case, there is no overlap between the image and extent. 
    if img_in is False:
      paths_imgs_extent.append(path_img)
  return paths_imgs_extent


def img2extent(path_img, extent, size_target=None, path_save=None):
    '''
    crop image to given extent/size.
    arg:
        image: the image to be croped; np.array().
        extent: extent to which image should be croped;
                list/tuple,(left, right, down, up). 
        size_target: size to which image should be croped 
              list/tuple, (row, col)
    return: 
        img_croped: the croped image, np.array()
    '''

    rs_data=gdal.Open(path_img)
    dtype_id = rs_data.GetRasterBand(1).DataType
    dtype_name = gdal.GetDataTypeName(dtype_id)
    if 'int8' in dtype_name:
        datatype = gdal.GDT_Byte
    elif 'int16' in dtype_name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    geotrans = rs_data.GetGeoTransform()
    dx, dy = geotrans[1], geotrans[5]
    nbands = rs_data.RasterCount
    proj_wkt = rs_data.GetProjection()
    NDV = rs_data.GetRasterBand(1).GetNoDataValue()
    xmin, xmax, ymin, ymax = extent

    if size_target is None:
        npix_x = int(np.round((xmax - xmin) / float(dx)))  # new col
        npix_y = int(np.round((ymin - ymax) / float(dy)))  # new row
        dx = (xmax - xmin) / float(npix_x)
        dy = (ymin - ymax) / float(npix_y)
    else:
        npix_x = size_target[1]
        npix_y = size_target[0]
        dx = (xmax - xmin) / float(size_target[1])  # new resolution
        dy = (ymin - ymax) / float(size_target[0])

    if path_save is None:
        drv = gdal.GetDriverByName('MEM')
        dest = drv.Create('', npix_x, npix_y, nbands, datatype)
    else: 
        driver = gdal.GetDriverByName("GTiff")
        dest = driver.Create(path_save, npix_x, npix_y, nbands, datatype)
        
    dest.SetProjection(proj_wkt)
    newgeotrans = (xmin, dx, 0.0, ymax, 0.0, dy)
    dest.SetGeoTransform(newgeotrans)
    if NDV is not None:
        for i in range(nbands):
            dest.GetRasterBand(i+1).SetNoDataValue(NDV)
            dest.GetRasterBand(i+1).Fill(NDV)
    else:
        for i in range(nbands):
            dest.GetRasterBand(i+1).Fill(0)

    gdal.ReprojectImage(rs_data, dest, proj_wkt, proj_wkt, gdal.GRA_Bilinear)
    out_array = dest.ReadAsArray(0, 0,  npix_x,  npix_y)

    if NDV is not None:
        out_array = np.ma.masked_where(out_array == NDV, out_array).data

    if nbands > 1:
        return np.transpose(out_array, (1, 2, 0))  # 
    else:
        return out_array

def tiles2extent(dir_tiled_data, extent, path_save=None):
    '''
    args:
      dir_data: string, directory of the tiled data
      extent: list, [left, right, bottom, up], can be obtained by readTiff() function.
      path_save, str, the file path to be saved. 
    return:
        the croped image.
    '''
    paths_tile = glob(dir_tiled_data+'/*[!albers].tif')
    ### data mosaic
    paths_tile_sel = imgs_in_extent(paths_img=paths_tile, extent=extent)
    paths_tile_sel = " ".join(paths_tile_sel)
    command = "gdal_merge.py -co COMPRESS=LZW -o tiles_mosaic.tif " + paths_tile_sel   ## mosaic
    print(os.popen(command).read())
    ### data subseting
    img_croped = img2extent(path_img='tiles_mosaic.tif', extent=extent, path_save=path_save)
    os.remove('tiles_mosaic.tif')
    return img_croped
