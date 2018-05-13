import cv2
import masked,utils
import numpy as np

def removeEmptyStamp( images ):
  emptyStamp = masked.readColorImage( "images/stampempty.png" )
  emptyHist = utils.calcHist( emptyStamp )
  for k,v in images.items():
    hist = utils.calcHist( v )
    emptynessScore = cv2.compareHist( emptyHist, hist , cv2.HISTCMP_INTERSECT )
    if( emptynessScore > 1.1 ):
      del images[k]

def writeImagesInMap( images ):      
  for key,value in images.iteritems():
    cv2.imwrite( key , value )

def calcHistograms( images ):
  result = {}
  for key,value in images.iteritems():
    hist = cv2.calcHist( [value] ,[0,1,2] , None ,[8,8,8],[0,256,0,256,0,256] )
    hist = cv2.normalize(hist,hist)
    hist = hist.flatten()
    result[key] = hist
  return result

def findBestMatch( name , image , references ):
  bestMatch = None
  bestScore = None
  for refName , ref in references.items():
    score = cv2.compareHist( image , ref , cv2.HISTCMP_INTERSECT)
    if( bestScore is None or score > bestScore ):
      bestScore = score
      bestMatch = refName 
  return bestMatch if bestMatch is not None else "No match?"

def writeResult( name , image , replace , replacement , text ):
  filename = name.replace( replace , replacement )
  cv2.putText( image, text, ( 0,12 ), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1 , cv2.LINE_AA )
  cv2.imwrite( filename , image )

images = masked.getMaskedInColor()
removeEmptyStamp(images)
writeImagesInMap( images )

references = masked.getImagesFromDirInColor("references")
referenceHistograms = calcHistograms(references)

histograms = calcHistograms( images )
compMethod = cv2.HISTCMP_INTERSECT
hits = {}

for name,image in histograms.items():
  bestMatchName = findBestMatch( name , image , referenceHistograms )
  print "Image {} best matches {}".format( name , bestMatchName )
  writeResult( name , images[name] , "filtered" , "results" , bestMatchName )

#for name, image in images.items():
#  print "comparing for {}".format( name )
#  currHist = histograms[name]
#  
#  for k, hist in histograms.items():
#    distance = cv2.compareHist( currHist, hist , compMethod)
#    hits["{}-{}".format(name,k)] = distance
#    if( distance > 1.0):
#      print "{}-{} : {}".format(name,k, distance )

