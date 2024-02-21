import PIL
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
import re
import cv2
from App.Components.urlRegex import uri_pattern

def parseSingleQR(file : Path) -> (str, bool) or (list, bool):
    """ based on a file, determine if whether the file contains a valid QR Code 
        and return the corresponding URL, if any, defanged. """
    
    print(uri_pattern)
    try:
        fileExif = decode(Image.open(file))
    except PIL.UnidentifiedImageError:
        return "File supplied is not a valid image or QR Code.", False
    else:
        # print(fileExif)
        if fileExif == []:
            img = cv2.imread(str(file.resolve()))
            opencvQRDetect = cv2.QRCodeDetector()
            retVal, decodedInfo, _ , _ = opencvQRDetect.detectAndDecodeMulti(img)

            # QR Code not present in image
            if not retVal:
                # print('cv2 decoded: ', retVal, decodedInfo)
                return "File either is not or does not contain valid a QR Code.", False
            else:
                # print('cv2 decoded: ', retVal, decodedInfo[0])
                if re.match(uri_pattern, decodedInfo[0]): # not sure, may need to change index
                    return defangURL(decodedInfo[0]), True
                return "No url detected in QR Code.", False

        # multiple QR codes in single image
        if len(fileExif) > 1:
            rawDataList = []
            for itr in range(len(fileExif)):
                if fileExif[itr].data and fileExif[itr].type == "QRCODE":
                    rawData = fileExif[itr].data.decode()
                    if re.match(uri_pattern, rawData):
                        rawDataList.append(defangURL(rawData))
            if rawDataList != []:
                return rawDataList, True

         # check type of image and if data field exists
        elif fileExif[0].type == "QRCODE" and fileExif[0].data:
            rawData = fileExif[0].data.decode()
            if re.match(uri_pattern, rawData):
                return defangURL(rawData), True
            return "No url detected in QR Code.", False
        return "File either is not or does not contain valid a QR Code.", False
    

# utility function
def defangURL(rawUrl : str) -> str: 
    """
    defangs a URL based on an input string (assumes the string is a URL itself)
    """
    return rawUrl.replace(".", "[.]").replace("http", "hxxp")

if __name__ == "__main__":
    parseSingleQR()