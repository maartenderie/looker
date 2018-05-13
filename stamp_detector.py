import cv2
import utils,masked
import numpy as np

# SOURCES
# Contours: https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
# Circles: https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/

# PRIVATES
def fallsWithAllowedRadius( image, r ):
  return r > 50 and r < 125

def detectCirclesViaContours( colorImage , debug ):
  #im2 = getColorFilteredImage( colorImage , debug )
  im2 = getContourImage( colorImage , debug )
  
  circles = cv2.HoughCircles( im2 , cv2.HOUGH_GRADIENT , 1.2 , 100. )
  circles = [] if circles is None else np.round( circles[0,:]).astype("int")
  if debug: print circles
  
  #min-max radius on cv2.HoughCircles != working :(
  result = []
  for (x,y,r) in circles:
    if( fallsWithAllowedRadius( colorImage , r ) ):
      result.append((x,y,r))
  if debug: print "Result detectCirclesViaContours: {}".format( result )
  return result

def getContourImage( colorImage , debug ):
  img_gray = cv2.cvtColor(colorImage, cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold( img_gray , 240, 255, 0 )
  im2, contours , hierarchy = cv2.findContours( thresh , cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
  im2 = cv2.bitwise_not(im2)
  #if debug: utils.display(im2)
  return im2

def detectCirclesViaFiltered( colorImage , expectedNrCircles, debug ):
  lower = np.array([140,160,220], dtype = "uint8" ) #BGR
  upper = np.array([180,220,255], dtype = "uint8" )
  
  filtered = cv2.inRange( colorImage, lower, upper )
  if debug: utils.display( filtered )
  
  ret, thresh = cv2.threshold( filtered , 254, 255, 0 )
  im2, contours , hierarchy = cv2.findContours( thresh , cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
  contours.sort( key = cv2.contourArea, reverse = True )
  
  result = []
  for contour in contours[0:expectedNrCircles]:
    x,y,w,h = cv2.boundingRect(contour)
    r = int(max( w,h )/2.0)
    if( fallsWithAllowedRadius( colorImage , r ) ):
      cv2.rectangle( colorImage , (x,y) , (x+w,y+h) , (255,0,0) , 3 )
      xcenter = x + r
      ycenter = y + r
      result.append( [ xcenter, ycenter , r ] )
    else:
      print "Warning: found contour with unallowed radius. Ignoring"
      cv2.rectangle( colorImage , (x,y) , (x+w,y+h) , (0,0,255) , 3 )
  
  #if debug: utils.display( colorImage )
  if debug: print "circlesViaFiltered: {}".format( result )
  return result
  
def extractStampLocationsFromCircles( circles ):
  result = []
  for (x,y,r) in circles:
    margin = int( r*0.22 )
    downMargin = int(1.3*r) # for the raid time etc.
    lu = ( x-r-margin , y-r-margin )
    rd = ( x+r+margin , y+r+margin+downMargin )
    result.append( (lu,rd) )
  return result

def extractStamps( image , stampLocations ):
  result = []
  for rect in stampLocations:
    lu = rect[0]
    rd = rect[1]
    cropped = image[ lu[1]:rd[1],lu[0]:rd[0] ]
    result.append(cropped)
  return result

def drawStamps( image , stampLocations ):
  color = (255,0,0) # blue
  for location in stampLocations:
    cv2.rectangle( image , location[0] , location[1] , color , 3 )
  return image

def drawCircles( image , circles ):
  color = (0,255,0) # green
  for (x,y,r) in circles:
      cv2.circle( image , (x,y) , r , color , 3 )
  return image

# PUBLICS

# Returns, from an image, an array of all found stamps in a colorImage
def detectStamps( colorImage , debug = False ):
  original = colorImage.copy() # bcs drawing on colorImage
  
  # circle detection from contours is robust, but the quality
  # of the circles is lower than circle detection via color filtering.
  # This is why these are combined
  circlesViaContours = detectCirclesViaContours( colorImage , debug )
  nrExpectedCircles = len( circlesViaContours )
  if debug: print "expected #circles: {}".format( nrExpectedCircles )
  
  circles = detectCirclesViaFiltered( colorImage, nrExpectedCircles , debug )
  if debug : drawCircles( colorImage , circles )
  
  stampLocations = extractStampLocationsFromCircles( circles )
  print "found {} stamps".format( len(stampLocations ) )
  if debug: utils.display( drawStamps( colorImage , stampLocations ) )
  
  stamps = extractStamps( original , stampLocations )
  return stamps

if __name__ == "__main__":
  writeStamps = True
  
  # visual testing
  stampNr = 0
  
  for i in range(2,3):
    colorImage = masked.readColorImage( "images/gym{}.png".format(i) )
    stamps = detectStamps( colorImage , debug = True )
    if writeStamps :
      for stamp in stamps:
        cv2.imwrite( "stamps/stamp{}.png".format( stampNr ) , stamp )
        stampNr = stampNr + 1
  
  for i in range(8,10):
    colorImage = masked.readColorImage( "images/gym{}.jpg".format(i) )
    stamps = detectStamps( colorImage , debug = True )
    if writeStamps :
      for stamp in stamps:
        cv2.imwrite( "stamps/stamp{}.png".format( stampNr ) , stamp )
        stampNr = stampNr + 1