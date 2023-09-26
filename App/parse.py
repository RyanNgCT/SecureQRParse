from pathlib import Path
import argparse, sys, os
from Components.parseqr import parseSingleQR

def parseQRsInDir(dirPath : Path) -> list[str]:
    """ based on a directory, enumerate over its file contents and run 
        parseSingleQR(), recursive, if there are subdirectories """
    
    allExtractedUrls = {} # maybe for future use
    extractedUrls = [] # list of defanged urls to be returned
    validUrls = 0  # counter for valid URLs
    index = 1

    for root, _, files in os.walk(dirPath):
        for file in files:
            filePath = os.path.join(root, file)
            filePath = Path(filePath)
            result, isValidUrl = parseSingleQR(filePath)
            allExtractedUrls[index] = result
            if isValidUrl:
                validUrls += 1
                extractedUrls.append(result)
            index += 1

    # displays validUrls out of totalUrls
    print(f"[INFO]: Decoded {validUrls} of {index - 1} files at location: '{dirPath.resolve()}'\n")
    return list(set(extractedUrls)) # remove duplicate urls, if any


def main() -> None:
    argDesc = '''SecureQRParse v0.3, (c) RyanNgCT, 2023'''
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
