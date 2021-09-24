
import os

vipshome = 'C:\\LIBVIPS\\vips-dev-8.11\\bin'
os.environ['PATH'] = vipshome + ';' + os.environ['PATH']

import czifile
import xml.etree.ElementTree as ET
import numpy as np
#import matplotlib.pyplot as plt
#import sys
import pyvips
#from tifffile import imwrite, memmap, TiffFile

cwd = os.getcwd()
os.chdir('C:/Users/Acer/Desktop/New folder')

filepath_sample = 'image.czi'
image = czifile.imread(filepath_sample) #5 min for 35Kx36K pixels
shape = image.shape
dtype = image.dtype

#save metadata
with czifile.CziFile(filepath_sample) as czi:
    xml_metadata = czi.metadata()

root = ET.fromstring(xml_metadata)
xmlOutput = ET.ElementTree(root) #initialize with contents of XML file
filepath_sample2 = filepath_sample.replace('.czi', '')
xmlOutput.write(filepath_sample2 + '_' + 'metadata.xml')

# %% extracting and saving 

#from TZXYC czi 
image1_swapped = np.asarray(image).transpose(0, 1, 2, 3, 4)
#to TZCYX ome.tiff (1, 7, 3, shape[2], shape[3]) 
image_time, image_series, image_height, image_width, image_bands = image1_swapped.shape

image_z1 = image1_swapped[0, 0, :, :, :]
image_z2 = image1_swapped[0, 1, :, :, :]
image_z3 = image1_swapped[0, 2, :, :, :]
image_z4 = image1_swapped[0, 3, :, :, :]
image_z5 = image1_swapped[0, 4, :, :, :]
image_z6 = image1_swapped[0, 5, :, :, :]
image_z7 = image1_swapped[0, 6, :, :, :]

image1_linear = image_z1.reshape(image_width*image_height*image_bands)
image2_linear = image_z2.reshape(image_width*image_height*image_bands)
image3_linear = image_z3.reshape(image_width*image_height*image_bands)
image4_linear = image_z4.reshape(image_width*image_height*image_bands)
image5_linear = image_z5.reshape(image_width*image_height*image_bands)
image6_linear = image_z6.reshape(image_width*image_height*image_bands)
image7_linear = image_z7.reshape(image_width*image_height*image_bands)

im1 = pyvips.Image.new_from_memory(image1_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im2 = pyvips.Image.new_from_memory(image2_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im3 = pyvips.Image.new_from_memory(image3_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im4 = pyvips.Image.new_from_memory(image4_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im5 = pyvips.Image.new_from_memory(image5_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im6 = pyvips.Image.new_from_memory(image6_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
im7 = pyvips.Image.new_from_memory(image7_linear, \
                                  image_width, image_height, bands=image_bands, format="uchar")
    
r1, g1, b1 = im1.bandsplit()
r2, g2, b2 = im2.bandsplit()
r3, g3, b3 = im3.bandsplit()
r4, g4, b4 = im4.bandsplit()
r5, g5, b5 = im5.bandsplit()
r6, g6, b6 = im6.bandsplit()
r7, g7, b7 = im7.bandsplit()
    
# split to separate image planes and stack vertically ready for OME 
im = pyvips.Image.arrayjoin([r1, g1, b1, r2, g2, b2, r3, g3, b3, r4, g4, b4, \
                             r5, g5, b5, r6, g6, b6, r7, g7, b7], across=1)

# set minimal OME metadata    
# before we can modify an image (set metadata in this case), we must take a 
# private copy
im = im.copy()
im.set_type(pyvips.GValue.gint_type, "page-height", image_height)
im.set_type(pyvips.GValue.gstr_type, "image-description",
f"""<?xml version="1.0" encoding="UTF-8"?>
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
    <Image ID="Image:0">
        <!-- Minimum required fields about image dimensions -->
        <Pixels DimensionOrder="TZCYX"
                ID="Pixels:0"
                SizeT="1"
                SizeZ="1"
                SizeC="{image_bands}"
                SizeY="{image_height}"
                SizeX="{image_width}"               
                Type="uint8">
        </Pixels>
    </Image>
</OME>""")

filename = filepath_sample2 + '21ROI' + '.ome.tif' #.tiff, ome.tif
im.tiffsave(filename, compression="jpeg", tile=True,
            tile_width=512, tile_height=512,
            pyramid=True, subifd=True) #compression="jp2k" when subid=false