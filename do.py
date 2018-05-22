import stamp_detector2 as stamp_detector
import text_extractor
import cv2
import utils
import os

i = 0
debugStamps = False
debugText = False

for imageNr in range(1, 10):
    dirname = "images"
    filename = os.path.join(dirname , "gym{}.png".format(imageNr) )
    print "= = =  parsing {}  = = =".format(filename)
    image = cv2.imread(filename)
    stamps = stamp_detector.detectStamps(image, debugStamps)

    print "got {} stamps".format(len(stamps))
    textOffsetY = 60

    stampNr = 0
    for stamp in stamps:
        if debugStamps: utils.display(stamp, "stamp{}".format(stampNr))
        tier, time = text_extractor.extractTexts(stamp, debugText)
        textFound = "tier{}//{}".format(tier, time)
        textLocation = (textOffsetY, textOffsetY + stampNr * textOffsetY)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, textFound, textLocation, font, 2, (0, 0, 255), 2, cv2.LINE_AA)

        stampNr = stampNr + 1
    print "displaying {}".format(filename)
    utils.display(image)
