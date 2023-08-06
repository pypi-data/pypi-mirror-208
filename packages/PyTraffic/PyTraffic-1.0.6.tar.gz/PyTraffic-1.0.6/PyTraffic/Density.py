# PyTraffic - Density

# Imports
import cv2
import os

# Function 1 - Check Density
def checkDensity(path):
    if (os.path.exists(path)):
        # Set Directory
        directory = os.path.dirname(os.path.realpath(__file__))
        directory = directory.replace(os.sep, "/")

        carsXml = cv2.CascadeClassifier(directory + "/models/cars.xml")

        count = 0
        frame = cv2.imread(path)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = carsXml.detectMultiScale(gray, 1.1, 1)

        for (x,y,w,h) in cars:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2) 
            count+=1

        cv2.waitKey(1)
        cv2.destroyAllWindows()

        return count
    else:
        raise Exception("The file path does not exist.")