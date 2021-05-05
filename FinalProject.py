'''
Title: hw4.py
Description: Display 3 random images and provide info about them when clicking their hyperlink
Author: Ozzie Moreno
Date:4/15/2021
'''

from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from image_info import image_info
import random
from PIL import Image

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "aaaa"

# main route 
@app.route('/')
def main():
    # send random list to main route
    random.shuffle(image_info)
    return render_template('main.html', data=image_info)

# takes in a parameter which will be the id of the photo
@app.route('/picture/<temp>')
def picture(temp):
    current = {}
    # look for matching id and set current picture
    for a in image_info:
        if a['id'] == temp:
            current = a
    # get information of the image from pillow
    pic = Image.open('hw4/static/images/'+current['id']+'.jpg')
    return render_template('picture.html', data=current, details=pic)
