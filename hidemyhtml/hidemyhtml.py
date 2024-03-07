import argparse
from pathlib import Path
import random
import string
from base64 import b64encode, b64decode
import os
from random import randrange

import gzip
from calmjs.parse import es5
from calmjs.parse.unparsers.es5 import minify_print
from colorama import Fore
from colorama import init as colorama_init
colorama_init(autoreset=True)


KEY = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8,12)))
WORDS = ["cousin","advice","cookie","association","movie","speaker","procedure","aspect","platform","construction","priority","permission","strategy","failure","description","sir","cancer","impression","economics","pollution","appearance","reflection","intention","concept","analysis","introduction","thing","ad","artisan","manager","knowledge","honey","guidance","ladder","potato","friendship","community","effort","food","airport","army","sympathy","bathroom","steak","instruction","phone","restaurant","combination","transportation","tradition"]

def pretty_p(msg: str, color=Fore.GREEN):
    print(f"[{color}+{Fore.RESET}] {msg}")


def rename_links(html: str) -> str:
    new_source = html
    assets = Path("assets")
    assets = [str(fname) for fname in list(assets.glob("*"))]
    pretty_p("Renaming files...")
    for fsrc in assets:
        original_fname = Path(fsrc).parts[-1]
        if f"/assets/{original_fname}" in new_source:
            pretty_p(f"Skipping {fsrc} - already renamed", color=Fore.BLUE)
            continue
        random_name = '-'.join(random.choices(WORDS, k=random.randint(2,4)))
        extension = Path(fsrc).parts[-1].split('.')[1]
        renamed_fname = f"assets/{random_name}.{extension}"
        new_source = new_source.replace(original_fname, renamed_fname)
        os.rename(fsrc, renamed_fname)
    return new_source


def encrypt_html(source: str) -> str:
    encrypted_html = bytearray()
    gzip_data = gzip.compress(source.encode('utf8'))
    for idx, _ in enumerate(bytearray(gzip_data)):
        encrypted_html.append(gzip_data[idx] ^ ord(KEY[idx % len(KEY)]))
    return b64encode(encrypted_html).decode()


def decrypt_html(source: str) -> str:
    decrypted_gzip = bytearray()
    decoded = b64decode(source)
    for idx, _ in enumerate(bytearray(decoded)):
        decrypted_gzip.append(decoded[idx] ^ ord(KEY[idx % len(KEY)]))

    real_gzip_data = gzip.decompress(decrypted_gzip)
    print(real_gzip_data[:8])


def encrypt_decoder(js_decoder: str, mode: str, template: str = "example") -> str:
    decoder_src = Path(__file__).parent / f"template/{template}"
    if mode == "js":
        decoder_js = f'{decoder_src}/js_decode.js'
    else:
        decoder_js = f'{decoder_src}/html_decode.js'

    with open(decoder_js, 'r') as f:
        js_decoder = f.read()
    
    js_decoder = js_decoder.replace('ENC_KEY', KEY)
    js_decoder = es5(js_decoder)
    js_decoder = minify_print(js_decoder, obfuscate=True)
    return b64encode(js_decoder.encode()).decode()


def gen_html(fake_html: str, source: str):
    return fake_html.replace("ENCODED_HTML_HERE", f'<!-- {source} -->')


def gen_js(fake_html: str, source: str):
    js_file = "output/Jquery-3.4.1.slim.min.js"
    with open(f'{js_file}', 'w', encoding='utf8') as f:
        f.write(f"var ixs = \"{source}\"")
    return fake_html.replace("ENCODED_HTML_HERE", f'<script src="{js_file}"></script>')


def insert_html(source: str, decoder: str, mode: str, template: str = "example"):
    with open(Path(__file__).parent / f"template/{template}/index.html", 'r', encoding='utf8') as f:
        fake_html = f.read()
    with open(Path(__file__).parent / f"template/{template}/styles.css", 'r', encoding='utf8') as f:
        fake_css = f.read()

    if mode == "js":
        fake_html = gen_js(fake_html, source)
    else:
        fake_html = gen_html(fake_html, source)
    
    fake_css = fake_css.replace("DECODER_HERE", decoder)

    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(fake_html)
    with open('output/styles2.css', 'w', encoding='utf-8') as f:
        f.write(fake_css)


def main():
    parser = argparse.ArgumentParser(description="Obfuscates an HTML page to avoid pesky scanners", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file", help="HTML file to obfuscate", nargs="?")
    parser.add_argument("-m", "--mode", dest="mode", default="html", choices=['html', 'js'], help="Insert obfuscated HTML into a HTML or JS file")
    parser.add_argument("-t", "--template", dest="template", default="example", help="Fake HTML template to use")
    parser.add_argument("-l", "--list", dest="list", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list:
        templates_path = Path(__file__).parent / "template"
        print('\n'.join([x.parts[-1] for x in templates_path.iterdir() if x.is_dir() and x.parts[-1] != "__pycache__"])) # silly fix for __pycache__ if user generates this directory
        return
    if not args.file:
        parser.error('the following argument are required: file')

    Path("./output").mkdir(exist_ok=True)

    pretty_p(f"Selected the {Fore.LIGHTBLUE_EX}{args.template}{Fore.RESET} template as a target...")
    with open(args.file, 'r', encoding="utf-8") as f:
        html_doc = f.read()
    html_doc = rename_links(html_doc)
    pretty_p(f"Compressing and XOR'ing page...")
    encrypted_html = encrypt_html(html_doc)
    enc_decoder = encrypt_decoder(args.mode, args.template)
    pretty_p("Hiding obfuscated HTML into our clean HTML template...")
    insert_html(encrypted_html, enc_decoder, args.mode)


if __name__ == "__main__":
    main()