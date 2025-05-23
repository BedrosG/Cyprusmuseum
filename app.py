from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
import base64
import io
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

@app.route('/')
def index():
    return "✅ Mobile Object Detection Server is running."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)

        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = model.predict(x)
        decoded = decode_predictions(preds, top=1)[0][0]
        label = decoded[1]
        confidence = float(decoded[2])

        return jsonify({'label': label, 'confidence': confidence})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
