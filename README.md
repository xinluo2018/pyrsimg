# **pyrsimg**  
Toolkit for easy processing of remote sensing image, particularly the processing related to the applicaiton of deep learning method is considered.   

## **Installation**
pip install pyrsimg



## dataio  
- **rsimg_io**    
  readTiff, writeTiff  

## process  
- **img2patch**      
  img2patch (class): toPatch, higher_patch_crop, toImage, crop, crop_scales   
- **image_extent**    
  get_img_extent, imgs_in_extent, img2extent, imgs2extent.   
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
- **metric_plot**   

## metrics  
- **metrics**      
  acc_matrix, acc_miou, oa_binary, miou_binary
- **metric_proc**      
  smooth

## To do   
Modify the script raster_vec.py, remove the rasterio, and use gdal instead, ref: https://hydro-informatics.com/jupyter/geo-convert.html  





