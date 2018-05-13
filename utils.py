import cv2

def display( img ):
  cv2.namedWindow( 'image' , cv2.WINDOW_NORMAL)
  cv2.imshow('image',img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def calcHist( img ):
  hist = cv2.calcHist( [img] ,[0,1,2] , None ,[8,8,8],[0,256,0,256,0,256] )
  return cv2.normalize(hist,hist).flatten()