## author: ziyue dou, xin luo
## create: 2025.5.16, ziyue dou  
## modify: 2025.5.16, xin luo
## des: add scale bar and north_arrow to the map

import numpy as np
import cartopy.crs as ccrs
from matplotlib.patches import Polygon


def add_scale_bar(ax, length=None, crs = ccrs.Mercator(), 
                      loc=(0.5, 0.05), linewidth=3, 
                      color_bar='black', color_text='black'):
    """
    params:
        ax: the axes to draw the scalebar on.
        length: the length of the scalebar in km.
        crs: the coordinate system that the scalebar is in.
        location: tuple (x,y), center of the scalebar in axis coordinates. 
                    (e.g. 0.5 is the middle of the plot)
        linewidth: the thickness of the scalebar.
    """    
    # Get the extent of the plotted area in coordinates in metres
    try:
        x0, x1, y0, y1 = ax.get_extent(crs=crs)  # ax is a cartopy axes
    except:
        raise ValueError("axes must be a cartopy axes")
    
    # Turn the specified scalebar location into coordinates in metres
    sbx = x0 + (x1 - x0) * loc[0]
    sby = y0 + (y1 - y0) * loc[1]
    text_space = (y1 - y0) * 0.02
    # Calculate a scale bar length if none has been given
    # (Theres probably a more pythonic way of rounding the number but this works)
    if not length: 
        length = (x1 - x0) / 5000 # in km
        ndim = int(np.floor(np.log10(length))) #number of digits in number
        length = round(length, -ndim) #round to 1sf
        #Returns numbers starting with the list
        def scale_number(x):
            if str(x)[0] in ['1', '2', '5']: return int(x)        
            else: return scale_number(x - 10 ** ndim)
        length = scale_number(length) 

    #Generate the x coordinate for the ends of the scalebar
    bar_xs = [sbx - length * 500, sbx + length * 500]
    #Plot the scalebar
    ax.plot(bar_xs, [sby, sby], transform=crs, color=color_bar, linewidth=linewidth)
    #Plot the scalebar label
    ax.text(sbx, sby+text_space, str(length) + ' km', transform=crs,
            horizontalalignment='center', verticalalignment='bottom', color=color_text)

def add_north_arrow(ax, loc=(0.95, 0.85), size = [0.05, 0.05],
               color_narrow_left='white', color_narrow_right='black',
               edge_color_narrow='gray', edge_width_narrow=1, 
               N_label = True, font_N=12, color_N = 'black',               
               projection=None, 
               text_offset=0.02):
    """add north arrow to the map"""

    if projection is None:
        projection = ax.projection
    
    xmin, xmax, ymin, ymax = ax.get_extent()
    
    # center of the north_arrow
    x_center = xmin + (xmax - xmin) * loc[0]
    y_center = ymin + (ymax - ymin) * loc[1]
    
  
    width = (xmax - xmin) * size[0]
    height = (ymax - ymin) * size[1] * 2

    # define top of the north_arrow
    top = (x_center, y_center + height / 2)
    bottom_left = (x_center - width / 2, y_center - height / 2)
    bottom_right = (x_center + width / 2, y_center - height / 2)
    mid_bottom = (x_center, y_center - height / 2 * 0.2)

    # add north arrow
    ax.add_patch(Polygon([top, bottom_left, mid_bottom], 
                facecolor=color_narrow_left, edgecolor=edge_color_narrow, 
                linewidth=edge_width_narrow, transform=projection))  # narrow left
    ax.add_patch(Polygon([top, bottom_right, mid_bottom], 
                facecolor=color_narrow_right, edgecolor=edge_color_narrow,
                linewidth=edge_width_narrow, transform=projection))  # narrow left
    
    # add N label
    if N_label:
        ax.text(x_center, y_center + height / 2 + (ymax - ymin) * text_offset, 'N',
            fontsize=font_N, ha='center', va='bottom', color=color_N, transform=projection)




