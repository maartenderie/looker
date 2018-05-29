import stamp_detector2 as stamp_detector
import text_extractor
import cv2
import utils
import os
import hist2 as hist

i = 0
debugStamps = False
debugText = False
debugGym = False

for imageNr in range(1, 10):
    dirname = "images"
    filename = os.path.join(dirname , "gym{}.png".format(imageNr) )
    print "= = =  parsing {}  = = =".format(filename)
    image = cv2.imread(filename)
    stamps = stamp_detector.detectStamps(image, debugStamps)

    print "got {} stamps".format(len(stamps))
    textOffsetY = 100

    referenceGyms = hist.loadReferenceHistograms()

    stampNr = 0

    h,w = image.shape[:2]
    image = cv2.resize(image, (2*w, 2*h))

    for stamp in stamps:
        if debugStamps: utils.display(stamp, "stamp{}".format(stampNr))
        tier, time = text_extractor.extractTexts(stamp, debugText)
        gymName,score = hist.detectGymName(stamp , referenceGyms , debugGym )
        gymName = gymName.replace("references", "" , 1 )
        gymName = gymName.replace(".png", "")

        textFound = "T{}.{}.{}:{}".format(tier, time, gymName, score)
        textLocation = (textOffsetY, textOffsetY + stampNr * textOffsetY)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, textFound, textLocation, font, 3, (0, 0, 255), 7, cv2.LINE_AA)

        stampNr = stampNr + 1
    print "displaying {}".format(filename)

    utils.display(image)
