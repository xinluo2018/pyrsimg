## author: xin luo 
## creat: 2022.3.16; modify: xxxx
## des: layer stacking for remote sensing image

from osgeo import gdal

def lay_stack(path_imgs, path_out):
  '''
  input:
    path_imgs: list, contains the paths of bands/imgs to be stacked
    path_out: str, the output path of the layer stacked image
  note: the first image in the path_imgs is the reference image.
  '''

  ## base image
  base_img = gdal.Open(path_imgs[0], gdal.GA_ReadOnly)
  base_Proj = base_img.GetProjection()
  base_Trans = base_img.GetGeoTransform()
  base_x = base_img.RasterXSize 
  base_y = base_img.RasterYSize
  base_n = base_img.RasterCount

  ## layer stacking 
  for path_stack in path_imgs[1:]:
      
      ## image to be layer stacked
      stack_img = gdal.Open(path_stack)
      stack_Proj = stack_img.GetProjection()
      stack_n = stack_img.RasterCount

      ## align image to the base image
      driver= gdal.GetDriverByName('GTiff')
      stack_align = driver.Create(path_out, base_x, base_y, stack_n, gdal.GDT_Float32)
      stack_align.SetGeoTransform(base_Trans)
      stack_align.SetProjection(base_Proj)
      gdal.ReprojectImage(stack_img, stack_align, stack_Proj, base_Proj, gdal.GRA_Bilinear)

      ## layer stacking
      n_bands = base_n+stack_n
      img_stack = driver.Create(path_out, base_x, base_y, n_bands, gdal.GDT_Float32)

      if(img_stack!= None):
          img_stack.SetGeoTransform(base_Trans)   # 
          img_stack.SetProjection(base_Proj)      # 

      for i in range(base_n):
          img_stack.GetRasterBand(i+1).WriteArray(base_img.GetRasterBand(i+1).ReadAsArray())
      for i in range(stack_n):
          img_stack.GetRasterBand(base_n+i+1).WriteArray(stack_align.GetRasterBand(i+1).ReadAsArray())
      ## update base image
      base_n = n_bands
      base_img = img_stack

  del img_stack, base_img, stack_img 
