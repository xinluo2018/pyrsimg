import pyproj

def coordxy_convert(proj_from, proj_to, x, y):
    """
    Transform coordinates from proj_from to proj_to
    using EPSG number
    input:
        proj1 and proj2 are EPSG number (e.g., 4326, 3031)
        x and y are x-coord and y-coord corresponding to proj1    
    return:
        x-coord and y-coord in proj2
    """
    proj1 = pyproj.Proj("EPSG:" + str(proj_from))
    proj2 = pyproj.Proj("EPSG:" + str(proj_to))
    return pyproj.transform(proj1, proj2, x, y)

