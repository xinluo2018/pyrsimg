## author: xin luo
## creat: 2023.9.1
## des: setting for the python package


from setuptools import setup
from setuptools import find_packages


VERSION = '1.1.3'

setup(
    name='pyrsimg',       # package name
    version=VERSION,      # package version
    description='Python toolkit for easy processing of satellite image',  # package description
    author='The pyrsimg developers',
    author_email='xinluo_xin@163.com',
    maintainer='Xin Luo',
    maintainer_email='xinluo_xin@163.com',    
    license='GPL License',  
    packages=find_packages(),  
    install_requires=['scikit-learn', 
                      'numpy', 
                      'opencv-python', 
                      'matplotlib', 
                      'scipy', 
                      'astropy'],           ## the user should install gdal by theirself.
    python_requires='>=3.8',                ## Minimum version requirement of the package
    )

