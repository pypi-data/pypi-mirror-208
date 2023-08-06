# PyTraffic - Vehicle Detection

# Imports
from PIL import Image
import cv2
import numpy as np
import os
import mimetypes
import time

# Set Directory
directory = os.path.dirname(os.path.realpath(__file__))
directory = directory.replace(os.sep, "/")

# Variables
car_cascade = cv2.CascadeClassifier(directory + "/models/haarcascade_car.xml")

# Function 1 - Detect Cars
def detectCars(path, showFile=False):
    if (os.path.exists(path)):
        # Check File Type
        mimetypes.init()

        mimestart = mimetypes.guess_type(path)[0]
        mimestart = mimestart.split('/')[0]

        if (mimestart == "image"): # Image
            # Opening the Image
            image = Image.open(path)
            image = image.resize((450, 250))
            image_arr = np.array(image)

            # Converting Image to Greyscale
            grey = cv2.cvtColor(image_arr, cv2.COLOR_BGR2GRAY)
            Image.fromarray(grey)

            # Blurring the Image
            blur = cv2.GaussianBlur(grey, (5,5), 0)
            Image.fromarray(blur)

            # Dilating the Image
            dilated = cv2.dilate(blur, np.ones((3,3)))
            Image.fromarray(dilated)

            # Morphology
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel) 
            Image.fromarray(closing)

            # Identifying the Cars
            cars = car_cascade.detectMultiScale(closing, 1.1, 1)

            # Counting the Cars
            count = 0

            for (x, y, w, h) in cars:
                cv2.rectangle(image_arr,(x,y),(x+w,y+h),(255,0,0),2)
                count += 1

            # Returning the Count and Image
            if (showFile):
                Image._show(Image.fromarray(image_arr))
            else:
                return count
        elif (mimestart == "video"):
            # Opening the Video
            video = cv2.VideoCapture(path)

            # Variables
            count = 0

            # Opening the Video and Processing
            while video.isOpened():
                time.sleep(.05)

                # Read First Frame
                ret, frame = video.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Identifying the Cars
                cars = car_cascade.detectMultiScale(gray, 1.4, 2)

                for (x,y,w,h) in cars:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.imshow('Vehicle Detection - Cars', frame)

                    count += 1

                # Clicking 'q' Closes the Video
                if cv2.waitKey(1) == ord("q"):
                    break

            video.release()
            cv2.destroyAllWindows()

            return count
        else:
            raise Exception("The file provided must be an image or a video.")
    else:
        raise Exception("The file path does not exist.")

print(detectCars('C:/myFolder/Aniketh Chavare/Elvvo/templates/assets/media/Speed/1.mp4'))