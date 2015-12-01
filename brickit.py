import io
import os

import legofy
from PIL import Image
from flask import Flask, render_template, request, redirect, send_file

BRICK_PATH = os.path.join(os.path.dirname(legofy.__file__), "assets", "bricks", "1x1.png")
BRICK_IMAGE = Image.open(BRICK_PATH)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    uploaded = request.files['file']
    if not uploaded:
        return redirect('/')
    image = Image.open(uploaded)
    new_size = legofy.get_new_size(image, BRICK_IMAGE)
    image.thumbnail(new_size, Image.ANTIALIAS)
    lego_image = legofy.make_lego_image(image, BRICK_IMAGE)
    new_image = io.BytesIO()
    lego_image.save(new_image, format='PNG')
    new_image.seek(0)

    return send_file(new_image, mimetype='image/png')
