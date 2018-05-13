import utils
import stamp_detector
import masked

class Raid:
  def __init__(self , egg , id ):
    self.egg = egg
    self.id = id
  def isEgg( self ):
    return egg
  def getId( self ):
    return id
  def toString(self):
    idString = "unknownId" if id is None else "{}".format(id)
    eggString = "egg={}".format( self.isEgg() )
    return "{} // {}".format( idString , eggString )

# PUBLICS
def detectRaid( stamp , debug = False ):
  resizedStamp = resizeStamp( stamp )
  
  eggArea = extractEggArea( resizedStamp )
  if debug: utils.display( eggArea )
  
  
  raid = determineRaid( eggArea , resizedStamp , debug )
  

if __name__ == "__main__":
  for i in range(1,2):
    colorImage = masked.readColorImage( "images/gym{}.png".format(i) )
    stamps = stamp_detectordetectStamps( colorImage , False )
    for stamp in stamps:
      raid = detectRaid( stamp , True )