import cv2
import os
import utils
from stamp_detector2 import detectCirclesViaFiltered
import masked


def calcHistogram(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist)
    return hist.flatten()


def findBestMatch(histogram, references):
    bestMatch = None
    bestScore = None
    for refName, ref in references.items():
        score = cv2.compareHist(histogram, ref, cv2.HISTCMP_INTERSECT)
        if bestScore is None or score > bestScore:
            bestScore = score
            bestMatch = refName
    roundedScore = round(bestScore, 2)
    return bestMatch, roundedScore if bestMatch is not None else "No match?"


def loadReferenceHistograms():
    references = masked.getImagesFromDirInColor("references")
    return {refName: calcHistogram(refImage)
            for (refName, refImage) in references.items()}


def loadReferenceImages():
    return masked.getImagesFromDirInColor("references")


def extractRoiRectFromStamp(stamp, debug):
    circle = detectCirclesViaFiltered(stamp, 1, debug)[0]
    lu = (circle[0] - circle[2], circle[1] - circle[2])
    rd = (circle[0] + circle[2], circle[1] + circle[2])
    roiRect = utils.crop(stamp, lu, rd)
    if debug: utils.display(roiRect, "rect")
    return roiRect


def loadEggMask():
    return cv2.imread("roi_mask.png", 0)


def applyMask(image, mask, debug):
    h, w = mask.shape[:2]
    image = cv2.resize(image, (w, h))
    print "{} and {}".format(mask.shape[:2], image.shape[:2])
    result = cv2.bitwise_and(image, image, mask=mask)
    if debug: utils.display(result, "masked")
    return result


def extractMaskedRoi(roi, debug):
    eggMask = loadEggMask()
    result = applyMask(roi, eggMask, debug)
    if debug: utils.display(result, "postMask")
    return result


def findBestMatchViaTemplating(maskedRoi, referenceImages):





def detectGymName2( stamp, referenceImages, debug = False):
    roiRect = extractRoiRectFromStamp(stamp, debug)
    maskedRoi = extractMaskedRoi(roiRect, debug)
    gymName, score = findBestMatchViaTemplating( maskedRoi, referenceImages)

    if debug: utils.display(stamp, "{}:{}".format(gymName, score))
    return gymName, score


def detectGymName(stamp, referenceHistos, debug=False):
    roiRect = extractRoiRectFromStamp(stamp, debug)
    maskedRoi = extractMaskedRoi(roiRect, debug)
    histogram = calcHistogram(maskedRoi)
    gymName, score = findBestMatch(histogram, referenceHistos)

    if debug: utils.display(stamp, "{}:{}".format(gymName, score))
    return gymName, score


def extractAddSaveReferences():
    for i in range(0, 32):
        filename = os.path.join("stamps", "stamp{}.png".format(i))
        stamp = masked.readColorImage(filename)
        postMask = extractMaskedRoi(stamp, False)
        outputFilename = os.path.join("references", "reference{}.png".format(i))
        cv2.imwrite(outputFilename, postMask)


def doVisualTest():
    stamp = cv2.imread(os.path.join("stamps", "stamp0.png"))
    referenceMap = loadReferenceHistograms()
    gymName, score = detectGymName(stamp, referenceMap, True)
    print "found gym: {}".format(gymName)


if __name__ == "__main__":
    doVisualTest()
