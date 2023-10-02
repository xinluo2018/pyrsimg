## author: xin luo, 
## creat: 2021.7.15
## modify: 2021.11.27

import numpy as np
from osgeo import ogr, gdal, osr


def raster2vec(path_raster, path_save, dn_values):
    ''' 
    des: Read input band with Rasterio
    input:
        raster_path, output_path: raster and ouput vector path
        dn_values: list, consist of the raster value to be vectorization
    return:
        vector (gpkg format) written to the given path.
    '''
    raster_ds = gdal.Open(path_raster)
    raster_band = raster_ds.GetRasterBand(1)
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster_ds.GetProjection())
    #  create output datasource
    dst_layername = "polygon"
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = drv.CreateDataSource(path_save)
    dst_layer = dst_ds.CreateLayer(dst_layername, geom_type=ogr.wkbPolygon, srs = raster_srs)
    newField = ogr.FieldDefn('DN', ogr.OFTInteger)
    dst_layer.CreateField(newField)
    dst_field = dst_layer.GetLayerDefn().GetFieldIndex('DN')
    print(dst_layer.GetFeatureCount())
    gdal.Polygonize(raster_band, None, dst_layer, dst_field, [])
    print(dst_layer.GetFeatureCount())
    for i in range(dst_layer.GetFeatureCount()):
      fea = dst_layer.GetFeature(i)
      if fea.GetField('DN') not in dn_values:
        dst_layer.DeleteFeature(i)
    dst_ds = None


def vec2mask(path_vec, path_raster, path_save=None):
    """
    des: generate/save mask file using the vector file(e.g.,.shp,.gpkg).
    author: jinhua zhang, create: 2021.3.13, modify by luo: 2021.11.27
    input: 
        path_vec: str, path of the vector data.
        path_raster: str, path of the raster data.
        path_save: str, path to save.
    retrun: 
        mask, np.array. and a .tiff file written to the given path.
    """
    raster, vec = gdal.Open(path_raster, gdal.GA_ReadOnly), ogr.Open(path_vec)
    x_res = raster.RasterXSize
    y_res = raster.RasterYSize
    layer = vec.GetLayer()
    if path_save is None:
        drv = gdal.GetDriverByName('MEM')
        targetData = drv.Create('', x_res, y_res, 1, gdal.GDT_Byte)
    else: 
        driver = gdal.GetDriverByName("GTiff")
        targetData = driver.Create(path_save, x_res, y_res, 1, gdal.GDT_Byte)

    targetData.SetGeoTransform(raster.GetGeoTransform())
    targetData.SetProjection(raster.GetProjection())
    band = targetData.GetRasterBand(1)
    NoData_value = -9999
    band.SetNoDataValue(NoData_value)
    band.FlushCache()
    gdal.RasterizeLayer(targetData, [1], layer, burn_values=[1])
    mask = targetData.ReadAsArray(0, 0, x_res, y_res)
    mask = np.where(mask>0, 1, 0)
    return mask

