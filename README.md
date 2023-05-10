# rsipy  
Toolkit for easy processing of remote sensing image  

## dataio  
- **geotif_io**    
  readTiff, writeTiff  

## preprocess  
- **img_patch**      
  imgPatch (class): toPatch, higher_patch_crop, toImage    
- **transform_xy**     
  coor2coor, geo2imagexy, imagexy2geo, get utm zone number from the given longitute.   
- **image transform**    
  lay_stack  
- **raster_vec**    
  raster2vec, vec2mask   
- **date_format**    
  date_convert.py    
- **image normalization**   
  img_normalize.py

## visual   
- **data**    
  imgShow, imsShow   
- **result**   
  mertric_plot(in SWatNet/utils/metrics_plot.py)    

## metric (on going)  
- batch-based     
  oa, miou,   
- image-based     
  oa, producer's, user' accuray, and confusion matrix.   

## tool   
- get_img_extent, img_in_extent, crop2extent, get_utm_zone.   


## to do   
1. compare the imgPatch.py and the crop_scales.py in Tibet-Water-2020.
2. remove the main function in the python script.
3. merge the get_img_extent.py and img_in_extent.py into one.



