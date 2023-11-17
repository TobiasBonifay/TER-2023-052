import tensorflow as tf
from tensorflow.python.keras.models import load_model


class Inferance:

    def __init__(self):
        pass

    def predict(self, bash):
        try:
            model = load_model("model")
            tr_predict = model(bash)
            return tr_predict.numpy()[0]
        except:
            print("Error while loading model")
        return 0
