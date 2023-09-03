## author: xin luo
## create: 2023.3.30
## des: image normalization


import numpy as np

class img_normalize:
    '''normalization with the given per-band max and min values'''
    def __init__(self, max_bands, min_bands):
        '''max, min: list, values corresponding to each band'''
        self.max, self.min = max_bands, min_bands      
    def __call__(self, image):
        image_nor = []
        if isinstance(self.max,int):            
            self.max = [self.max for i in range(image.shape[-1])]
            self.min = [self.min for i in range(image.shape[-1])]        
        for band in range(image.shape[-1]):
            band_nor = (image[:,:,band]-self.min[band])/(self.max[band]-self.min[band]+0.0001)
            image_nor.append(band_nor)
        image_nor = np.array(image_nor)
        image_nor = np.clip(image_nor, 0., 1.) 
        return image_nor