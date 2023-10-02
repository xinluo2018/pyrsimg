## author: xin luo
## create: 2023.3.30, modify:2023.9.28
## des: image normalization


import numpy as np

def img_normalize(img, max_bands, min_bands):    
    '''
    des: normalization with the given per-band max and min values
    input:
        img: input multiple spectral satellite image, shape: (row, col, bands)
        max_bands: int or list, maximum value of bands.
        min_bands: int or list, minimum value of bands.
    return:
        img_nor: the normalized statellite image.    
    '''
    img_nor = []
    if isinstance(max_bands, int):            
        max_bands = [max_bands for i in range(img.shape[-1])]
        min_bands = [min_bands for i in range(img.shape[-1])]        
    for i_band in range(img.shape[-1]):
        band_nor = (img[:,:,i_band]-min_bands[i_band])/(max_bands[i_band]-min_bands[i_band]+0.0001)
        img_nor.append(band_nor)
    img_nor = np.stack(img_nor, axis=-1)
    img_nor = np.clip(img_nor, 0., 1.) 
    return img_nor

