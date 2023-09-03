## author: xin luo
## create: 2021.10.26; modify: 2023.8.20
## des: function for processing the obtained metrics, e.g., loss, oa.

import numpy as np
from scipy.interpolate import make_interp_spline

def smooth(y, window=31, num_sam = None):
    '''
    input:
      y: the sequential data.
      window: the smooth window used for averating y.
      num_sam: the number of sampled data.       
    return:
      x, y: the smoothed sequential data corresponding x-axis and y-axis, respectively. 
    '''
    _head = np.full(shape=int((window-1)/2), fill_value=y[0])
    _tail = np.full(shape=int((window-1)/2), fill_value=y[-1])
    s = np.r_[_head, y, _tail]
    w = np.ones(window,'d')
    y = np.convolve(w/w.sum(), s, mode='valid')
    x = np.arange(y.shape[0])
    if num_sam is not None:
        i_iter = np.arange(y.shape[0])
        x_y_spline = make_interp_spline(i_iter, y)
        x = np.linspace(i_iter.min(), i_iter.max(), num_sam)
        y = x_y_spline(x)
    return x, y





