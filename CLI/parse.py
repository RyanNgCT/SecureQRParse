import PIL
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
import argparse, sys, re, os


def parseSingleQR(file : Path) -> tuple[str, bool]:
    """ based on a file, determine if whether the file contains a valid QR Code 
        and return the corresponding URL, if any, defanged. """
    
    try:
        fileExif = decode(Image.open(file))
    except PIL.UnidentifiedImageError:
        return "File supplied is not a valid image or QR Code.", False
    else:
        # check type of image and if data field exists
        if fileExif[0].type == "QRCODE" and fileExif[0].data:
            rawData = fileExif[0].data.decode()
            uri_pattern = r"^(?:https?|hxxps?):\/\/(?:\[\.\]|\[\.\]\[\.\]|[^\[\]])+|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)(?:$|\s)"
            if re.match(uri_pattern, rawData):
                return defangURL(rawData), True
            else:
                return "No url detected in QR Code.", False
        return "File is not/does not contain a QR Code.", False


def parseQRsInDir(dirPath : Path) -> list[str]:
    """ based on a directory, enumerate over its file contents and run 
        parseSingleQR(), recursive, if there are subdirectories """
    
    def parseDir(path : Path) -> set[str]:
        allExtractedUrls = {} # maybe for future use
        extractedUrls = [] # list of defanged urls to be returned
        validUrls = 0  # counter for valid URLs
        index = 1

        for root, _, files in os.walk(path):
            for file in files:
                filePath = os.path.join(root, file)
                result, isValidUrl = parseSingleQR(filePath)
                allExtractedUrls[index] = result
                if isValidUrl:
                    validUrls += 1
                    extractedUrls.append(result)
                index += 1

        # displays validUrls out of totalUrls
        print(f"[INFO]: Decoded {validUrls} of {index - 1} files at location: '{path.resolve()}'\n")
        return list(set(extractedUrls)) # remove duplicate urls, if any

    return parseDir(dirPath)


def defangURL(rawUrl : str) -> str:
    return rawUrl.replace(".", "[.]").replace("http", "hxxp")


def main() -> None:
    argDesc = '''SecureQRParse v0.2, (c) RyanNgCT, 2023'''
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description=argDesc)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="File to be parsed.")
    group.add_argument("-d", "--directory", help="Directory of file(s) to be parsed")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.file:
        pathOfFile = Path(args.file)
        if pathOfFile.is_file():
            retStr, isValidUrl = parseSingleQR(pathOfFile)
        else:
            sys.exit("Specified location is not a file / does not exist.")

    elif args.directory:
        pathOfDir = Path(args.directory)
        if pathOfDir.is_dir():
            retStr = parseQRsInDir(pathOfDir)
        else:
            sys.exit("Specified location is not a directory / does not exist.")
    
    if args.directory or isValidUrl:
        print("Url(s), exclude duplicate: ", retStr)
    else:
        print(retStr)


if __name__ == "__main__":
    main()
