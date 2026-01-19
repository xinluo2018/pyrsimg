## author: xin luo, 
## creat: 2021.7.15
## modify: 2026.1.11

import numpy as np
import rasterio
from rasterio import features
import geopandas as gpd
from shapely.geometry import shape

def raster2vec(path_raster, path_save, dn_values):
    ''' 
    des: Read input band with Rasterio
    input:
        raster_path, output_path: raster and ouput vector path
        dn_values: list, consist of the raster value to be vectorization
    return:
        vector (gpkg format) written to the given path.
    '''
    with rasterio.open(path_raster) as src:
        image = src.read(1) # 读取第一波段
        transform = src.transform
        crs = src.crs

        dn_set = set(dn_values)
        mask = np.isin(image, list(dn_set))

    shapes_generator = features.shapes(image, mask=mask, transform=transform)
    geoms = []
    values = []
    for polygon, value in shapes_generator:
        val = int(value)
        if val in dn_set:
            geoms.append(shape(polygon))
            values.append(val)
    if not geoms:
        print("No features found matching the DN values.")
        return

    gdf = gpd.GeoDataFrame({'DN': values}, geometry=geoms, crs=crs)
    driver = 'GPKG' if path_save.endswith('.gpkg') else 'ESRI Shapefile'
    gdf.to_file(path_save, driver=driver)
    print(f"Vector saved to {path_save}, Feature count: {len(gdf)}")

def vec2mask(path_vec, path_raster, path_save=None):
    """
    des: generate/save mask file using the vector file(e.g.,.shp,.gpkg).
    author: jinhua zhang, create: 2021.3.13, modify by luo: 2021.11.27
    input: 
        path_vec: str, path of the vector data.
        path_raster: str, path of the raster data.
        path_save: str, path to save.
    retrun: 
        mask: np.array (binary, 0/1)
    """
    gdf = gpd.read_file(path_vec)

    with rasterio.open(path_raster) as src:
        out_shape = src.shape
        out_transform = src.transform
        meta = src.meta.copy()

    if gdf.crs != meta['crs']:
        gdf = gdf.to_crs(meta['crs'])
    shapes = ((geom, 1) for geom in gdf.geometry)

    mask = features.rasterize(
        shapes=shapes,
        out_shape=out_shape,
        transform=out_transform,
        fill=0,       
        default_value=1, 
        dtype=rasterio.uint8
    )

    if path_save:
        meta.update({
            "driver": "GTiff",
            "height": out_shape[0],
            "width": out_shape[1],
            "count": 1,
            "dtype": rasterio.uint8,
            "nodata": 0 
        })
        with rasterio.open(path_save, 'w', **meta) as dst:
            dst.write(mask, 1)     
    return mask