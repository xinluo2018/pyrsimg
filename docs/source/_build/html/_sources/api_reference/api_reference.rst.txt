API Reference
===============

rsimg_io
---------------
* readTiff (class): 
* writeTiff: write out the .tiff formated remote sensing image. 

.. function:: readTiff(path_in)

    Description: Write out the .tiff formated remote sensing image          

    :param: path_in    
    :return: img(np.array), extent(tuple), projection(str), dimentions(tuple)

.. function:: writeTiff(im_data, im_geotrans, im_geosrs, path_out)

    Write out the .tiff formated remote sensing image          

    :param: im_data, im_geotrans, im_geosrs, path_out    
    :retrun: None



geo_imgxy
-----------------

.. function:: get_utm_zone(lon)

    Description: Get utm zone from the given wgs84 coordinates.

    :param: lon: the given longitute, should be in the range of [-180, 180]   
    :retrun: utm_zone_number

.. function:: coor2coor(srs_from, srs_to, x, y)

    Description: Transform coordinates from srs_from to srs_to

    :param: srs_from:  EPSG number (e.g., 4326, 3031)
            
            srs_to: EPSG number (e.g., 4326, 3031)
            
            x: x-coord corresponding to srs_from

            y: corresponding to srs_to

    :retrun: utm_zone_number



.. function:: geo2imagexy(x, y, gdal_trans, integer=True)

    Description: from georeferenced location (i.e., lon, lat) to image location(col,row).

    Note: the coordinate system should be same between x/y and gdal_trans.

    :param: gdal_proj: obtained by gdal.Open() and .GetGeoTransform(), or by geotif_io.readTiff()['geotrans']

            x: project or georeferenced x, i.e.,lon 

            y: project or georeferenced y, i.e., lat

    :retrun: utm_zone_number



.. function:: imagexy2geo(row, col, gdal_trans)

    Description: from image location(col,row) to georeferenced location (i.e., lon, lat).

    :param:  img_gdal: GDAL data (read by gdal.Open()

             row: row of the input image (dataset)
             
             col: col of the input image (dataset)

    :retrun: x: geographical coordinates at x-axis (left up of pixel)
              
             y: geographical coordinates at y-axis (left up of pixel)


img_extent
------------------

.. function:: get_img_extent(path_img)

    Description: obtain the image extent.

    :param:  path_img: path of the remote sensing image.
    :retrun: extent: image extent. list -> [left, right, bottom, up]
             espg_code: ESPG code
             
.. function:: imgs_in_extent(path_img)

    Description: Selected imgs that in the given extent.

    :param:  paths_img: list, images paths

             extent: image extent. list -> [left, right, bottom, up]
    :retrun: paths_imgs_extent, list.


.. function:: img2extent(path_img, extent, size_target=None, path_save=None)

    Description: Crop image to given extent/size.

    :param: path_img: string, the image path to be croped.

            extent: extent to which image should be croped; list/tuple,(left, right, down, up). 

            size_target: size to which image should be croped list/tuple, (row, col)
    :retrun: img_croped: the croped image, np.array()


.. function:: imgs2extent(paths_img, extent, path_save=None)

    Description: crop multiple images to the given extent.

    :param: dir_data: string, directory of the tiled data

            extent: list, [left, right, bottom, up], can be obtained by readTiff() function.

            path_save: string, the file path to be saved. 
    :retrun: img_croped: the croped image.



img_normalize
---------------------

.. class:: img_normalize(max_bands, min_bands)(image)

    Description: image normalization.

    :param: max_bands: list, max value of each the band of image.
        
            min_bands: list, min values of each the band of image.

            image: np.array.

    :retrun: image_nor: the normalized image.


img2patch (class)  
---------------------------

.. class:: img2patch(img, patch_size, edge_overlay)

    Description: Conversion between the remote sensing image and patches

    :param: img: np.array()

            patch_size: size of the patch

            edge_overlay: an even number, single-side overlay of the neighboring images.
    :method: .toPatch(): 

              Description: convert img to patches.
              
              :param: None

              :retrun: patch_list: contains all generated patches.
                        
                        start_list: contains all start positions(row, col) of the generated patches. 
    :method: .higher_patch_crop(higher_patch_size)

              Description: crop the higher-scale patch

              :param: higher_patch_size: int, the lager patch size compared the low-scale patch size.
              :retrun: higher_patch_list: list, contains higher-scale patches corresponding to the lower-scale patches.

    :method: .toImage(patch_list)
              
              Description: merge patches into one image.
              
              :param: patch_list: list of the all patches.
              
              :retrun: img_array: the merged image by patches 



.. function:: crop(image, size=(256, 256), channel_first=False)

    Description: randomly crop corresponding to specific size.
    
    :param: img: np.array(), (height, width, channels), the remote senisng image.
                       
            size: tuble/list, (height, width)

    :retrun: patch, the cropped patch from the image.



.. function:: crop_scales(image, scales=(2048, 512, 256), channel_first=False)

    Description: Randomly crop multiple-scale pari-wise patches and truths (from high to low) from remote sensing image and truth image.

    :param: img: np.array(), (height, width, channels), the remote senisng image.
                        
            scales: tuple or list (high scale -> low scale)

    :retrun: patches_group_down: list of multiscale patches.


imgShow
---------------
.. function:: imgShow(img, ax=None, extent=None, color_bands=(2,1,0), clip_percent=2, per_band_clip=False, focus_per=None, focus_pix=None)

    Description: show the single image.

    :param: img: (row, col, band) or (row, col), DN range should be in [0,1]

            extent: list, the coordinates of the extent. 
    
            num_bands: a list/tuple, [red_band,green_band,blue_band]
    
            clip_percent: for linear strech, value within the range of 0-100. 
    
            per_band_clip: if True, the band values will be clipped by each band respectively. 
    
            focus_per: list, [up_start_percent,down_end_percent,left_start_percent, right_end_percent]; 0 < value < 1
    
            focus_pix: list, [up_start_pixel,down_end_pixel,left_start_pixel, right_end_pixel]; 0 < value < (width or height) of the image

    :retrun: None


.. function:: imsShow(img_list, img_name_list, clip_list=None, color_bands_list=None, axis=True, row=None, col=None)

    Description: show the multiple images.

    :param: img_list: containes all images
            
            img_names_list: image names corresponding to the images
            
            clip_list: percent clips (histogram) corresponding to the images
            
            color_bands_list: color bands combination corresponding to the images
            
            row, col: the row and col of the figure
            
            axis: True or False

    :retrun: None


lay_stack 
---------------------

.. function:: lay_stack(path_imgs, path_out, union=True, res=None)

    Description: layer stacking of the multiple bands of image.

    :param: path_imgs: list, contains the paths of bands/imgs to be stacked
            
            path_out: str, the output path of the layer stacked image
            
            union: bool, if true, the output extent is the extents union of input images. Otherwise, the output extent is the extents intersection of input images.
        
            res: resolution of the layer stacked image.

    :retrun: imgs_stacked: np.array(), the stacked image.



metric_proc 
-------------------
.. function:: smooth(y, window=31, num_sam = None)

    Description: smooth the sequential data.

    :param: y: the sequential data.
            
            window: the smooth window used for averating y.
            
            num_sam: the number of sampled data.  
    :retrun: x: the smoothed sequential data of x-axis. 
             
             y: the smoothed sequential data of y-axis. 

metric
---------------
.. function:: acc_matrix(cla_map, truth_map=None, sam_pixel=None, id_label=None)

    Description: calculate the accuracy matrix.

    :param: cla_map: classification result of the full image.
            
            truth_map: truth image (either truth_map or sam_pixel should be given).
            
            sam_pixel: np.array, (num_samples,3), col 1,2,3 are the row,col and label.            
            
            id_label: 0/1/2/..., Calculating producer's or user's accuracy for target class.

    :retrun: acc_oa: overall accuracy 

             confus_mat: confusion matrix

.. function:: acc_miou(cla_map, truth_map, labels=None)

    Description: calculate the miou metric.

    :param: cla_map: classification result of the full image
            
            truth_map: truth image (either truth_map or sam_pixel should be given)
            
            labels: a list, the class id for calculating. e.g., [0,1,2]

    :retrun: miou: MIoU metric

.. function:: oa_binary(pred, truth)

    Description: calculate overall accuracy (2-class classification) for each batch.

    :param: pred: 4D tensor 
            
            truth: 4D tensor
    :retrun: oa: overall accuracy

.. function:: miou_binary(pred, truth)

    Description: calculate miou (2-class classification) for each batch.

    :param: pred: 4D tensor 
            
            truth: 4D tensor
    :retrun: miou: miou metric


raster_vec 
---------------------
.. function:: raster2vec(raster_path, output_path, dn_values)

    Description: Read input band with Rasterio.

    :param: raster_path: raster path
            
            output_path: ouput vector path
            
            dn_values: list, consist of the raster value to be vectorization

    :retrun: miou: miou metric

.. function:: vec2mask(path_vec, path_raster, path_save=None)

    Description: generate/save mask file using the vector file(e.g.,.shp,.gpkg).

    :param: path_vec: str, path of the vector data.
            
            path_raster: str, path of the raster data.
            
            path_save: str, path to save.
    :retrun: mask: np.array().


transform_time 
-------------------

.. function:: date2doy(year, month, day, hour=0, minute=0)

    Description: convert year-month-day-hour-minute to doy (day-of-year)
    
    :param: year
            month: 0~12 
            day: 0~31
            hour 
            minute

    :retrun: doy: day of the year.

.. function:: doy2date(year, doy)

    Description: Convert doy(day-of-year) to year-month-day-hour-minute formate the function returns the month and the day of the month. 

    :param: year
            
            doy

    :retrun: month
              
             day: the day of the month

.. function:: dt64_to_dyr(dt64)

    Description: Convert datetime64 to decimal year format. e.g., '2020-05-23T03:25:22.959373696' -> 2020.3907103825136.   

    :param: dt64: np.datetime64 format time

    :retrun: dt_float: float, the decimal date.

.. function:: second_to_dyr(time_second, time_start='2000-01-01 00:00:00.0')

    Description: convert time (second format) to decimal year. This function suitable for the jason data, sentinel-3 data, and the cryosat2 data for time conversion.

    :param: time_second: seconds from the time start.

    :retrun: time_second_dyr: decimal date.



