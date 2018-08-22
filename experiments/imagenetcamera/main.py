#!/usr/bin/env python
"""Runs a main loop."""

import classify
import camera.rpi
import time

def main():
    print("Getting Image...")
    img_gen = camera.rpi.generate_capture()
    try:
        while True:
            image_t0 = time.time()
            image = next(img_gen)
            print("Shape:", image.shape, time.time() - image_t0)
            classify_t0 = time.time()
            classification = classify.classify_image(image)
            print("Classification:", classification, time.time() - classify_t0)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Exiting")
        img_gen.close()


if __name__ == "__main__":
    main()
