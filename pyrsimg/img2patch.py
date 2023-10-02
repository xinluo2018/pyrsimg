### author: xin luo, 
### create: 2021.3.19, modify: 2023.8.19
### des: 
###    1. Convert the remote sensing image to patches and in reverse.
###    2. Randomly crop multiple-scales patchs from the remote sening image.

import cv2
import random
import numpy as np
from osgeo import gdal

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
        rs_data=gdal.Open(path_img)
        dtype_id = rs_data.GetRasterBand(1).DataType
        dtype_name = gdal.GetDataTypeName(dtype_id)
        if 'int8' in dtype_name:
            datatype = gdal.GDT_Byte
        elif 'int16' in dtype_name:
            datatype = gdal.GDT_UInt16
        else:
            datatype = gdal.GDT_Float32
        geotrans = rs_data.GetGeoTransform()
        dx, dy = geotrans[1], geotrans[5]
        nbands = rs_data.RasterCount
        proj_wkt = rs_data.GetProjection()
        NDV = rs_data.GetRasterBand(1).GetNoDataValue()
        xmin, xmax, ymin, ymax = self.extent

        if self.size_target is None:
            npix_x = int(np.round((xmax - xmin) / float(dx)))  # new col
            npix_y = int(np.round((ymin - ymax) / float(dy)))  # new row
            dx = (xmax - xmin) / float(npix_x)
            dy = (ymin - ymax) / float(npix_y)
        else:
            npix_x = self.size_target[1]
            npix_y = self.size_target[0]
            dx = (xmax - xmin) / float(self.size_target[1])  # new resolution
            dy = (ymin - ymax) / float(self.size_target[0])

        if path_save is None:
            driver = gdal.GetDriverByName('MEM')
            dest = driver.Create('', npix_x, npix_y, nbands, datatype)
        else: 
            driver = gdal.GetDriverByName("GTiff")
            dest = driver.Create(path_save, npix_x, npix_y, nbands, datatype)
            
        dest.SetProjection(proj_wkt)
        newgeotrans = (xmin, dx, 0.0, ymax, 0.0, dy)
        dest.SetGeoTransform(newgeotrans)
        if NDV is not None:
            for i in range(nbands):
                dest.GetRasterBand(i+1).SetNoDataValue(NDV)
                dest.GetRasterBand(i+1).Fill(NDV)
        else:
            for i in range(nbands):
                dest.GetRasterBand(i+1).Fill(0)
        gdal.ReprojectImage(rs_data, dest, proj_wkt, proj_wkt, gdal.GRA_Bilinear)
        out_array = dest.ReadAsArray(0, 0,  npix_x,  npix_y)
        if NDV is not None:
            out_array = np.ma.masked_where(out_array == NDV, out_array).data
        if nbands > 1:
            return np.transpose(out_array, (1, 2, 0))  # 
        else:
            return out_array

