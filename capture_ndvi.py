import os
import time
import datetime
import numpy as np
import cv2
import picamera
import picamera.array
import requests

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
ENDPOINT_URL = 'FILL ME'
IMAGE_DIRECTORY = '/home/pi/camera/images'

if not os.path.exists(IMAGE_DIRECTORY):
    os.makedirs(IMAGE_DIRECTORY)

def capture_image(width, height):
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as output:
            camera.resolution = (width, height)
            camera.capture(output, 'rgb')
            return output.array

def calculate_ndvi(image):
    blue_channel = image[:, :, 0].astype(np.float32)
    red_channel = image[:, :, 2].astype(np.float32)

    ndvi = (red_channel - blue_channel) / (red_channel + blue_channel)
    ndvi = np.clip(ndvi, -1, 1)
    ndvi_normalized = cv2.normalize(ndvi, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    #ndvi_normalized = (ndvi + 1) / 2

    return ndvi_normalized

def apply_colormap(image, colormap=cv2.COLORMAP_JET):
    #image_8bit = (image * 255).astype(np.uint8)  # Convert the float image to 8-bit unsigned integer
    #return cv2.applyColorMap(image_8bit, colormap)
    return cv2.applyColorMap(image, colormap)


def save_image(image, filename):
    cv2.imwrite(filename, image)

def send_image_to_endpoint(image_path, endpoint_url):
    with open(image_path, 'rb') as image_file:
        response = requests.post(endpoint_url, files={'fileToUpload': image_file})
    return response

while True:
    current_hour = datetime.datetime.now().hour

    if 8 <= current_hour < 20:  # Check if the current hour is between 8 and 20 (inclusive of 8, exclusive of 20)
        image = capture_image(IMAGE_WIDTH, IMAGE_HEIGHT)
        ndvi_image = calculate_ndvi(image)
        ndvi_image_colored = apply_colormap(ndvi_image)  # Apply colormap to the NDVI image
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        image_filename = os.path.join(IMAGE_DIRECTORY, f'ndvi_{timestamp}.jpg')
        print(image_filename)
        save_image(ndvi_image_colored, image_filename)  # Save the colored NDVI image
        response = send_image_to_endpoint(image_filename, ENDPOINT_URL)
        print(f'Image sent to endpoint with status code: {response.status_code}')
        print (f'Retuerned: {response.text}')
    
    time.sleep(600)  # Sleep for 10 minutes

