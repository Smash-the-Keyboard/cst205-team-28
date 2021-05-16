import numpy as np
from PIL import Image
import sys
from PIL.ImageQt import ImageQt
import random
from pixabay import Image
import requests

# Class: CST 205 - Multimedia Design & Programming
# Title: project.py
# Abstract: Code contains functions for image manipulations.
# Authors: Chaitanya Parwatkar
# Date Created: 05/05/2021



#-------- Shrink function ---------
def shrink_image(your_image):
    source3 = Image.open(your_image)
    w,h = source3.width, source3.height

    # target is where the image has to be moved
    # We don't need this if we aren't moving the image anywhere
    # the w, h above is the size of the canvas
    # canvas = Image.new('RGB', (w, h))

    w_image = input ("Enter a value to reduce your image's width (Between 0 - 5): ")
    h_image = input ("Enter a new height (Between 0 - 5): ")

    # this will shrink a picture
    target_x = 0                                                
    for source_x in range(0, source3.width, w_image):           
        target_y = 0                                            
        for source_y in range(0, source3.height, h_image):     
            pixel = source3.getpixel((source_x, source_y))      
            canvas = Image.new('RGB', (round(w/w_image), round(h/h_image))) 
            canvas.putpixel((target_x, target_y), pixel)        
            target_y += 1
        target_x += 1
    canvas.show()



#-------- Resize function ---------
def resize_up_down(your_image):

    # opens an image
    image = Image.open(your_image)

    # We ask the user what size he wants to resize the image to
    w = input ("Enter a new width for the image: ")
    h = input ("Enter a new height: ")
    resized_image = image.resize(w, h)
    # resized_image.save('bb3_resized.jpg')
    resized_image.show()




# -------- Scaling up function ---------
def scaling_up(your_image):
    source = Image.open(your_image)
    mf = input ("Enter a value to enlarge your image (Between 2 - 4): ")
    w, h = source.width * mf, source.height * mf
    target = Image.new('RGB', (w,h))

    target_x = 0
    for source_x in np.repeat(range(source.width), mf):
        target_y = 0
        for source_y in np.repeat(range(source.height), mf):
            pixel = source.getpixel((int(source_x), int(source_y)))
            target.putpixel((target_x, target_y), pixel)
            target_y += 1
        target_x += 1
    target.show()



# -------- Grayscale function ---------	
def grayscale(your_image):
	im2 = Image.open(your_image)
	new_list =  [((a[0]*299 + a[1]*587 + a[2]*114 )//1000,) * 3
	for a in im2.getdata()]
	im2.putdata(new_list)
	
	# turning image from PIL to QImage
	if im2.mode == 'RGB':
		im2 = im2.convert('RGBA')
	qimage = toqimage(im2)
	return QPixmap.fromImage(qimage)
	


# -------- Negative function ---------
def negative(your_image):
    img = Image.open(your_image)
    image_a = np.array(img)
    max_value = 255
    image_a = max_value - image_a
    inverted_image = Image.fromarray(image_a)
    inverted_image.show()



#-------- sepia function ---------
def sepia(your_image):
	im2 = Image.open(your_image)
	width, height = im2.size
	sepiaImg = im2.copy()
	
	for x in range(width):
		for y in range(height):
			red, green, blue = im2.getpixel((x,y))
			new_val = (0.3 * red + 0.59 * green + 0.11 * blue)

			new_red = int(new_val * 2)
			if new_red > 255:
				new_red = 255
			new_green = int(new_val * 1.5)
			if new_green > 255:
				new_green = 255
			new_blue = int(new_val)
			if new_blue > 255:
				new_blue = 255

			sepiaImg.putpixel((x,y), (new_red, new_green, new_blue))
	#turn PIL image to Qimage so we can use it in the GUI		
	if sepiaImg.mode == 'RGB':
		sepiaImg = sepiaImg.convert('RGBA')
	qimage = toqimage(sepiaImg)

	return QPixmap.fromImage(qimage)
	
	
	
#------ thumbnail function -------
def thumbnail(your_image):
	im2 = Image.open(your_image)
	w, h = im2.width,im2.height
	target = Image.new('RGB', (w, h), 'aliceblue')
	
	target_x = 0
	for source_x in range(0, im2.width, 2):
		target_y = 0
		for source_y in range(0, im2.height, 2):
			pixel = im2.getpixel((source_x, source_y))
			target.putpixel((target_x, target_y), pixel)
			target_y += 1
		target_x += 1
	#turn PIL image to Qimage so we can use it in the GUI		
	if target.mode == 'RGB':
		target = target.convert('RGBA')
	qimage = toqimage(target)

	return QPixmap.fromImage(qimage)

	
#---------none function return the same picture ----------
def none(your_image):
	im2 = Image.open(your_image)
	
	if im2.mode == 'RGB':
		im2 = im2.convert('RGBA')
	qimage = toqimage(im2)

	return QPixmap.fromImage(qimage)