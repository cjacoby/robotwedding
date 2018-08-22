import numpy as np
from PIL import Image
import tensorflow as tf
#from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions

print("Loading Model")
model = tf.keras.applications.mobilenet.MobileNet()
#model = ResNet50(weights='imagenet')

def classify_image(img):
    resized = np.array(Image.fromarray(img).resize((224, 224)))
    x = np.expand_dims(image.img_to_array(resized), axis=0)
    x = preprocess_input(x)

    preds = model.predict(x)

    results = decode_predictions(preds, top=3)[0]
    return "Predicted: {}".format(','.join([x[1] for x in results]))
