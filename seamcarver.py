import numpy as np
import cv2
import math
from PIL import Image, ImageTk
from scipy import ndimage
from imageio import imread, imwrite
from tkinter import filedialog
import tkinter as tk
from numba import jit

def calc_energy(img):
    filter_du = np.array([
        [1.0, 2.0, 1.0],
        [0.0, 0.0, 0.0],
        [-1.0, -2.0, -1.0],
    ])
    # This converts it from a 2D filter to a 3D filter, replicating the same
    # filter for each channel: R, G, B
    filter_du = np.stack([filter_du] * 3, axis=2)

    filter_dv = np.array([
        [1.0, 0.0, -1.0],
        [2.0, 0.0, -2.0],
        [1.0, 0.0, -1.0],
    ])
    # This converts it from a 2D filter to a 3D filter, replicating the same
    # filter for each channel: R, G, B
    filter_dv = np.stack([filter_dv] * 3, axis=2)

    img = img.astype('float32')
    convolved = np.absolute(ndimage.convolve(img, filter_du)) + np.absolute(ndimage.convolve(img, filter_dv))

    # We sum the energies in the red, green, and blue channels
    energy_map = convolved.sum(axis=2)
    return energy_map

@jit
def energy_map(myImage,height,width):
    energy = []
    imagearr = []
    for y in range(0,height):
        imagearr.append([])
        energy.append([])
        for x in range(0,width):
            #left
            if(x != 0):
                r_l, g_l, b_l = myImage.getpixel((x-1, y))
            else:
                r_l, g_l, b_l = myImage.getpixel((x, y))
            #right
            if(x != width-1):
                r_r, g_r, b_r = myImage.getpixel((x+1, y))
            else:
                r_r, g_r, b_r = myImage.getpixel((x, y))
            #up
            if(y != 0):
                r_u, g_u, b_u = myImage.getpixel((x, y-1))
            else:
                r_u, g_u, b_u = myImage.getpixel((x, y))
            #down
            if(y != height-1):
                r_d, g_d, b_d = myImage.getpixel((x, y+1))
            else:
                r_d, g_d, b_d = myImage.getpixel((x, y))

            v_dist = (r_u - r_d)**2 + (b_u - b_d)**2 + (g_u - g_d)**2
            h_dist = (r_l - r_r)**2 + (b_l - b_r)**2 + (g_l - g_r)**2
            e = v_dist + h_dist
            imagearr[y].append(myImage.getpixel((x,y)))
            energy[y].append(e)
    np_energy = np.array(energy, dtype='float32')
    return np_energy, imagearr

@jit
def min_seam_energy(myImage, height, width):
    energy, imagearr = energy_map(myImage, height, width)
    previous = list(energy[0])
    coord_pointers = {}
    for y in range(1, len(energy)):
        pixel_energies_row = energy[y]
        seam_energies_row = []
        for x, pixel_energy in enumerate(pixel_energies_row):
            x_left = max(x - 1, 0)
            x_right = min(x + 1, len(pixel_energies_row) - 1)
            if previous[x_left] < previous[x] and previous[x_left] < previous[x_right]:
                index = x_left - x
                min_seam_energy = pixel_energy + previous[x_left]
            elif previous[x_right] < previous[x] and previous[x_right] < previous[x]:
                index = x_right - x
                min_seam_energy = pixel_energy + previous[x+1]
            else:
                index = 0
                min_seam_energy = pixel_energy + previous[x]
            seam_energies_row.append(min_seam_energy)
            coord_pointers[(x,y)] = (index+x, y-1)
        previous = seam_energies_row
    return np.argmin(previous), coord_pointers, imagearr

@jit
def carve_image(myImage, myImageTwo):
    #img = imread("/Users/advaitishwar/Desktop/seam2.jpg")
    # width = columns, height = rows
    width, height = myImage.size
    #energy, np_energy,imagearr = energy_map(myImage, height, width) #root means square energy function
    #energy1 = calc_energy(img) #sobel filter energy function
    column, coord_pointers, imagearr = min_seam_energy(myImage, height, width)
    for i in range(width):
        coord_pointers[(i,0)] = (-1,-1)

    x = column
    y = height-1
    for i in range(height):
        myImageTwo.putpixel((x, y), (255,0,0))
        imagearr[y].pop(x)
        x,y = coord_pointers[(x,y)]
        
    image_step = np.array(imagearr, dtype = 'uint8')
    myImage = Image.fromarray(image_step)
    return myImage, myImageTwo

def main():
    myImage = Image.open("/Users/advaitishwar/Desktop/seam2.jpg")
    myImageTwo = myImage.copy()
    for i in range(0,20):
        myImage, myImageTwo = carve_image(myImage, myImageTwo)
    myImage.show()
    myImageTwo.show()



if __name__ == "__main__":
    main()