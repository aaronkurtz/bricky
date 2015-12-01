from datetime import datetime
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
    try:
        image = Image.open(uploaded)
    except IOError:
        return redirect('/')
    new_size = legofy.get_new_size(image, BRICK_IMAGE)
    image.thumbnail(new_size, Image.ANTIALIAS)
    lego_image = legofy.make_lego_image(image, BRICK_IMAGE)
    new_image = io.BytesIO()
    lego_image.save(new_image, format='PNG')
    new_image.seek(0)

    response = send_file(new_image, mimetype='image/png')
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True)
