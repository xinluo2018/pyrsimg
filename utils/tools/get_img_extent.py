# author: xin luo
# create: 2022.3.26; modify: xxxx
# des: obtain the geographic extent of image: (west, right, south, north)
# usage: python get_extent.py $path_img

import argparse
from osgeo import gdal, osr

def get_args():
      """ Get command-line arguments. """
      parser = argparse.ArgumentParser(
            description='get extent of the given image')
      parser.add_argument(
            'path_img', metavar='path_img', type=str, nargs='+',
            help='path of the remote sensing image (.tif)')
      return parser.parse_args()

def get_extent(path_img):
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

if __name__ == '__main__':
      # extract arguments 
      args = get_args()
      path_img = args.path_img[0]     # input file(s)
      extent, espg_code = get_extent(path_img)
      print(extent[0],extent[1],extent[2],extent[3])