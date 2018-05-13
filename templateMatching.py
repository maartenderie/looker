import cv2
import utils,masked
import numpy as np

image = masked.readColorImage( "images/gym2.png" )
img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold( img_gray , 240, 255, 0 )
im2, contours , hierarchy = cv2.findContours( thresh , cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
utils.display( im2 )


circles = cv2.HoughCircles( im2 , cv2.HOUGH_GRADIENT , 1.2 , 100 )
print circles

if circles is not None :
  circles = np.round( circles[0,:]).astype("int")
  for (x,y,r) in circles:
    cv2.circle( image , (x,y) , r , (255,0,0) , 2 )
else:
  print "srry no circles"

utils.display( image)
exit(0)

template = cv2.imread("circle/fullCircle.png", 0)
mask = cv2.imread("circle/mask.png", 0)
template = cv2.bitwise_and( template , mask )
utils.display( template )


w, h = template.shape[::-1]

methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
maxMethods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED' ]

for method in maxMethods :
  res = cv2.matchTemplate(im2,template,eval(method))
  
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
  cv2.rectangle(image, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,0,255), 2)
  
  utils.display(res)
  #threshold = 0.5
  #loc = np.where( res >= threshold)
  #for pt in zip(*loc[::-1]):
  #    cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

  #cv2.imwrite('res.png',img_rgb)
  utils.display( image )