from sklearn.cluster import OPTICS
import rasterio
import numpy as np

def find_clusters(image_path):
    with rasterio.open(image_path) as src:
        data = src.read()
        data = data.transpose()
        shape = data.shape
        data = data.reshape(shape[0] * shape[1], 3)
        clustering = OPTICS(min_samples=1000, n_jobs=8).fit(data)
        import pdb; pdb.set_trace()

