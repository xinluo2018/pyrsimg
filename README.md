# **pyrsimg**  
Toolkit for easy processing of remote sensing image, particularly the processing related to the applicaiton of deep learning method is considered.   

## **Installation**
1. install the pyrsimg package:   
```pip install pyrsimg```  
2. The dependency package of gdal should be installed:      
```conda install gdal```   
or:   
```pip install gdal```

## Examples:
1. [**Image reading and show.**](https://pyrsimg.readthedocs.io/en/latest/examples/read_and_show.html)   
2. [**Conversion from image to patch.**](https://pyrsimg.readthedocs.io/en/latest/examples/img_patch_convert.html)


## dataio  
- **rsimg_io**    
  readTiff, writeTiff  

## process  
- **img2patch**      
  img2patch (class): toPatch, higher_patch_crop, toImage
  crop2size (class): toSize, toScales
  crop2extent (class): img2extent
- **image normalization**   
  img_normalize.py   
- **image transform**     
  lay_stack   


## transform  
- **geo_imgxy**      
  get_utm_zone, coor2coor, geo2imagexy, imagexy2geo     
- **transform_time**      
  date2doy, doy2date, dt64_to_dyr, second_to_dyr    
- **raster_vec**    
  raster2vec, vec2mask    

## visual   
- **remote sensing image**    
  imgShow, imsShow   


## metrics  
- **metrics**      
  acc_matrix, acc_miou, oa_binary, miou_binary
- **metric_proc**      
  smooth

## To do   
1. check the metrics, and write the docmentation. 
2. reprojection for the remote sensing image
3. modify coor2coor by using shapely and pyproj package.





