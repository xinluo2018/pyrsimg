## author: xin luo 
## creat: 2022.9.30, modify: 2023.5.10
## des: select images in the given extent.
## usage: python utils/imgs_in_extent.py -imgs $paths_img -e $left $right $bottom $up

from glob import glob
import argparse
import pyproj
from osgeo import gdal, osr

def get_args():
    description = "find the images fall in the given extent."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-imgs', metavar='imgs', type=str, nargs='+',
        help=('images path for searching for.'))
    parser.add_argument(
        '-e', metavar=('left','right','bottom', 'up'), dest='extent', type=float, nargs=4,
        help=('extent for image finding.'),
        default=[91, 92, 27, 28])
    return parser.parse_args()

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

if __name__ == '__main__':
    args = get_args()
    paths_img = args.imgs[:]
    extent = args.extent[:]
    paths_imgs_extent = imgs_in_extent(paths_img, extent)
    for path in paths_imgs_extent:
        print(path)


