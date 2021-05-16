# Class: CST 205 - Multimedia Design & Programming
# Title: app.py
# Abstract: Main file for the flask application
# Authors: Christian Sumares
# Date Created: 04/26/2021
# Library imports
import os
import ast

from flask import Flask, render_template, request, json
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from PIL import Image

# Flickr API Library
from flickrapi import FlickrAPI

# Local imports
from info import images

FLICKR_PUBLIC = 'db7abd50cd8fc7f7ee439f787cc05413'
FLICKR_SECRET = 'c624cffc27d82c00'

flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
extras='url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'INSERT SECRET KEY HERE'
bootstrap = Bootstrap(app)
class Search(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    count = StringField('Count', validators=[DataRequired()])


class ImageManipulation(FlaskForm):
    manipulation = SelectField('Effect', choices=['None'])

flickr = None

def flickr_init():
    filename = os.path.join(app.static_folder, 'data', 'flickr.json')
    with open(filename) as flickr_file:
        flickr_keys = json.load(flickr_file)
        flickr = FlickrAPI(flickr_keys['public_key'], flickr_keys['secret_key'], format='json')
    return flickr

def flickr_search(query, count, flickr):
    extras = 'url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    decode = (flickr.photos.search(text=query, per_page=count, extras=extras)).decode('utf-8')
    photos = ast.literal_eval(decode)
    return photos['photos']['photo']

@app.route('/', methods=['GET', 'POST'])
def index():
    flickr = flickr_init()
    
    search_form = Search()
    search_results = []
    query = request.args.get('query')
    count = request.args.get('count')
    
    if query is not None:
        search_results = flickr_search(query, count, flickr)

    return render_template('index.html', form=search_form, search_query=query, search_results=search_results)
@app.route('/image/<image_id>', methods=('GET', 'POST'))
def image(image_id):
    image_form = ImageManipulation()
    if image_form.validate_on_submit():
        # Apply image manipulation here?
        pass
    return render_template('image.html', form=image_form, image_id=image_id)