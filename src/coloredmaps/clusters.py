from sklearn.cluster import OPTICS, MeanShift
from scipy.signal import decimate
import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt
import cv2
import colorsys

def find_clusters(image_path, factor=1.0, n_jobs=8):
    """Finds clusters in a given map in the RGB space.
    """
    with rasterio.open(image_path) as src:
        data = src.read(out_shape=(src.count, int(src.height * factor), int(src.width * factor)), resampling=Resampling.nearest)
        data = data.transpose()
        shape = data.shape
        data = data.reshape(shape[0] * shape[1], 3)
        clustering = MeanShift(bandwidth=50, n_jobs=n_jobs).fit(data)
        results = {}
        labels = clustering.labels_
        labels = np.unique(labels)
        for label in labels:
            if label != -1:
                center = clustering.cluster_centers_[label]
                size = data[clustering.labels_ == label].shape[0]
                results[label] = {'center' : clustering.cluster_centers_[label], 'size' : size}
        return results

def visualize_clusters(results, filename):
    """Plots the results of the find_clusters method.
    """
    plt.pie([results[p]['size'] for p in results], colors=[results[p]['center'] / 255.0 for p in results])
    plt.savefig(filename)

    
