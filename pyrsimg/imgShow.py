''' 
author: xin luo
create: 2020, modify: 2025.12.11
des: remote sensing image visualization
'''

import matplotlib.pyplot as plt
import numpy as np

def imgShow(img, 
            ax=None, 
            color_bands=(2,1,0),
            clip_percent=2, 
            per_band_clip=False,
            **kwargs):
    '''
    Description: show the single image.
    args:
        img: (row, col, band) or (row, col), DN range should be in [0,1]
        ax: axes for showing image.
        extent: list(left, right, bottom, top), the coordinates of the extent. 
        num_bands: a list/tuple, [red_band,green_band,blue_band]
        clip_percent: for linear strech, value within the range of 0-100. 
        per_band_clip: if True, the band values will be clipped by each band respectively. 
    return: None
    '''
    img = img.copy()
    img[np.isnan(img)]=0   ## remove NaN values 
    img = np.squeeze(img)

    if np.min(img) == np.max(img):
        if len(img.shape) == 2:
            if ax: im = ax.imshow(np.clip(img, 0, 1), vmin=0,vmax=1, **kwargs)
            else: im = plt.imshow(np.clip(img, 0, 1), vmin=0,vmax=1, **kwargs)
        else:
            if ax: im = ax.imshow(np.clip(img[:,:,0], 0, 1), vmin=0, vmax=1, **kwargs)
            else: im = plt.imshow(np.clip(img[:,:,0], 0, 1), vmin=0, vmax=1, **kwargs)
    else:
        if len(img.shape) == 2:
            img_color = np.expand_dims(img, axis=2)
        else:
            img_color = img[:,:,[color_bands[0], color_bands[1], color_bands[2]]]    
        img_color_clip = np.zeros_like(img_color)
        if per_band_clip == True:
            for i in range(img_color.shape[-1]):
                if clip_percent == 0:
                    img_color_hist = [0,1]
                else:
                    img_color_hist = np.percentile(img_color[:,:,i], [clip_percent, 100-clip_percent])
                img_color_clip[:,:,i] = (img_color[:,:,i]-img_color_hist[0])\
                                    /(img_color_hist[1]-img_color_hist[0]+0.0001)
        else:
            if clip_percent == 0:
                    img_color_hist = [0,1]
            else:
                img_color_hist = np.percentile(img_color, [clip_percent, 100-clip_percent])
            img_color_clip = (img_color-img_color_hist[0])\
                                     /(img_color_hist[1]-img_color_hist[0]+0.0001)

        if ax: im = ax.imshow(np.clip(img_color_clip, 0, 1), vmin=0, vmax=1, **kwargs)
        else: im = plt.imshow(np.clip(img_color_clip, 0, 1), vmin=0, vmax=1, **kwargs)
        return im
    

def imsShow(img_list, img_name_list=None, clip_list=None, figsize=(8,4),\
                            color_bands_list=None, axs=None, 
                            axis_ticks=True, row=None, col=None, extent_list=None):
    ''' 
    des: visualize multiple images.
        input: 
            img_list: containes all images
            img_names_list: image names corresponding to the images
            clip_list: percent clips (histogram) corresponding to the images
            color_bands_list: color bands combination corresponding to the images
            row, col: the row and col of the figure
            axis: True or False
            extent_list: the extent of each image, if not provided, the extent will be set to None
        return: None
    '''
    if clip_list is None:
        clip_list = [2 for i in range(len(img_list))]
    if color_bands_list is None:
        color_bands_list = [[2, 1, 0] for i in range(len(img_list))]
    if extent_list is None:
        extent_list = [None for i in range(len(img_list))]
    if row == None:
        row = 1
    if col == None:
        col = len(img_list)
    if axs is None:
        fig, axs = plt.subplots(row, col, figsize=figsize)
    for i in range(row):
        for j in range(col):
            ind = (i*col)+j
            if ind == len(img_list):
                break
            imgShow(img=img_list[ind], ax=axs[ind], 
                        color_bands=color_bands_list[ind], clip_percent=clip_list[ind], extent=extent_list[ind])     
            if img_name_list: axs[ind].set_title(img_name_list[ind])
            if not axis_ticks: axs[ind].set_axis_off()
    return axs