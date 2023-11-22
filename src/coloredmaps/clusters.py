from sklearn.cluster import OPTICS, MeanShift
from scipy.signal import decimate
import rasterio
from rasterio.enums import Resampling
import numpy as np
import matplotlib.pyplot as plt
import cv2
import colorsys
import click
import json
import pathlib
import os

def find_clusters(image_path, output_dir, factor=1.0, n_jobs=8):
    """Finds clusters in a given map in the RGB space.
    """
    filename = pathlib.Path(image_path).stem
    with rasterio.open(image_path) as src:
        profile = src.profile
        orig_data = src.read(out_shape=(src.count, int(src.height * factor), int(src.width * factor)), resampling=Resampling.nearest)
        data = orig_data.transpose()
        shape = data.shape
        data = data.reshape(shape[0] * shape[1], 3)
        clustering = MeanShift(bandwidth=50, n_jobs=n_jobs).fit(data)
        results = {}
        labels = clustering.labels_
        labels = np.unique(labels)
        nodata = 255
        profile['nodata'] = nodata
        for label in labels:
            if label != -1:
                center = clustering.cluster_centers_[label]
                size = data[clustering.labels_ == label].shape[0]
                class_data = np.ones((shape[0] * shape[1], 3)) * nodata
                class_data[clustering.labels_ == label] = data[clustering.labels_ == label]
                class_data = class_data.reshape((shape[0], shape[1], 3))
                class_data = class_data.transpose()
                class_output = pathlib.Path(output_dir) / f"{filename}_{label}.tiff"
                with rasterio.open(class_output, 'w', **profile) as dst:
                    dst.write(class_data)
                results[str(label)] = {'center' : [int(x) for x in list(clustering.cluster_centers_[label])], 'size' : int(size)}
        with open(pathlib.Path(output_dir) / f"{filename}.json", 'w') as fd:
            json.dump(results, fd)
        plt.pie([results[p]['size'] for p in results], colors=[[x / 255.0 for x in results[p]['center']] for p in results])
        plt.savefig(pathlib.Path(output_dir) / f"{filename}_colors.svg")

@click.command()
@click.option('-i', '--input-file', help='Input TIFF file')
@click.option('-o', '--output-dir', help='Output directory')
@click.option('-f', '--factor', help='Downsampling factor', default=0.1)
@click.option('-n', '--n-jobs', help='Number of jobs for mean shift algorithm', default=8)
def run_clusterize(input_file, output_dir, factor, n_jobs):
    find_clusters(input_file, output_dir, factor=factor, n_jobs=n_jobs)

if __name__ == '__main__':
    run_clusterize()
