# Class: CST 205 - Multimedia Design & Programming
# Title: app.py
# Abstract: Main file for the flask application
# Authors: Christian Sumares
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
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from PIL import Image


app = Flask(__name__)
app.config['SECRET_KEY'] = 'INSERT SECRET KEY HERE'
bootstrap = Bootstrap(app)


image_effects = ['None']

def get_image_info_file():
    with open('info.json') as info:
        return json.loads(info.read())


def save_image_info_file(info_dict):
    with open('info.json', 'w') as info_file:
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
        print(raw_response)
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
    decode = (flickr.photos.search(text=query, per_page=5, extras=extras)).decode('utf-8')
    photos = ast.literal_eval(decode)
    return photos['photos']['photo']


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

    if effect_form.validate_on_submit():
        # Manipulate image here?
        # Update image url for this response
        pass

    if 'url' not in image_info:
        abort(404)

    return render_template('image.html', form=effect_form, image_info=image_info)


@app.route('/upload', methods=('GET', 'POST'))
def upload():

    upload_form = ImageUpload()

    if upload_form.validate_on_submit():
        print('Upload form is valid')
        # Save image file
        image_file = upload_form.image_file.data
        image_file.save(os.path.join(app.instance_path, '..', 'static', 'images', image_file.filename))
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
