### author: xin luo, 
### create: 2021.3.19, modify: 2023.8.19
### des: 
###    1. Convert the remote sensing image to patches and in reverse.
###    2. Randomly crop multiple-scales patchs from the remote sening image.

import numpy as np
import cv2
import random

class img2patch():
    def __init__(self, img, patch_size, edge_overlay):
        ''' edge_overlay = left overlay or, right overlay
        edge_overlay should be an even number. '''
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
        '''
        patch_list = [patch[self.edge_overlay//2:-self.edge_overlay//2, self.edge_overlay//2:-self.edge_overlay//2,:]
                                                        for patch in patch_list]
        patch_list = [np.hstack((patch_list[i*self.img_patch_col:i*self.img_patch_col+self.img_patch_col]))
                                                        for i in range(self.img_patch_row)]
        img_array = np.vstack(patch_list)
        img_array = img_array[self.edge_overlay//2:self.img_row+self.edge_overlay//2, \
            self.edge_overlay//2:self.img_col+self.edge_overlay//2,:]
        return img_array


def crop(image, size=(256, 256), channel_first=False):
    ''' 
      input:
        img: np.array(), (height, width, channels), the remote senisng image.
        turth: np.array(), the groud truth of the image.
        size: tuble/list, (height, width)
      des: randomly crop corresponding to specific size
    '''
    if channel_first:
      image = np.transpose(image, (1,2,0))    
    start_h = random.randint(0, image.shape[0]-size[0])
    start_w = random.randint(0, image.shape[1]-size[1])
    patch = image[start_h:start_h+size[0], start_w:start_w+size[1],:]
    if channel_first:
      patch = np.transpose(patch, (2,0,1))
    return patch


def crop_scales(image, scales=(2048, 512, 256), channel_first=False):
    ''' 
      input:
        img: np.array(), (height, width, channels), the remote senisng image.
        turth: np.array(), the groud truth of the image.
        scales: tuple or list (high scale -> low scale)
      des: randomly crop multiple-scale pari-wise patches and truths (from high to low) 
            from remote sensing image and truth image.
    '''
    if channel_first:
      image = np.transpose(image, (1,2,0))
    height, width = image.shape[:-1]
    if height<scales[0] or width<scales[0]:
      raise Exception('The input scale overpass the size of image!')
    patches_group = []
    patch_high = crop(image, size=(scales[0], scales[0]), channel_first=channel_first)
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
    if channel_first:
       patches_group_down = [np.transpose(patch_down, (2,0,1)) for patch_down in patches_group_down]
    return patches_group_down

