from flask import Flask, request, render_template, redirect
import PIL
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
import re, os
from http.client import responses

template_dir = os.path.abspath('../FrontEnd/templates')
static_dir = os.path.abspath('../FrontEnd/static')

# allow for files to be imported from other folder
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check for allowed image extensions
def allowed_file(filename : str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}


def defangURL(rawUrl : str) -> str:
    return rawUrl.replace(".", "[.]").replace("http", "hxxp")


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


@app.route('/')
def upload_form() -> dict: # returns response object
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file() -> str:
    file = request.files['file']
    if 'file' not in request.files or file.filename == '':
        retObj = redirect(request.url)
        msg = f"{retObj.status_code} - {responses[retObj.status_code]}"
        return render_template('response.html', displayStr=msg)

    if file and allowed_file(file.filename):
        # Ensure the 'uploads' directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the uploaded file to the 'uploads' directory
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        # Process the uploaded image as needed (e.g., display it)
        fullPath = Path(app.config['UPLOAD_FOLDER'] + os.sep + file.filename)
        retStr, isValidUrl = parseSingleQR(fullPath)

        if isValidUrl:
            finalStr = f"Url: {retStr}"
            return render_template('response.html', displayStr=finalStr)
        else:
            return render_template('response.html', displayStr=retStr)

    return render_template('response.html', displayStr ='Invalid file type! Allowed extensions: jpg, jpeg, png, gif.')


@app.route('/<path:catch_all>')
def catch_all(catch_all) -> None:
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
