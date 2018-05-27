import cv2
import os
import utils
from stamp_detector2 import detectCirclesViaFiltered


def writeImagesInMap(images):
    for key, value in images.iteritems():
        cv2.imwrite(key, value)


def calcHistograms(images):
    result = {}
    for key, image in images.iteritems():
        hist = calcHistogram(image)
        result[key] = hist
    return result


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
    return bestMatch if bestMatch is not None else "No match?"


def loadReferenceGyms():
    result = {}
    # TODO {name:histogram}
    return result


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


def detectGymName(stamp, referenceGyms, debug=False):
    roi = extractRoiRectFromStamp(stamp, debug)
    cv2.imwrite("someRoi.png", roi)

    eggMask = loadEggMask()
    if debug: utils.display(eggMask, "mask")
    filteredRoi = applyMask(roi, eggMask, debug)
    exit(0)
    histogram = calcHistogram(filteredRoi)
    gymName = findBestMatch(histogram, referenceGyms)
    if debug: utils.display(stamp, gymName)


def doVisualTest():  # TODO old remove?
    stamp = cv2.imread(os.path.join("stamps", "stamp0.png"))
    detectGymName(stamp, {}, True)


if __name__ == "__main__":
    doVisualTest()
