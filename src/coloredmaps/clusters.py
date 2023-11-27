from sklearn.cluster import MeanShift, estimate_bandwidth
import numpy as np
import matplotlib.pyplot as plt
import cv2
import colorsys
import click
import json
import pathlib
import os

COLOR_SPACES = {
    'rgb': (cv2.COLOR_BGR2RGB, cv2.COLOR_RGB2BGR, None),
    'hsl': (cv2.COLOR_BGR2HLS, cv2.COLOR_HLS2BGR, cv2.COLOR_HLS2RGB),
    'hsv': (cv2.COLOR_BGR2HSV, cv2.COLOR_HSV2BGR, cv2.COLOR_HSV2RGB),
    'xyz': (cv2.COLOR_BGR2XYZ, cv2.COLOR_XYZ2BGR, cv2.COLOR_XYZ2RGB),
    'lab': (cv2.COLOR_BGR2LAB, cv2.COLOR_LAB2BGR, cv2.COLOR_LAB2RGB),
    'luv': (cv2.COLOR_BGR2LUV, cv2.COLOR_LUV2BGR, cv2.COLOR_LUV2RGB)
}

def sharpen(img):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(img, -1, kernel)
    return sharpened

def find_clusters(image_path, output_dir, sharpen_times=0, n_samples=100000, bandwidth=50, n_jobs=8, color='rgb'):
    """Finds clusters in a given map in the RGB space.
    """
    filename = pathlib.Path(image_path).stem
    data = cv2.imread(image_path)
    data = cv2.cvtColor(data, COLOR_SPACES[color][0])    
    for _ in range(sharpen_times):
        data = sharpen(data)
    shape = data.shape
    data = data.reshape(shape[0] * shape[1], 3)
    if bandwidth == -1:
        bandwidth = estimate_bandwidth(data[np.random.choice(data.shape[0], 10000)])
    print(f"Bandwidth value in use: {bandwidth}")
    print(f"Color space in use: {color}")
    clustering = MeanShift(bandwidth=bandwidth, n_jobs=n_jobs).fit(data[np.random.choice(data.shape[0], n_samples)])
    results = {}
    predicted_labels = clustering.predict(data)
    labels = np.unique(predicted_labels)
    nodata = 255
    for label in labels:
        if label != -1:
            center = clustering.cluster_centers_[label]
            size = data[predicted_labels == label].shape[0]
            class_data = np.zeros((shape[0] * shape[1], 3))
            alpha = (predicted_labels == label).astype(np.uint8) * 255
            alpha = alpha.reshape((shape[0], shape[1]))
            class_data[predicted_labels == label] = data[predicted_labels == label]
            class_data = class_data.reshape((shape[0], shape[1], 3))
            class_output = pathlib.Path(output_dir) / f"{filename}_{label}.tiff"
            bgr_data = cv2.cvtColor(class_data.astype(np.uint8), COLOR_SPACES[color][1])
            b_data, g_data, r_data = cv2.split(bgr_data)
            bgra_data = cv2.merge((b_data, g_data, r_data, alpha))
            cv2.imwrite(str(class_output), bgra_data)
            if color != 'rgb':
                rgb_center = list(cv2.cvtColor(np.array([[center]]).astype(np.uint8), COLOR_SPACES[color][2])[0][0])
            else:
                rgb_center = list(center)
            results[str(label)] = {'center' : [int(x) for x in rgb_center], 'size' : int(size)}
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
@click.option('-c', '--color', help='Choose a color space', default='rgb')
def run_clusterize(input_file, output_dir, n_samples, bandwidth, n_jobs, sharpen, color):
    if output_dir is None:
        os.makedirs(pathlib.Path(input_file).stem, exist_ok=True)
        output_dir = pathlib.Path(input_file).stem
    if color not in COLOR_SPACES:
        print(f"Color space not supported, choose from {list(COLOR_SPACES.keys())}")
        exit()
    find_clusters(input_file, output_dir, n_samples=n_samples, bandwidth=bandwidth, n_jobs=n_jobs, sharpen_times=sharpen, color=color)

if __name__ == '__main__':
    run_clusterize()
