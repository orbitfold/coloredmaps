from sklearn.cluster import MeanShift, estimate_bandwidth
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

def find_clusters(image_path, output_dir, sharpen_times=0, n_samples=100000, bandwidth=50, n_jobs=8, color=cv2.COLOR_BGR2RGB):
    """Finds clusters in a given map in the RGB space.
    """
    filename = pathlib.Path(image_path).stem
    data = cv2.imread(image_path)
    data = cv2.cvtColor(data, color)    
    for _ in range(sharpen_times):
        data = sharpen(data)
    shape = data.shape
    data = data.reshape(shape[0] * shape[1], 3)
    if bandwidth == -1:
        bandwidth = estimate_bandwidth(data[np.random.choice(data.shape[0], 10000)])
    print(f"Bandwidth value in use: {bandwidth}")
    clustering = MeanShift(bandwidth=bandwidth, n_jobs=n_jobs).fit(data[np.random.choice(data.shape[0], n_samples)])
    results = {}
    predicted_labels = clustering.predict(data)
    labels = np.unique(predicted_labels)
    nodata = 255
    for label in labels:
        if label != -1:
            center = clustering.cluster_centers_[label]
            size = data[predicted_labels == label].shape[0]
            class_data = np.ones((shape[0] * shape[1], 3)) * nodata
            class_data[predicted_labels == label] = data[predicted_labels == label]
            class_data = class_data.reshape((shape[0], shape[1], 3))
            class_output = pathlib.Path(output_dir) / f"{filename}_{label}.tiff"
            cv2.imwrite(str(class_output), cv2.cvtColor(class_data.astype(np.uint8), color))
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
@click.option('-c', '--color', help='Choose a color space', default=cv2.COLOR_BGR2RGB)
def run_clusterize(input_file, output_dir, n_samples, bandwidth, n_jobs, sharpen, color):
    if output_dir is None:
        os.makedirs(pathlib.Path(input_file).stem, exist_ok=True)
        output_dir = pathlib.Path(input_file).stem
    find_clusters(input_file, output_dir, n_samples=n_samples, bandwidth=bandwidth, n_jobs=n_jobs, sharpen_times=sharpen, color=color)

if __name__ == '__main__':
    run_clusterize()
