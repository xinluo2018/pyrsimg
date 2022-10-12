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
- get_img_extent, get_utm_zone.

## to do
