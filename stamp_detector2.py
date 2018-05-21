import cv2
import utils, masked
import numpy as np


# Extracts stamps using contours and refines these using filtering by color

# SOURCES
# Contours: https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
# Circles: https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/

# PRIVATES
def fallsWithAllowedRadius(image, r):
    return 50 < r < 125


def detectCirclesViaContours(colorImage, debug):
    contourImage = getContourImage(colorImage, debug)
    return detectHoughCircles(contourImage, debug)


def detectHoughCircles(im2, debug, ratioHG=1.2):
    circles = cv2.HoughCircles(im2, cv2.HOUGH_GRADIENT, ratioHG, 100.)
    circles = [] if circles is None else np.round(circles[0, :]).astype("int")
    if debug: print "all circles found: {}".format(circles)
    # min-max radius on cv2.HoughCircles != working :(
    result = []
    for (x, y, r) in circles:
        if fallsWithAllowedRadius(im2, r):
            result.append((x, y, r))
    return result


def getContourImage(colorImage, debug):
    img_gray = cv2.cvtColor(colorImage, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img_gray, 240, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    im2 = cv2.bitwise_not(im2)
    if debug: utils.display(im2, "contours", False)
    return im2


def detectCirclesViaFiltered(colorImage, expectedNrCircles, debug):
    lower = np.array([140, 160, 220], dtype="uint8")  # BGR
    upper = np.array([200, 220, 255], dtype="uint8")

    filtered = cv2.inRange(colorImage, lower, upper)
    print "filtered"
    if debug: utils.display(filtered, "filtered")

    kernel = np.ones((5, 5), np.uint8)
    filtered = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, kernel, iterations=3)
    if debug: utils.display(filtered, "MORPH_CLOSE")

    ret, thresh = cv2.threshold(filtered, 254, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    getArcLength = lambda x: cv2.arcLength(x, closed=True)
    contours.sort(key=getArcLength, reverse=True)

    result = []
    for contour in contours[0:expectedNrCircles]:
        x, y, w, h = cv2.boundingRect(contour)
        r = int(max(w, h) / 2.0)
        if fallsWithAllowedRadius(colorImage, r):
            cv2.rectangle(colorImage, (x, y), (x + w, y + h), (255, 0, 0), 3)
            xcenter = x + r
            ycenter = y + r
            result.append([xcenter, ycenter, r])
        else:
            print "Warning: found contour with unallowed radius. Ignoring"
            cv2.rectangle(colorImage, (x, y), (x + w, y + h), (0, 0, 255), 3)

    # if debug: utils.display( colorImage )
    if debug: print "circlesViaFiltered: {}".format(result)
    return result


def extractStampLocationsFromCircles(circles, margin):
    result = []
    for (x, y, r) in circles:
        absoluteMargin = int(r * margin)
        downMargin = int(1.3 * r)  # for the raid time etc.
        lu = (x - r - absoluteMargin, y - r - absoluteMargin)
        rd = (x + r + absoluteMargin, y + r + absoluteMargin + downMargin)
        result.append((lu, rd))
    return result


def extractStamps(image, stampLocations):
    result = []
    for rect in stampLocations:
        lu = rect[0]
        rd = rect[1]
        result.append(utils.crop(image, lu, rd))
    return result


def displayStamps(image, stampLocations):
    img = image.copy()
    drawStamps(img, stampLocations)
    utils.display(img)


def drawStamps(image, stampLocations):
    color = (255, 0, 0)  # blue
    for location in stampLocations:
        cv2.rectangle(image, location[0], location[1], color, 2)
    return image


def displayCircles(image, circles):
    copyImage = image.copy()
    drawCircles(copyImage, circles)
    utils.display(copyImage)


def drawCircles(image, circles):
    color = (0, 255, 0)  # green
    if circles is None or len(circles) is 0: return
    for (x, y, r) in circles:
        cv2.circle(image, (x, y), r, color, 3)
    return image


def refineStamp(roughStamp, debug):
    lower = np.array([120, 140, 220], dtype="uint8")  # BGR
    upper = np.array([220, 240, 255], dtype="uint8")

    filtered = cv2.inRange(roughStamp, lower, upper)
    if debug: utils.display(filtered, "filtered")

    ret, thresh = cv2.threshold(filtered, 240, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    getArcLength = lambda cntr: cv2.arcLength(cntr, closed=True)
    contour = max(contours, key=getArcLength)
    x, y, w, h = cv2.boundingRect(contour)

    r = int(max(w, h) / 2.0)

    if not fallsWithAllowedRadius(roughStamp, r):
        print "Warning: found contour with unallowed radius. Ignoring"
        cv2.rectangle(roughStamp, (x, y), (x + w, y + h), (0, 0, 255), 3)
        return None

    circles = [[x + r, y + r, r]]
    if debug: displayCircles(roughStamp, circles)

    if debug: utils.display(roughStamp, "pre extraction", False)

    stampLocations = extractStampLocationsFromCircles(circles, margin=0.18)
    if debug: displayStamps(roughStamp, stampLocations)
    refinedStamps = extractStamps(roughStamp, stampLocations)

    stampFound = len(refinedStamps) is 1
    if debug and stampFound: utils.display(refinedStamps[0], "refined")
    return refinedStamps[0] if stampFound else None


def refineStamp2(roughStamp, debug):
    roughStampGrey = cv2.cvtColor(roughStamp, cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(roughStampGrey, 240, 255, 0)
    contourImage, contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contourImage = cv2.bitwise_not(contourImage)
    if debug: utils.display(contourImage)
    circles = detectHoughCircles(contourImage, debug, 1.3)
    if debug: displayCircles(roughStamp, circles)

    return contourImage


# PUBLICS

# Returns, from an image, an array of all found stamps in a colorImage
def detectStamps(colorImage, debug=False):
    if colorImage is None:
        print "WARN: got None @ detectStamps! Returning []."
        return []

    circlesViaContours = detectCirclesViaContours(colorImage, debug)
    if debug: displayCircles(colorImage, circlesViaContours)

    roughStampLocations = extractStampLocationsFromCircles(
        circlesViaContours, 1.0)
    roughStamps = extractStamps(colorImage, roughStampLocations)

    refinedStamps = []
    for roughStamp in roughStamps:
        if debug: utils.display(roughStamp, "roughStamp_i")

        refinedStamp = refineStamp(roughStamp, debug)
        if refinedStamp is not None:
            refinedStamps.append(refinedStamp)

    return refinedStamps


def visualTest():
    writeStamps = True
    stampNr = 0

    for i in range(5, 6):
        colorImage = masked.readColorImage("images/gym{}.png".format(i))
        stamps = detectStamps(colorImage, debug=True)
        if writeStamps:
            for stamp in stamps:
                cv2.imwrite("stamps/stamp{}.png".format(stampNr), stamp)
                stampNr = stampNr + 1


if __name__ == "__main__":
    visualTest()
