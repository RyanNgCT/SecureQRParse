# SecureQRParse

- Python Script and Web Application to extract urls and defang them from QR Codes.

### 1. Installation of Scripts and Dependencies
```bash
$ git clone https://github.com/RyanNgCT/SecureQRParse
$ cd SecureQRParse
$ pip install -r requirements.txt # optionally create virtual env
```

### 2. Usage
- Command-Line Tool Interface (can use `--file` or `--directory` to extract urls from a given file/directory).
```bash
$ cd App
$ python parse.py [--file/-f <FILE>] [--directory/-d <DIR>] [-h/--help]
```

- Flask Web App
```bash
# install dependencies first
$ cd App && flask run
```

To modify the css stylings:
a) install Node.js on your platform: https://nodejs.org/en/download/

b) run the `npx` script
```
$ cd App/FrontEnd
$ npm run create-css
```

### Possible To-dos

- [x] allow for recursive search (depth > 1) when looking at files in subdirectories/subfolders, while using the `--directory` flag.
- [x] convert and host python script as an interactive Flask Web-App.
- [ ] security mechanisms for Flask Web-App.


### Others
- Reference to set-up Tailwind CSS on Flask: https://www.codewithharry.com/blogpost/using-tailwind-with-flask/