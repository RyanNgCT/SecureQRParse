# SecureQRParse

- Python Script to extract urls and defang them from QR Codes.
- Command-Line Tool Interface _for now_ (can use `--file` or `--directory` to extract urls from a given file/directory).

## Possible To-dos

- [x] allow for recursive search (depth > 1) when looking at files in subdirectories/subfolders, while using the `--directory` flag.
- [x] convert and host python script as an interactive Flask Web-App.
- [ ] security mechanisms for Flask Web-App.