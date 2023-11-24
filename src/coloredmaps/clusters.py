from sklearn.cluster import MeanShift, estimate_bandwidth
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

def sharpen(img):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(img, -1, kernel)
    return sharpened

def find_clusters(image_path, output_dir, sharpen_times=0, n_samples=100000, bandwidth=50, n_jobs=8):
    """Finds clusters in a given map in the RGB space.
    """
    filename = pathlib.Path(image_path).stem
    with rasterio.open(image_path) as src:
        profile = src.profile
        orig_data = src.read()
        data = orig_data.transpose()
        for _ in range(sharpen_times):
            data = sharpen(data)
        shape = data.shape
        data = data.reshape(shape[0] * shape[1], 3)
        if bandwidth == -1:
            bandwidth = estimate_bandwidth(data[np.random.choice(data.shape[0], 10000)])
            print(f"Estimated bandwidth: {bandwidth}")
        clustering = MeanShift(bandwidth=bandwidth, n_jobs=n_jobs).fit(data[np.random.choice(data.shape[0], n_samples)])
        results = {}
        predicted_labels = clustering.predict(data)
        labels = np.unique(predicted_labels)
        nodata = 255
        profile['nodata'] = nodata
        for label in labels:
            if label != -1:
                center = clustering.cluster_centers_[label]
                size = data[predicted_labels == label].shape[0]
                class_data = np.ones((shape[0] * shape[1], 3)) * nodata
                class_data[predicted_labels == label] = data[predicted_labels == label]
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
@click.option('-o', '--output-dir', help='Output directory', default=None)
@click.option('-s', '--n-samples', help='Number of samples for clustering', default=100000)
@click.option('-b', '--bandwidth', help='Bandwidth parameter', default=50)
@click.option('-n', '--n-jobs', help='Number of jobs for mean shift algorithm', default=8)
@click.option('-f', '--sharpen', help='Apply the sharpen filter a specified number of times', default=0)
def run_clusterize(input_file, output_dir, n_samples, bandwidth, n_jobs, sharpen):
    if output_dir is None:
        os.makedirs(pathlib.Path(input_file).stem, exist_ok=True)
        output_dir = pathlib.Path(input_file).stem
    find_clusters(input_file, output_dir, n_samples=n_samples, bandwidth=bandwidth, n_jobs=n_jobs, sharpen_times=sharpen)

if __name__ == '__main__':
    run_clusterize()
