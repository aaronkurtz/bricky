import os

import legofy
import PIL
from flask import Flask, render_template

brick_path = os.path.join(os.path.dirname(legofy.__file__), "assets", "bricks", "1x1.png")
brick_image = PIL.Image.open(brick_path)

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')
