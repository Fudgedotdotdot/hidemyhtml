## HideMyHTML

Hiding our "legitimate" phishing pages from pesky scanners that want our phishing engagements to fail.

### Installation
Use [pipx](https://pipx.pypa.io/stable/installation/).

`pipx install git+https://github.com/fudgedotdotdot/hidemyhtml`

### Usage
```
usage: main.py [-h] [-m {html,js}] [-t TEMPLATE] [-l] [file]

Obfuscates an HTML page to avoid pesky scanners

positional arguments:
  file                  HTML file to obfuscate (default: None)

options:
  -h, --help            show this help message and exit
  -m {html,js}, --mode {html,js}
                        Insert obfuscated HTML into a HTML or JS file (default: html)
  -t TEMPLATE, --template TEMPLATE
                        Fake HTML template to use (default: example)
  -l, --list            List available templates (default: False)
  ```

Clone a login page, put the assets (images, css, etc) into an assets directory (as shown below) and run the tool.
```
❯ find .
.
./assets
./assets/682lhlha.svg
./assets/favicon.ico
./assets/illustration
./assets/right_arrow.svg
./assets/styles.css
./index.html
```
The tool uses a template page to insert the login page into. The template is stored in the `template/*` directory and additional templates can be added.

To create a new template, you have to make sure to keep the `ENCODED_HTML_HERE`  in the HTML file and `DECODER_HERE` in the CSS file. The way you trigger the decoding process is up to you, the example template has, surprisingly, an example on how you could do so. 


### Additional remarks
I had some issues when executing javascript code contained in the login page after decoding and had to use an img tag with a onerror handler to run the required JS. 

Weirdly, the `document.write` sink should work with script tags (or maybe I'm just stupid) :  [https://portswigger.net/web-security/cross-site-scripting/dom-based](https://portswigger.net/web-security/cross-site-scripting/dom-based)

