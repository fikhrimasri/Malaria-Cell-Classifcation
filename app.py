from __future__ import division, print_function
import os
import numpy as np

# Tensorflow
import tensorflow as tf
from tensorflow.keras.models import load_model

# load image
from PIL import Image
from skimage import transform

# Flask utils
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Request, Response

# Define a flask app
app = Flask(__name__)

# Model saved with tensorflow model.save()
MODEL_PATH = 'Models/model_best.h5'

#Load your trained model
model = load_model(MODEL_PATH)
model._make_predict_function()          # Necessary to make everything ready to run on the GPU ahead of time
print('Model Succes Load..')


def model_predict(filename, model):
   np_image = Image.open(filename)
   np_image = np.array(np_image).astype('float32')/255
   np_image = transform.resize(np_image, (64, 64))
   np_image = np.expand_dims(np_image, axis=0)
   pred = model.predict(np_image)
   return pred

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.join(os.getcwd())
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        pred = model_predict(file_path, model)
        os.remove(file_path)#removes file from the server after prediction has been returned

        if pred[0] > 0.5:
            return "Not Detect Malaria Cell"
        else:
            return "Detect Malaria Cell"
    return None

    #this section is used by gunicorn to serve the app on Heroku
if __name__ == '__main__':
        app.run()

