import tensorflow as tf
import os


class Inference:
    """
    This class is used to perform inference on a saved model with a bash input (list of X values)
    and return the predicted value of the model.
    """

    def __init__(self):
        pass

    def predict(self, bash):
        model = tf.keras.models.load_model(os.path.join(os.path.dirname(__file__), 'model'))
        tr_predict = model(bash)
        return tr_predict.numpy()[0]
