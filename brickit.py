from datetime import datetime
import io
import logging
import os

from PIL import Image
from flask import Flask, render_template, request, redirect, send_file, got_request_exception
from flask_sslify import SSLify
import keen
import legofy
import rollbar
import rollbar.contrib.flask

DEV = 'development'
LIVE = 'production'

BRICK_PATH = os.path.join(os.path.dirname(legofy.__file__), "assets", "bricks", "1x1.png")
BRICK_IMAGE = Image.open(BRICK_PATH)

ROLLBAR_ACCESS_TOKEN = os.environ.get('ROLLBAR_ACCESS_TOKEN', None)

BRICKY_ENV = os.environ.get('BRICKY_ENV', DEV)

app = Flask(__name__)
if BRICKY_ENV == LIVE:
    sslify = SSLify(app, age=600)


@app.before_first_request
def setup_logging():
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.before_first_request
def setup_rollbar():
    if ROLLBAR_ACCESS_TOKEN:
        rollbar.init(ROLLBAR_ACCESS_TOKEN, BRICKY_ENV, root=os.path.dirname(os.path.realpath(__file__)), allow_logging_basic_config=False)
        got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bad')
def bad():
    1 / 0
    return None


@app.route('/upload', methods=['POST'])
def upload():
    uploaded = request.files['file']
    if not uploaded:
        return redirect('/')
    file_info = {'filename': uploaded.filename, 'mimetype': uploaded.mimetype}
    try:
        image = Image.open(uploaded)
    except IOError:
        app.logger.info('Bad Upload - {}'.format(file_info))
        if BRICKY_ENV == LIVE:
            keen.add_event('bad_upload', file_info)
        return redirect('/')
    new_size = legofy.get_new_size(image, BRICK_IMAGE)
    image.thumbnail(new_size, Image.ANTIALIAS)
    lego_image = legofy.make_lego_image(image, BRICK_IMAGE)
    new_image = io.BytesIO()
    lego_image.save(new_image, format='PNG')
    new_image.seek(0)

    browser_info = {'user_agent': request.headers.get('User-Agent', 'No Agent'),
                    'X-Request-ID': request.headers.get('X-Request-ID', 'Missing X-Request-ID')}

    app.logger.info('Headers - {}'.format(browser_info))
    app.logger.info('Upload - {}'.format(file_info))
    if BRICKY_ENV == LIVE:
        keen.add_event('browser', browser_info)
        keen.add_event('upload', file_info)

    response = send_file(new_image, mimetype='image/png')
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True)
