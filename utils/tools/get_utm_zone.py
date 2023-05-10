### ----- 
# author: luo xin, 
# creat: 2022.10.9
# des: image location transform between different coordinate system. 
# -----

import numpy as np

def get_utm_zone(lon):
  '''
  des: get utm zone from the given wgs84 coordinates.
  lon: the given longitute, should be in the range of [-180, 180].
  return: utm_zone number.
  '''
  utm_zone = np.floor(lon/6)+31
  return int(utm_zone)
