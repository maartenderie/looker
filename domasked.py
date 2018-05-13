import masked
import utils

images = masked.getMaskedInColor()
for k,v in images.items():
  utils.display( v )
