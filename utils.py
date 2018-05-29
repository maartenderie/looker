import cv2


def display(originalImage, remark="", convert=False):
    if remark is not "":
        if convert:
            image = cv2.cvtColor(originalImage, cv2.COLOR_GRAY2BGR)
        else:
            image = originalImage.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, remark, (10, 10), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
        #print "Displaying: {}".format(remark)
    else:
        image = originalImage
    windowName = "image: {}".format( remark )
    cv2.namedWindow(windowName , cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName , 400,750 )
    cv2.moveWindow(windowName , 20,20)
    cv2.imshow( windowName, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def calcHist(img):
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    return cv2.normalize(hist, hist).flatten()


def crop(image, lu, rd):
    h, w = image.shape[:2]
    xMin = max(0, lu[0])
    xMax = min(rd[0], w)
    yMin = max(0, lu[1])
    yMax = min(rd[1], h)
    # print "w{} h{}m xmin{} xmax{} ymin{} ymax{}".format( w,h,xMin , xMax,yMin,yMax )
    result = image[yMin:yMax, xMin:xMax]
    # display( result )
    return result


def displayContoursOnGrey(grayImage, contours):
    colorImage = cv2.cvtColor(grayImage, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        cv2.drawContours(colorImage, [contour], -1, (0, 255, 0), 1)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(colorImage, (x, y), (x + w, y + h), (0, 255, 255), 1)
    display(colorImage)
