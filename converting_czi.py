
import os
import czifile
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from tifffile import imwrite, memmap, TiffFile

cwd = os.getcwd()
os.chdir('D:/Disco_Nitro5/Geology/Zeiss microscopy platforms/Online db and conversion/Zeiss slides')

filepath_sample = 'chlr_schist_stonehav.czi'
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

# %% Metada

for neighbor in root.iter('Overlap'):
    overlapping_str = neighbor.text
   
for neighbor in root.iter('Width'):
    tile_width = neighbor.text
    
for neighbor in root.iter('Height'):
    tile_height = neighbor.text

channel_name = []
for neighbor in root.iter('PolarizerAngle'):
    channel_name_temp = neighbor.text    
    channel_name.append(channel_name_temp)
    
# More options:    
#'Magnification', 'Contrast Name', 'OriginalCompressionMethod', 
#'SizeX', 'SizeY', 'SizeS', 'SizeM'(size mosaic position), 'AcquisitionDuration'
#'Channel Name', 'PolarizerAngle', 'PolarizerAngle', 
#'Objective Name', 'Distance Id' (search inside), 'Detector Id'

# %% finding ROI

img1 = image[0, 0, :, :, :] #(TZXYC)
rangeX = slice(10000, 25000)
rangeY = slice(20000, 30000)
img2 = img1[rangeY, rangeX, :]
shapeROI = img2.shape
plt.imshow(img2) 
# %% extracting and saving as OME tiff (10min for 10Kx25K)

image1 = image[:, :, rangeX, rangeY, :]
image1_swapped = np.asarray(image1).transpose(0, 1, 4, 3, 2)

# create an empty OME-TIFF file
filename = filepath_sample2 + '1ROI' + '.ome.tif'
shapeOME = (1, 7, 3, shapeROI[0], shapeROI[1])
imwrite(filename, shape=shapeOME, dtype=dtype, metadata={'axes': 'TZCYX'})

# memory map numpy array to data in OME-TIFF file
tzcyx_stack = memmap(filename)

# write data to memory-mapped array
for z in range(shapeOME[1]):
        tzcyx_stack[z] = image1_swapped[0, z, :, :, :]
        tzcyx_stack.flush()
        
# %% saving as tiff for ImageJ
img_sample = czifile.imread(filepath_sample)
#imwrite(filepath_sample+"_for_imageJ.tiff", img_sample, imagej=True, resolution=(resolution_x, resolution_x), metadata={'spacing': 1.0, 'unit': 'micron'})