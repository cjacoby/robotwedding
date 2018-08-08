import click
import io
import numpy as np
import picamera
import picamera.array
from PIL import Image
import time


def capture_image(jpeg_path):
    """Capture an image from the camera, save it to jpeg_path."""
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(jpeg_path)


def capture_image_pil():
    """Capture an image and return it as a PIL.Image"""
    # Create the in-memory stream
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        camera.capture(stream, format='jpeg')
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)
    return image


def capture_resized_array(newsize=(224, 224)):
    """
    * Capture an image as an RGB array
    * resize it to newsize
    """
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        with picamera.array.PiRGBArray(camera, size=newsize) as output:
            camera.capture(output, 'rgb', resize=newsize)
            print('Captured {}x{} image'.format(output.array.shape[1], output.array.shape[0]))
            import pdb; pdb.set_trace()
            print("Shape:", output.array.shape)
            return output.array


if __name__ == "__main__":
    capture_image("testimg.jpeg")

    capture_resized_array()
    