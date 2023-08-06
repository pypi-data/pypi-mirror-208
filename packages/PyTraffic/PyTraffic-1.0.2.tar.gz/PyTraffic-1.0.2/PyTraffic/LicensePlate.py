# PyTraffic - License Plate

# Imports
import os
import cv2
import imutils
import numpy as np
import pytesseract

# Variables
OpenCV = "OpenCV"
Tesseract = "Tesseract"

# Function 1 - Check License Plate
def checkLicensePlate(method, path):
    if (os.path.exists(path)):
        if (method == "OpenCV"): # OpenCV
            # Reading the Image
            img = cv2.imread(path)

            # Converting the Images to Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cascade = cv2.CascadeClassifier('PyTraffic/models/license_plate_opencv.xml')

            # Finding the Plates
            plates = cascade.detectMultiScale(gray, 1.2, 5)
            print('Number of Detected License Plates:', len(plates))

            # Displaying Each License Plate
            for (x,y,w,h) in plates:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                gray_plates = gray[y:y+h, x:x+w]
                color_plates = img[y:y+h, x:x+w]

                cv2.imshow('Number Plate', gray_plates)
                cv2.imshow('Number Plate Image', img)
                cv2.waitKey(0)
        elif (method == "Tesseract"): # Tesseract
            # Connecting to Tesseract
            pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

            # Reading the Image
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (600,400))

            # Converting the Images to Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
            gray = cv2.bilateralFilter(gray, 13, 15, 15) 

            # Finding Contours
            edged = cv2.Canny(gray, 30, 200) 
            contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)
            contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
            screenCnt = None

            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.018 * peri, True)

                if len(approx) == 4:
                    screenCnt = approx
                    break

            if screenCnt is None:
                detected = 0
            else:
                detected = 1

            if detected == 1:
                cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

            mask = np.zeros(gray.shape,np.uint8)
            new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
            new_image = cv2.bitwise_and(img,img,mask=mask)

            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx:bottomx+1, topy:bottomy+1]

            # License Plate Number
            text = pytesseract.image_to_string(Cropped, config='--psm 11')

            # Close OpenCV
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Return the License Plate Number
            return text
        else:
            raise Exception("Please use a valid method for identifying the license plate numbers.")
    else:
        raise Exception("The file path does not exist.")