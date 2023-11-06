#!/usr/bin/env python
# coding: utf-8

# In[1]:


from skimage.transform import rescale
from skimage import img_as_ubyte, filters
from skimage import io
import matplotlib.pyplot as plt
import numpy as np
import os


# In[2]:


def load_image(filename, path):
    '''add the filename to the root directory'''
    path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(path):
        print('Found image {}'.format(path))
        return io.imread(path)
        #return Image.open(path) 
    
    # if you reach this line, you didn't find the image you're looking for
    print('Load failed: could not find image {}'.format(path))


# In[3]:


def plot_rgb_histo(image):
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    for slice_, name, color in ((r,'r', 'red'),(g,'g', 'green'),(b,'b', 'blue')):
        plt.hist(slice_.ravel(), bins=100, 
                 range=[0,1], 
                 label=name, color=color, histtype='step')
    plt.legend()


# In[4]:


def getRGBMedians(image):
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    r_median = np.median(r)
    g_median = np.median(g)
    b_median = np.median(b)
    return r_median, g_median, b_median


# In[5]:


def rescaleImage(image, targetSize = 0.25):
    image_rescaled = rescale(image, targetSize, channel_axis=2, preserve_range=True)
    return image_rescaled


# In[6]:


def normalizeImage(image):
    image_normalized = (image/ 255.)
    return image_normalized.clip(0, 1)


# In[7]:


def whitebalanceImage(image, setSigma = 1): 
    image_processed = image.copy()    
    #apply gaussian filter
    image_processed = filters.gaussian(image_processed, sigma=setSigma, preserve_range=True, channel_axis=2)       
    #recenter background
    image_processed = (image_processed*1.0 / image_processed.mean(axis=(0,1)))
    return image_processed.clip(0, 1)


# In[8]:


def plotBeforeAfterComparison(image_before, titleBefore, image_after, titleAfter):
    fig, ax = plt.subplots(1,2, figsize=(10,6))
    ax[0].imshow(image_before)
    ax[0].set_title(titleBefore)
    ax[1].imshow(image_after)
    ax[1].set_title(titleAfter)


# In[9]:


#example usage

# SCANS_ROOT = os.path.abspath("D:\old_scans_hackathon\Hackathon_Auswahl_Karten\Auswahl_Karten_Farbwerte")
# assert os.path.exists(SCANS_ROOT)

# fname_color_yellow = "PLS_9771_01.tif"#yellow image wit color
# image = load_image(fname_color_yellow, SCANS_ROOT)

# image = rescaleImage(image)
# image = normalizeImage(image)

# plotBeforeAfterComparison(image, "Original", whitebalanceImage(image), "WhiteBalanced")

