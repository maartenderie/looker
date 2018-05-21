import cv2
import numpy as np
from utils import display, crop,displayContoursOnGrey
import masked

def getTimeSymbolNames():
  digitSymbolNames = map( lambda x: "{}".format(x) , range(10) )
  otherSymbolNames = ['AM','PM','tilde'] + ['A','P','M']
  return digitSymbolNames + otherSymbolNames

def loadSymbols( debug ):
  symbolNames = getTimeSymbolNames() + ['ongoing','tier']
  
  result = {}
  for symbolName in symbolNames:
    filename = "symbols\{}.png".format( symbolName )
    symbol = cv2.imread( filename , 0 )
    preprocessedSymbol = preprocessSymbol( symbol , debug )
    result[symbolName] = preprocessedSymbol 
  return result

def preprocessSymbol( symbol , debug ):
  return symbol

def fitsIn( symbol, stamp):
  hSym, wSym = symbol.shape[:2]
  hStamp, wStamp = stamp.shape[:2]
  hFits = not hSym > hStamp
  wFits = not wSym > wStamp
  #print "{} {} {} {} {} {}".format( hSym, wSym, hStamp, wStamp , hFits, wFits )
  return hFits and wFits
  
def matchSymbols( stamp , symbols , debug ):
  foundSymbols = {}
  
  method = cv2.TM_CCOEFF_NORMED
  threshold = 0.7
  
  for name,symbol in symbols.items():
    foundSymbols[name] = []
    if fitsIn( symbol, stamp ):
      matched = cv2.matchTemplate( stamp , symbol , method )
      loc = np.where( matched > threshold )
      for match in zip(*loc[::-1]):
        foundSymbols[name].append( match )
    else:
      if debug: print "INFO: {} wont fit".format( name )
  
  #if debug: print "found symbols: {}".format( foundSymbols )
  return foundSymbols

def displaySymbolsFound( stamp , symbolsFound ):
  copyImage = stamp.copy()
  for symbolName, locations in symbolsFound.items():
    for location in locations:
      font = cv2.FONT_HERSHEY_SIMPLEX
      cv2.putText(copyImage,symbolName, location , font, 1,(0,0,255),1,cv2.LINE_AA)
  display( copyImage ,"w sym" )

def scaleStamp( stamp , debug ):
  desiredWidth = 265
  desiredHeight = 409
  return cv2.resize( stamp , (desiredWidth,desiredHeight))
  
def cropYRegion( stamp , yMin, yMax):
  h,w = stamp.shape[:2]
  return stamp[ yMin:yMax, 0:h ]

def detectTier( stamp , tierSymbol, debug ):
  tierRegion = cropYRegion( stamp , 345, 400)
  ret, threshold = cv2.threshold( tierRegion , 220, 255, 0)
  threshold = cv2.bitwise_not(threshold)
  contourImage, contours, hierarchy = cv2.findContours( threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
  
  if debug: displayContoursOnGrey( contourImage, contours )
  tierLvl = sum( cv2.contourArea( x ) > 500 for x in contours )
  return tierLvl

def determineSymbolOccurence( image , symbol,debug ):
  symbolMap = {'someName':symbol}
  symbolsFound = matchSymbols( image , symbolMap, debug )
  return len(symbolsFound['someName'])
  
def detectTime( scaledBwStamp , symbols, debug ):
  timeRegion = cropYRegion( scaledBwStamp , 275, 355 )
  nrOngoingFound = determineSymbolOccurence( timeRegion , symbols['ongoing'], debug )
  #display( timeRegion, 'time {}'.format(nrOngoingFound) )
  if nrOngoingFound > 0:
    return 'ongoing'
  else:
    return detectTimeViaSegmentation( timeRegion , symbols, debug  )

def mostFrequentSymbol( foundSymbols ):
  bestSymbol = None
  bestCount = 0
  for name , locations in foundSymbols.items():
    bestSymbol = name if len(locations) > bestCount else bestSymbol
    bestCount = max( bestCount , len(locations ))
  return bestSymbol , bestCount

def removeContoursEncapsulatedByContours( contours, debug ):
  result = []
  for i in range( 0, len(contours) ):
    x,y,w,h = cv2.boundingRect( contours[i] )
    encapsulated = False
    for j in range( 0, len(contours) ):
      #print "{},{}".format( cv2.boundingRect( contours[i] ), cv2.boundingRect( contours[j] ) )
      if i is j: continue
      if encapsulated: continue
      x2,y2,w2,h2 = cv2.boundingRect( contours[j] )
      xEncap = x > x2 and x+w < x2+w2
      yEncap = y > y2 and y+h < y2+h2
      encapsulated = xEncap and yEncap
      if debug and encapsulated:
        print "{},{}".format( cv2.boundingRect( contours[i] ), cv2.boundingRect( contours[j] ) )
    if not encapsulated: result.append( contours[i] )
    #print "before {}, after {}".format( len(contours), len(result) )
  return result
  
def detectTimeViaSegmentation( timeRegion , symbols, debug  ):
  ret, threshold = cv2.threshold( timeRegion , 190, 255, 0)
  threshold = cv2.bitwise_not(threshold)
  contourImage, contours, hierarchy = cv2.findContours( threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
  
  digitSymbolNames = ['A','P','M'] + map( lambda x: "{}".format(x) , range(10) )
  digitMap = {key: symbols.get(key) for key in digitSymbolNames }
  
  largeContours = [ x for x in contours if cv2.contourArea( x ) > 100 ]
  largeContours = removeContoursEncapsulatedByContours( largeContours, debug )
  if debug: displayContoursOnGrey( contourImage, largeContours )
  
  hits = []
  for largeContour in largeContours:
    margin = 5
    x,y,w,h = cv2.boundingRect( largeContour )  
    lu = (x - margin, y - margin)
    rd = (x + w + margin, y + h + margin)
    charCrop = crop( timeRegion , lu, rd )
    foundSymbols = matchSymbols( charCrop , digitMap , debug )
    #print "{}".format(foundSymbols)
    #display( charCrop )
    symbol , count = mostFrequentSymbol( foundSymbols )
    hits.append( (symbol , lu) )
  
  hits.sort( key=lambda hit: hit[1][0] ) #sort by x
  if debug: print "sorted hits: {}".format( hits )
  result = ''.join( [hit[0] for hit in hits] )
  return result
  
# PUBLICS
def extractTexts( stamp , debug = False ):
  symbols = loadSymbols( debug )
  if debug: display( stamp, "extractTexts input")
  bwStamp = cv2.cvtColor( stamp , cv2.COLOR_BGR2GRAY )
  scaledBwStamp = scaleStamp( bwStamp , debug )  
  tier = detectTier( scaledBwStamp , symbols['tier'], debug )
  time = detectTime( scaledBwStamp , symbols , debug )
  
  if debug: display( scaledBwStamp , "lvl{}@{}".format(tier,time) )
  return tier,time

def doVisualTest():
  for i in range(0,30):
    filename = "stamps\stamp{}.png".format( i )
    print "testing text extractor for {}".format( filename )
    stamp = masked.readColorImage( filename )
    extractTexts( stamp , debug = True )
  
if __name__ == "__main__":
  doVisualTest()