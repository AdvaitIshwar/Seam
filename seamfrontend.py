import seamcarver as sc
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
global filename, myImage, myImageTwo

def carve(myImage, myImageTwo, count):
    myImage, myImageTwo = sc.carve_image(myImage, myImageTwo)
    display = ImageTk.PhotoImage(myImageTwo)
    panel.config(image = display)
    panel.image = display
    if count > 0:
        root.after(1, carve, myImage, myImage, count-1)


root = tk.Tk()
root.title("Seam Carving Visualizer")
root.geometry("1000x1000")

#def open():
    

#btn = tk.Button(root, text = "Open Image", command = open).pack()
filename = filedialog.askopenfilename(initialdir = "/", title = "Select an Image")
myImage = Image.open(filename)
myImageTwo = myImage.copy()
display_image_two = ImageTk.PhotoImage(myImageTwo)
panel = tk.Label(root, image=display_image_two)
panel.image = display_image_two
panel.pack()
carve(myImage, myImageTwo, 100)

root.mainloop()

