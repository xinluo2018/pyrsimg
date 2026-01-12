### author: xin luo, 
### create: 2021.3.19, modify: 2025.12.11
### des: 
###    1. Convert the remote sensing image to patches and in reverse.
###    2. Randomly crop multiple-scales patchs from the remote sening image.

import cv2
import random
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling


class img2patch():
    def __init__(self, img, patch_size, edge_overlay):
        '''  
        args:
            img: np.array()
            patch_size: size of the patch
            edge_overlay: an even number, single-side overlay of the neighboring images.
        '''

        if edge_overlay % 2 != 0:
            raise ValueError('Argument edge_overlay should be an even number')
        self.edge_overlay = edge_overlay        
        self.patch_size = patch_size
        self.img = img[:,:,np.newaxis] if len(img.shape) == 2 else img
        self.img_row = img.shape[0]
        self.img_col = img.shape[1]
        self.img_patch_row = np.nan    # valid when call toPatch
        self.img_patch_col = np.nan
        self.start_list = []           #  

    def toPatch(self):
        '''
        des: 
            convert img to patches. 
        return: 
            patch_list, contains all generated patches.
            start_list, contains all start positions(row, col) of the generated patches. 
        '''
        patch_list = []
        patch_step = self.patch_size - self.edge_overlay
        img_expand = np.pad(self.img, ((self.edge_overlay, self.patch_size),
                                          (self.edge_overlay, self.patch_size), (0,0)), 'constant')
        self.img_patch_row = (img_expand.shape[0]-self.edge_overlay)//patch_step
        self.img_patch_col = (img_expand.shape[1]-self.edge_overlay)//patch_step
        for i in range(self.img_patch_row):
            for j in range(self.img_patch_col):
                patch_list.append(img_expand[i*patch_step:i*patch_step+self.patch_size,
                                                        j*patch_step:j*patch_step+self.patch_size, :])
                self.start_list.append([i*patch_step-self.edge_overlay, j*patch_step-self.edge_overlay])
        return patch_list

    def higher_patch_crop(self, higher_patch_size):
        '''
        des: 
            crop the higher-scale patch (centered by the given low-scale patch)
                (!!Note: the toPatch() usually should be firstly called when use higher_patch_crop())
        input:
            higher_patch_size, int, the lager patch size compared the low-scale patch size. 
        return: 
            higher_patch_list, list, contains higher-scale patches corresponding to the lower-scale patches.
        '''
        higher_patch_list = []
        radius_bias = higher_patch_size//2-self.patch_size//2
        img_expand = np.pad(self.img, ((self.edge_overlay, self.patch_size), \
                                            (self.edge_overlay, self.patch_size), (0,0)), 'constant')
        img_expand_higher = np.pad(img_expand, ((radius_bias, radius_bias), (radius_bias, radius_bias), (0,0)), 'constant')
        start_list_new = list(np.array(self.start_list)+self.edge_overlay+radius_bias)
        for start_i in start_list_new:
            higher_row_start, higher_col_start = start_i[0]-radius_bias, start_i[1]-radius_bias
            higher_patch = img_expand_higher[higher_row_start:higher_row_start+higher_patch_size, \
                                                            higher_col_start:higher_col_start+higher_patch_size,:]
            higher_patch_list.append(higher_patch)
        return higher_patch_list

    def toImage(self, patch_list):
        '''
        des: 
            merge patches into one image. 
            (!!note: the toPatch() usually should be firstly called when use toImage())
        args:
            patch_list: list of the all patches.
        return: 
            img_array: the merged image by patches 
        '''
        patch_list = [patch[self.edge_overlay//2:-self.edge_overlay//2, self.edge_overlay//2:-self.edge_overlay//2,:]
                                                        for patch in patch_list]
        patch_list = [np.hstack((patch_list[i*self.img_patch_col:i*self.img_patch_col+self.img_patch_col]))
                                                        for i in range(self.img_patch_row)]
        img_array = np.vstack(patch_list)
        img_array = img_array[self.edge_overlay//2:self.img_row+self.edge_overlay//2, \
            self.edge_overlay//2:self.img_col+self.edge_overlay//2,:]
        return img_array

class crop2size():
    '''  
    des: crop image with specific size.
    args:
      img: np.array()
      channel_first: True or False.
    '''
    def __init__(self, img, channel_first=False):
      self.channel_first = channel_first
      if self.channel_first: 
        self.img = np.transpose(img, (1,2,0)) 
      else:
        self.img = img

    def toSize(self, size=(256, 256)):
      ''' 
        des: randomly crop corresponding to specific size
        input:
          size: tuble/list, (height, width)
        return: patch, the cropped patch from the image.
      '''
      start_h = random.randint(0, self.img.shape[0]-size[0])
      start_w = random.randint(0, self.img.shape[1]-size[1])
      patch = self.img[start_h:start_h+size[0], start_w:start_w+size[1],:]
      if self.channel_first:
        patch = np.transpose(patch, (2,0,1))
      return patch

    def toScales(self, scales=(2048, 512, 256)):
        ''' 
        des: randomly crop multiple-scale patches (from high to low) from remote sensing image.
        input:
            scales: tuple or list (high scale -> low scale)
        return: patches_group_down: list of multiscale patches.
        '''
        height, width = self.img.shape[:-1]
        if height<scales[0] or width<scales[0]:
          raise Exception('The input scale overpass the size of image!')
        patches_group = []
        patch_high = self.toSize(size=(scales[0], scales[0]))
        patches_group.append(patch_high)
        for scale in scales[1:]:
            start_offset = (scales[0]-scale)//2
            patch_lower = patch_high[start_offset:start_offset+scale, start_offset:start_offset+scale, :]
            patches_group.append(patch_lower)
        patches_group_down = []
        for patch in patches_group[:-1]:
            patch_down=[cv2.resize(patch[:,:,num], dsize=(scales[-1], scales[-1]), \
                                interpolation=cv2.INTER_LINEAR) for num in range(patch.shape[-1])]
            patches_group_down.append(np.stack(patch_down, axis=-1))
        patches_group_down.append(patch_lower)
        if self.channel_first:
          patches_group_down = [np.transpose(patch_down, (2,0,1)) for patch_down in patches_group_down]
        return patches_group_down

class crop2extent():
    '''   
    des: crop image with specific geographical extent.
    args:
        extent: list (left, right, down, up), extent for image cropping. \
                              the extent should agree with the projection of input image.
    '''
    def __init__(self, extent, size_target=None):
        self.extent = extent
        self.size_target = size_target
    def img2extent(self, path_img, path_save=None):
        '''  
        crop image to given extent/size.
        arg:
            path_img: string, the image path to be croped.
            size_target: size to which image should be croped 
                  list/tuple, (row, col)
            path_save: string, the path for output saving.    
        return: 
            img_croped: the croped image, np.array()
        '''
        with rasterio.open(path_img) as src:
            xmin, xmax, ymin, ymax = self.extent
            
            # Determine Output Dimensions and Resolution
            if self.size_target is None:
                npix_x = int(np.round((xmax - xmin) / src.res[0]))
                npix_y = int(np.round((ymax - ymin) / src.res[1]))
            else:
                npix_y, npix_x = self.size_target 

            # Calculate new pixel resolution
            pixel_width = (xmax - xmin) / npix_x
            pixel_height = (ymax - ymin) / npix_y

            # Construct destination Affine Transform
            dst_transform = from_origin(xmin, ymax, pixel_width, pixel_height)
            
            # Prepare destination array
            out_shape = (src.count, npix_y, npix_x)
            dest_array = np.zeros(out_shape, dtype=src.dtypes[0])
            
            # Reproject (Warp)
            for i in range(src.count):
                reproject(
                    source=rasterio.band(src, i + 1),
                    destination=dest_array[i],
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=src.crs,
                    resampling=Resampling.bilinear,
                    src_nodata=src.nodata,
                    dst_nodata=src.nodata
                )

            # Save to disk if path is provided
            if path_save is not None:
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": npix_y,
                    "width": npix_x,
                    "transform": dst_transform
                })
                with rasterio.open(path_save, "w", **out_meta) as dest:
                    dest.write(dest_array)
            
            # Handle Return Shape
            if src.count > 1:
                return np.transpose(dest_array, (1, 2, 0))
            else:
                return dest_array[0]
