from flask import Flask, request, render_template, redirect
import PIL
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
import re, os, magic
from http.client import responses

template_dir = os.path.abspath('../FrontEnd/templates')
static_dir = os.path.abspath('../FrontEnd/static')

# allow for files to be imported from other folder
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check for allowed image extensions
def allowed_file(file) -> bool:
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}
    mime = magic.Magic(mime=True)
    detectedMimeType = mime.from_buffer(file.read(512))  # Read the first 512 bytes to determine the MIME type
    file.seek(0)
    return detectedMimeType in ALLOWED_MIME_TYPES


def defangURL(rawUrl : str) -> str:
    return rawUrl.replace(".", "[.]").replace("http", "hxxp")


def refangURL(rawUrl : str) -> str:
    return rawUrl.replace("hxxp", "http").replace("[.]", ".")


def parseSingleQR(file : Path) -> tuple[str, bool]:
    """ based on a file, determine if whether the file contains a valid QR Code 
        and return the corresponding URL, if any, defanged. """
    
    try:
        fileExif = decode(Image.open(file))
    except PIL.UnidentifiedImageError:
        return "File supplied is not a valid image or QR Code.", False
    else:
        if fileExif == []:
             return "File either is not or does not contain valid a QR Code.", False

        # check type of image and if data field exists
        if fileExif[0].type == "QRCODE" and fileExif[0].data:
            rawData = fileExif[0].data.decode()
            uri_pattern = r"^(?:https?|hxxps?):\/\/(?:\[\.\]|\[\.\]\[\.\]|[^\[\]])+|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)(?:$|\s)"
            if re.match(uri_pattern, rawData):
                return defangURL(rawData), True
            else:
                return "No url detected in QR Code.", False
        return "File either is not or does not contain valid a QR Code.", False


@app.route('/')
def upload_form() -> dict: # returns response object
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file() -> str:
    file = request.files['file']
    if 'file' not in request.files or file.filename == '':
        retObj = redirect(request.url)
        msg = f"{retObj.status_code} - {responses[retObj.status_code]}"
        exception = True
        return render_template('response.html', displayStr=msg, exception=exception)

    if file and allowed_file(file):
        # Ensure the 'uploads' directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the uploaded file to the 'uploads' directory
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        # Process the uploaded image as needed (e.g., display it)
        fullPath = Path(app.config['UPLOAD_FOLDER'] + os.sep + file.filename)
        retStr, isValidUrl = parseSingleQR(fullPath)

        if isValidUrl:
            finalStr = f"Defanged URL: {retStr}"
            rawUri=refangURL(retStr)
            return render_template('response.html', displayStr=finalStr, condition=isValidUrl, rawUri=rawUri)
        else:
            exception = True
            return render_template('response.html', displayStr=retStr, exception=exception)
    exception = True
    return render_template('response.html', displayStr ='Invalid file type! Allowed extensions: jpg, jpeg, png, gif.', exception=exception)

@app.route('/<path:catch_all>')
def catch_all(catch_all) -> None:
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
