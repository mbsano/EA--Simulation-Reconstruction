__author__ = 'Mike'

import os,sys
from PyQt4.QtGui import QDialog, QBitmap, QImage, QPixmap, QImageWriter, QImageReader, qRgb
import csv
from PyQt4.Qt import QPoint, QColor
from math import sqrt, atan2, pi, sin, cos


def main():
    print "running program"

    #screenwidth =2800 #5120
    #screenheight = 1800 #2880
    #mainImage = QImage(screenwidth, screenheight, QImage.Format_RGB32)
    #mainImage.fill(qRgb(255,255,255))

    #imageData = processData(readCSV('250ns 1000V pulse monopolar electrode - 100 pt arc -2.csv'))

    '''
                #createTimeOffset(imgData, gridStep, sensorDistance, speedOfSound)
    timeOffset = createTimeOffset(imageData, 0.0005, 0.04, 1500)

    #createImage(imageData, 'yolo_test -5') #create an unmanipulated version just for kicks
    #createOffsetImage(imageData, timeOffset, "250ns 1000V pulse 0.0005m grid -monopolar electrode - 1500ms -7")
    downsample = downSampleImage(imageData, timeOffset)

    #need to correct time offset for downsampled data
    dsOffset = []
    for i in range(0,len(timeOffset),1):
        dsOffset.append(timeOffset[i]/10)
    createOffsetImage(downsample, dsOffset, "250ns 1000V pulse 0.0005m grid -monopolar electrode - 1500ms - ds- 9")
    '''


    radImageData = processRadialData(readCSV('2500ns 1000V pulse monopolar electrode - 1000 pt arc.csv'))
    # data now has form [angle, t=0, t=0+...]
    averageNumber = 2
    downSampleRadData = downSampleImage(radImageData, averageNumber)
    sensorDistance = 0.04 #[m]
    speedOfSound = 1500 #[m/s]
    timeOffset = sensorDistance / speedOfSound #[s]
    timeStep = 2.5e-8 #[s], i know this from the simulation output
    pixelSteps = timeOffset / timeStep
    downsampledOffset = 0# int(pixelSteps / averageNumber)

    createRadialImage(downSampleRadData,downsampledOffset, "2500ns 1000V pulse monopolar electrode - 1000 pt arc2")

def createRadialImage(data, timeOffset, filename):
    height = 2*len(data)
    width = 2*len(data[0])
    mx = max(height, width)
    xZero = width/2
    yZero = height
    mainImage = QImage(mx, mx, QImage.Format_RGB32) #create a square image
    mainImage.fill(qRgb(0,0,0))

    for line in data:
        for px in range(timeOffset, len(line), 1):
            theta = line[0]
            #print ("heyo theta: ", theta)
            x = ((px-timeOffset) * sin(theta))
            y = ((px-timeOffset) * cos(theta))
            if x+xZero >=0 and y+xZero >=0 and theta>0:
                pixel = int(line[px])
                mainImage.setPixel(QPoint(x+xZero, y+xZero), qRgb(pixel,pixel,pixel))

    saveImage(mainImage,filename)

def downSampleImage(imagedata, averagenumber):
    #first we need to downsampl the data to make it more manageable (16383x16383 = 268MP)
    sampleNumber = averagenumber
    downsample = []
    total = 0
    sampleLength = len(imagedata[0])
    for j in range(0, len(imagedata), 1):
        linesample = []
        linesample.append(imagedata[j][0]) #keep the first value (the angle)
        for i in range(1, sampleLength,1):
            #print ("the remainder is: ", divmod(i, sampleNumber)[1])

            if (divmod(i,sampleNumber)[1] == 0):
                average = total / sampleNumber
                linesample.append(average)
                total = 0
            else:
                total = total + imagedata[j][i]
        #print ("latest linesample is: ", linesample)
        downsample.append(linesample)
    print ("the downsample has dimensions of: ",  len(downsample[0]))
    return downsample

def createOffsetImage(processedData, timeOffset, fileName):
    imageHeight = len(processedData[0]) + 1
    #imageWidth= len(processedData[0]) + 1
    imageWidth = len(processedData) + 1
    repeat = (imageHeight / imageWidth) / 10
    repeatedImageWidth = imageWidth * repeat
    print("offset image should repeat each line ", repeat, " times.")

    #mainImage = QImage(imageHeight,imageWidth, QImage.Format_RGB32)
    mainImage = QImage(imageHeight, repeatedImageWidth , QImage.Format_RGB32)
    print("offset image has dimentions: ", mainImage.height(), " x ", mainImage.width())
    mainImage.fill(qRgb(0,0,0))

    x = 1
    y = 1

    for x in range(0,len(processedData)-1, 1):
        offset = repeat*x
        #print( "Repeating x value is: " + str(x)  + " and repeating: "  + str(repeat) + " times and offset is:" + str(offset))
        if offset <= repeatedImageWidth: #basically ignore any stretched data that is outside the image frame
            for y in range(0,(len(processedData[0]) - max(timeOffset)),1):
                for delta in range(offset, (offset+repeat), 1): #this just repeats the data to stretch the image
                    #print ("delta is: ", delta , " and offset is: ", offset, " for x = ", x)
                    toffset = timeOffset[x]
                    dataLine = processedData[x]
                    dataPixel = dataLine[y + toffset]
                    mainImage.setPixel(QPoint(y,delta), int(dataPixel))
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


def createImage(processedData, filename):
    imageHeight = len(processedData[0]) + 1
    #imageWidth= len(processedData[0]) + 1
    imageWidth = len(processedData) + 1
    repeat = (imageHeight / imageWidth) / 10
    print("should repeat each line ", repeat, " times.")

    #mainImage = QImage(imageHeight,imageWidth, QImage.Format_RGB32)
    mainImage = QImage(imageHeight,imageWidth * repeat, QImage.Format_RGB32)
    print(" image has dimentions: ", mainImage.height(), " x ", mainImage.width())
    #mainImage.fill(qRgb(0,0,0))

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

    saveImage(mainImage,filename)

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

    print ("non adjusted timeoffset is: ", timeOffset)

    #we dont want to look into the future, so subtract the offset from the source to the very center
    adjustedTimeOffset = []
    for i in range(0, len(timeOffset),1):
        adjustedTimeOffset.append(timeOffset[i] - timeOffset[center])
    print ("adjusted timeoffset is: ", adjustedTimeOffset)

    return adjustedTimeOffset


def processRadialData(imgData):
    #takes data [x, y, t=0, t=0+...] from file and returns [angle, t=0, t=0+....]
    mx = findMax(imgData) #super inefficient since we have to scan data twice
    r = []
    image = []
    for row in imgData:
        #find the angle for each row
        x = float(row[0])
        y = float(row[1])
        angle = atan2(y,x)
        #print ("data has angle: ", angle)
        #append the angle to the data
        r.append(angle)

        for i, item in enumerate(row): #ignore old x and y coords
            if i > 1:
                r.append(((float(item)))/mx * (25/2)) #normalize data then scale to 255
                #r.append(abs((float(item)))/mx * 255) #normalize data then scale to 255

        image.append(r)
        r = []

    return image

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
            #print ("item: " + item)
            if abs(float(item)) > mx:
                mx = abs(float(item))
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
