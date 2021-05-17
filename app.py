# Class: CST 205 - Multimedia Design & Programming
# Title: app.py
# Abstract: Main file for the flask application
# Authors: Christian Sumares, Ethan Blake Castro
# Date Created: 04/26/2021

# Standard imports
import ast
import os

# Library imports
from flask import Flask, render_template, request, json, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flickrapi import FlickrAPI  # Flickr API Library
from requests import get as requests_get
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

# Local imports
from transform import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'INSERT SECRET KEY HERE'
bootstrap = Bootstrap(app)


image_effects = ['None', 'Grayscale', 'Negative', 'Sepia', 'Thumbnail']


def get_image_info_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    infoJSON = os.path.join(dir_path, "info.json")
    with open(infoJSON) as info:
        return json.loads(info.read())


def save_image_info_file(info_dict):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    infoJSON = os.path.join(dir_path, "info.json")
    with open(infoJSON, 'w') as info_file:
        info_file.write(json.dumps(info_dict))


def id_from_filename(filename):
    return os.path.basename(filename).rsplit('.')[0]


def get_image_info(image_id):

    image_info = {}

    local_info = get_image_info_file()

    if image_id in local_info:
        image_info = local_info[image_id]
        image_info['url'] = f'/static/images/{image_id}.jpg'
    else:
        raw_response = flickr.photos.getInfo(photo_id=image_id)
        flickr_info = json.loads(raw_response.decode('utf-8'))
        if flickr_info['stat'] == 'ok':
            photo = flickr_info['photo']
            # Get url of original photo
            photo_sizes = json.loads(flickr.photos.getSizes(photo_id=image_id).decode('utf-8'))
            original_url = photo_sizes['sizes']['size'][-1]['source']
            image_info = {
                'title': photo['title']['_content'],
                'tags': [tag['_content'] for tag in photo['tags']['tag']],
                'flickr_page_url': photo['urls']['url'][0]['_content'],
                'url': original_url
            }

    return image_info


class Search(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])


class ImageEffect(FlaskForm):
    effect = SelectField('Effect', choices=image_effects)


class ImageUpload(FlaskForm):
    image_file = FileField('Image', validators=[FileRequired()])
    image_title = StringField('Title', validators=[DataRequired()])
    image_tags = StringField('Tags')
    image_effect = SelectField('Effect', choices=image_effects)


# Initialize Flickr API module
flickr_filename = os.path.join(app.static_folder, 'data', 'flickr.json')
with open(flickr_filename) as flickr_file:
    flickr_keys = json.load(flickr_file)
    flickr = FlickrAPI(flickr_keys['public_key'], flickr_keys['secret_key'], format='json')


def search(query):
    keywords = query.lower().split()
    results = []
    image_info_file = get_image_info_file()
    for image_id in image_info_file:
        image_info = image_info_file[image_id]
        hits = 0
        for keyword in keywords:
            if keyword in image_info['title'].lower().split() or keyword in [tag.lower() for tag in image_info['tags']]:
                hits += 1
        if hits != 0:
            image_info['id'] = image_id
            image_info['hits'] = hits
            results.append(image_info)
    results.sort(key=lambda img: img['hits'], reverse=True)
    return results


def flickr_search(query):
    extras = 'url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    decode = (flickr.photos.search(text=query, per_page=5, safe_search=1, extras=extras)).decode('utf-8')
    photos = ast.literal_eval(decode)
    return photos['photos']['photo']


def apply_image_effect(image_path, effect, output_path=None):

    if output_path is None:
        output_path = image_path

    if effect == 'Grayscale':
        grayscale(image_path, output_path)
    elif effect == 'Negative':
        negative(image_path, output_path)
    elif effect == 'Sepia':
        sepia(image_path, output_path)
    elif effect == 'Thumbnail':
        thumbnail(image_path, output_path)


def download_flickr_image(flickr_url, file_path):
    r = requests_get(flickr_url, stream=True)
    with open(file_path, 'wb') as f:
        for chunk in r:
            f.write(chunk)


@app.route('/')
def index():

    search_form = Search()

    local_results = []
    flickr_results = []

    query = request.args.get('query')

    if query is not None:
        local_results = search(query)
        flickr_results = flickr_search(query)

    return render_template(
        'index.html',
        form=search_form,
        search_query=query,
        local_results=local_results,
        flickr_results=flickr_results
    )


@app.route('/image/<image_id>', methods=('GET', 'POST'))
def image(image_id):

    effect_form = ImageEffect()

    image_info = get_image_info(image_id)

    effect = effect_form.effect.data

    if 'url' not in image_info:
        abort(404)

    if effect_form.validate_on_submit() and effect != 'None':
        # Build image file name
        modified_file_name = f'{image_id}_{effect}.jpg'
        # Check if a modified image already exists
        modified_file_path = os.path.join(
            app.instance_path,
            '..',
            'static',
            'images',
            'effect_cache',
            modified_file_name
        )
        if not os.path.exists(modified_file_path):
            if 'flickr_page_url' in image_info:
                # Download a copy of the original image
                download_flickr_image(image_info['url'], modified_file_path)
                # Apply effect
                apply_image_effect(modified_file_path, effect)
            else:
                # Get the path of the original file
                original_file_path = os.path.join(app.instance_path, '..', 'static', 'images', f'{image_id}.jpg')
                # Apply effect
                apply_image_effect(original_file_path, effect, modified_file_path)
        # Update image url for this response
        image_info['url'] = f'/static/images/effect_cache/{modified_file_name}'

    return render_template('image.html', form=effect_form, image_info=image_info)


@app.route('/upload', methods=('GET', 'POST'))
def upload():

    upload_form = ImageUpload()

    if upload_form.validate_on_submit():
        print('Upload form is valid')
        # Save image file
        image_file = upload_form.image_file.data
        image_file_path = os.path.join(app.instance_path, '..', 'static', 'images', image_file.filename)
        image_file.save(image_file_path)
        # Apply effect, if any
        apply_image_effect(image_file_path, upload_form.image_effect.data)
        # Update info.json
        image_id = id_from_filename(image_file.filename)
        image_info = get_image_info_file()
        image_info[image_id] = {
            'title': upload_form.image_title.data,
            'tags': upload_form.image_tags.data.split(',')
        }
        save_image_info_file(image_info)
        return redirect(url_for('image', image_id=image_id))
    else:
        print(upload_form.image_title.data)
        print('Upload form is NOT valid!')
        print(upload_form.errors)

    return render_template('upload.html', form=upload_form)