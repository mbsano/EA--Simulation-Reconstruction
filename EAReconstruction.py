__author__ = 'Mike'

import os,sys
from PyQt4.QtGui import QDialog, QBitmap, QImage, QPixmap, QImageWriter, QImageReader, qRgb
import csv
from PyQt4.Qt import QPoint, QColor
from math import sqrt


def main():
    print "running program"
    screenwidth =2800 #5120
    screenheight = 1800 #2880
    mainImage = QImage(screenwidth, screenheight, QImage.Format_RGB32)
    mainImage.fill(qRgb(255,255,255))

    imageData = processData(readCSV('test0005.csv'))


    timeOffset = createTimeOffset(imageData, 0.0005, 0.004, 1500)
    createOffsetImage(imageData, timeOffset, "0.0005-1500ms")

def createOffsetImage(processedData, timeOffset, fileName):
    imageHeight = len(processedData[0]) + 1
    #imageWidth= len(processedData[0]) + 1
    imageWidth = len(processedData) + 1
    repeat = (imageHeight / imageWidth) / 10
    #print("should repeat each line ", repeat, " times.")

    #mainImage = QImage(imageHeight,imageWidth, QImage.Format_RGB32)
    mainImage = QImage(imageHeight,imageWidth * repeat, QImage.Format_RGB32)
    print(" image has dimentions: ", mainImage.height(), " x ", mainImage.width())
    mainImage.fill(qRgb(0,0,0))

    x = 1
    y = 1

    for x in range(0,len(processedData)-1, 1):
        for y in range(0,(len(processedData[0]) - max(timeOffset)),1):
            toffset = timeOffset[x]
            dataLine = processedData[x]
            dataPixel = dataLine[y + toffset]
            mainImage.setPixel(QPoint(y,x), int(dataPixel))
    '''
    for line in processedData:
        for pixel in line:
            #print pixel
            mainImage.setPixel(QPoint(x, y), int(pixel))
            x += 1
        x = 1
        y += 1
    '''
    saveImage(mainImage,fileName)


def createImage(processedData):
    imageHeight = len(processedData[0]) + 1
    #imageWidth= len(processedData[0]) + 1
    imageWidth = len(processedData) + 1
    repeat = (imageHeight / imageWidth) / 10
    print("should repeat each line ", repeat, " times.")

    #mainImage = QImage(imageHeight,imageWidth, QImage.Format_RGB32)
    mainImage = QImage(imageHeight,imageWidth * repeat, QImage.Format_RGB32)
    print(" image has dimentions: ", mainImage.height(), " x ", mainImage.width())
    mainImage.fill(qRgb(0,0,0))

    x = 1
    y = 1

    '''
    for line in processedData:
        for pixel in line:
            #print pixel
            mainImage.setPixel(QPoint(x, y), int(pixel))
            x += 1
        x = 1
        y += 1
    '''

    for line in processedData:
        for z in range(1,repeat,1):
            for pixel in line:
                mainImage.setPixel(QPoint(x, y), int(pixel))
                x += 1
            x = 1
            y += 1

    saveImage(mainImage,'test')

def createTimeOffset(imgData, gridStep, sensorDistance, speedOfSound):
    #center of image is located half way through the list
    #time offset is a function of the distance from this halfway point
    # t= V *Lb + ta
    # V = velocity of sound in water (1500 m/s)
    # Lb is the distance from the acoustic source = sqrt( a^2 + x^2 )
    # a is the distance from the acoustic source to the "center sensor"
    # x is the distance from the "center sensor" to each individual sensor (distance between data points = 0.001m)

    center = int(len(imgData) / 2) # a is located at the very center of the image
    print ("center is located at: ", center)
    x_distance = []
    step = gridStep # 0.001 #this is the grid spacing between sensors
    for i in range(1,len(imgData),1):
        x_distance.append(abs(center - i) * step)
    print x_distance

    a_distance = sensorDistance #0.004 # [m] this is the distance from the acoustic source and the center sensor

    Lb = [] #Lb is the length of the line from the acoustic source to each sensor
    for i in range(0, len(imgData)-1,1):
        #print i
        Lb.append( sqrt(a_distance*a_distance + x_distance[i]*x_distance[i]))
    print Lb

    Tb = [] # Tb is the time offset from the acoustic source
    V = speedOfSound #1500  [m/s] V is the velocity of sound in water
    for i in range(0, len(imgData)-1, 1):
        Tb.append(Lb[i]/V)
    print Tb

    '''
    #we dont want to look into the "future" so subtract time for wave to travel from source to very center (center)
    for i in range(0,len(Tb),1):
        Tb[i] = Tb[i] - Tb[center]
    print Tb
    '''

    #now find exactly how many "time steps" in the future these datapoints occur at
    timestep = 2.5e-8
    timeOffset = []
    for i in range(0,len(Tb),1):
        timeOffset.append(int(round(Tb[i]/timestep,0)))
    print timeOffset

    return timeOffset




def processData(imgData):
    mx = findMax(imgData) #super inefficient since we have to scan data twice
    r = []
    image = []
    for row in imgData:
        for item in row:
            r.append(abs((float(item)))/mx * 255) #normalize data then scale to 255
        image.append(r)
        r = []
    print ("image has dimensions", len(image))
    print ("image line has dimensions", len(image[0]))
    return image

def findMax(imData):
    mx = 0
    for row in imData:
        for item in row:
           if float(item) > mx:
               mx = float(item)
    return mx

def readCSV(csvFile):
    line = []

    with open(csvFile, 'rb') as fle:
        print "file open"
        reader = csv.reader(fle)
        i=0
        for row in reader:
            line.append(row)
            #print("data line has size ", len(line))

    #print(line[len(line)-1])
    return line


def saveImage(image, nam):
    name =  nam
    imagefile = QImageWriter()
    imagefile.setFileName(str(name) + ".bmp")
    imagefile.setFormat("BMP")
    imagefile.setQuality(100)
    imagefile.write(image)


main()
