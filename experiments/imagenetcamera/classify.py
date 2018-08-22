from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions

print("Loading Model")
model = ResNet50(weights='imagenet')

def classify_image(img):
        resized = np.array(Image.fromarray(img).resize((224, 224)))
        x = np.expand_dims(image.img_to_array(resized), axis=0)
        x = preprocess_input(x)

        preds = model.predict(x)

        results = decode_predictions(preds, top=3)[0]
        return f"Predicted: {','.join([x[1] for x in results])}"

