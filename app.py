# Class: CST 205 - Multimedia Design & Programming
# Title: app.py
# Abstract: Main file for the flask application
# Authors: Christian Sumares
# Date Created: 04/26/2021

# Library imports
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from PIL import Image

# Local imports
from info import images

app = Flask(__name__)
app.config['SECRET_KEY'] = 'INSERT SECRET KEY HERE'
bootstrap = Bootstrap(app)


class Search(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])


class ImageManipulation(FlaskForm):
    manipulation = SelectField('Effect', choices=['None'])


def search(query):
    keywords = query.lower().split()
    results = []
    for image_id in images:
        image_info = images[image_id]
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


@app.route('/')
def index():

    search_form = Search()

    search_results = []

    query = request.args.get('query')

    if query is not None:
        search_results = search(query)

    return render_template('index.html', form=search_form, search_query=query, search_results=search_results)


@app.route('/image/<image_id>', methods=('GET', 'POST'))
def image(image_id):

    image_form = ImageManipulation()

    if image_form.validate_on_submit():
        # Apply image manipulation here?
        pass

    return render_template('image.html', form=image_form, image_id=image_id)