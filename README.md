# Bricky

Upload an image and transform it into a 1x1 brick version.

https://bricky.herokuapp.com/

Bricky uses [Legofy](https://github.com/JuanPotato/Legofy) for the image transformation.

## Setup

Install ImageMagick and zlib devel libraries.
    sudo apt-get install imagemagick zlib1g-dev

Create a Python virtual environment in your preferred way.

    pip install --upgrade pip
    pip install -r requirements.txt
    python brickit.py

Open [http://localhost:5000/](http://localhost:5000/) and upload an image.
