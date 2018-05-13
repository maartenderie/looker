import cv2
import utils

def getMasked():
  filtered = {}
  
  for i in range(1,7):
    src = readColorImage("images/gym{}.png".format(i))
        
    for j in range(1,7):
      mask = readColorImage( "images/mask{}.bmp".format(j))
      mask = cv2.bitwise_not( mask )
      fil = cv2.bitwise_and( mask , src )
      
      name = "masked{}-{}".format(i,j)
      filtered[name] = fil
  return filtered
  
def readColorImage( filename ):
  return cv2.imread(filename , cv2.IMREAD_COLOR)
  #return cv2.cvtColor( src , cv2.COLOR_BGR2RGB )

def readBWImage( filename ):
  return cv2.imread(filename,0)

def getImagesFromDirInColor( directory ):
  import os
  result = {}
  for filename in os.listdir(directory):
    path = os.path.join(directory,filename)
    result[path] = readColorImage( path )
  return result

def getMaskedInColor():
  filtered = {}
  
  mask = readColorImage("images/stampmask.png" )
  
  nr = 0
  for i in range(1,7):
    src = readColorImage("images/gym{}.png".format(i))  
    for xrange in [(120,350),(435,665),(755,985)]:
      for yrange in [(740,1125),(1200,1585)]:
        cropped = src[ yrange[0]:yrange[1],xrange[0]:xrange[1] ]
        #utils.display(cropped)
        masked = cv2.bitwise_and( mask , cropped )
        filtered["filtered/{}.png".format(nr)] = masked
        nr = nr+1
  return filtered