import matplotlib.pyplot as plt
import keras_ocr
import math
import cv2
import numpy as np

def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2)/2)
    y_mid = int((y1 + y2)/2)
    return (x_mid, y_mid)

def inpaint_text(img, pipeline):
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    for box in prediction_groups[0]:
        x0, y0 = box[1][0]
        x1, y1 = box[1][1]
        x2, y2 = box[1][2]
        x3, y3 = box[1][3]

        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mid1 = midpoint(x0, y0, x3, y3)

        thickness = int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mid1), 255, thickness)
        img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)

    return img

def process_image_with_patches(img_path, pipeline, patch_size):
    img = keras_ocr.tools.read(img_path)
    height, width = img.shape[:2]

    for x in range(0, width, patch_size):
        for y in range(0, height, patch_size):
            patch = img[y:y + patch_size, x:x + patch_size]
            img[y:y + patch_size, x:x + patch_size] = inpaint_text(patch, pipeline)

    return img

pipeline = keras_ocr.pipeline.Pipeline()

img_path = '/localhome/zapp_an/Desktop/DataXplorer_hackaton/png/Pls_8540_0014.png'
patch_size = 200  # Adjust the patch size as needed for your small texts

new_img = process_image_with_patches(img_path, pipeline, patch_size)

img_rgb = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
cv2.imwrite('Pls_8540_0014_patch200.jpg', img_rgb)
