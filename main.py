import cv2
import numpy as np
import masked
import utils

def test():
  img = cv2.imread('images/gym2.png',0)
  utils.display( img )
  mask = cv2.imread('images/mask1.bmp',0)
  utils.display( mask )

  invmask = cv2.bitwise_not(mask)
  utils.display( invmask )

  onlygym = cv2.bitwise_and( invmask , img )
  utils.display( onlygym )

siftCollection = []
images = ['gym1.png','gym2.png','gym3.png','gym4.png']

#for all images
  #for all masks

filtered = masked.getMasked()

#for i in range(1,5):
#  src = cv2.imread("images/gym{}.png".format(i),0)
#  
#  for j in range(1,7):
#    mask = cv2.imread( "images/mask{}.bmp".format(j) , 0 )
#    mask = cv2.bitwise_not( mask )
#    fil = cv2.bitwise_and( mask , src )
#    filtered.append( fil )

for key,value in filtered.iteritems():
  utils.display( value )

sift  = cv2.xfeatures2d.SIFT_create()
#keypoints = {}
desses = {}
for fil in filtered:
  kp , des = sift.detectAndCompute( fil , None )
  if len(kp) > 50:    
    #outname = "filtered/fil{}-{}.png".format(i,j)
    #cv2.imwrite( outname ,fil )
    #keypoints[fil] = kp
    desses[fil] = des
    #siftcollection[fil] = (kp,des)

bf = cv2.BFMatcher()

for fil in filtered:
  kp , des = siftcollection[fil]
  
  


