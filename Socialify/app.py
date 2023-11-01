
from flask import Flask, request, redirect, render_template, jsonify, send_file
import string
import random
import csv
import qrcode
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)

def generate_shortcode():
    characters = string.ascii_letters + string.digits
    shortcode = ''.join(random.choice(characters) for _ in range(6))  # 6-character shortcode
    return shortcode

url_mappings = {}  # Dictionary to store shortcode-long URL mappings

def load_url_mappings_from_csv():
    try:
        with open('url_mappings.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    shortcode, long_url = row[:2]
                    url_mappings[shortcode] = long_url
                else:
                    print('Invalid row in CSV: ' + row)
    except FileNotFoundError:
        pass


def store_url(long_url, shortcode):
    if not long_url.startswith('http://') and not long_url.startswith('https://'):
        long_url = 'https://' + long_url

    with open('url_mappings.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([shortcode, long_url])
    url_mappings[shortcode] = long_url


@app.route('/')
def index():
    return render_template('index.html', shortened_url=None)

    long_url = request.form['long_url']
    if not long_url.startswith('http://') and not long_url.startswith('https://'):
        long_url = 'https://' + long_url

    shortcode = generate_shortcode()
    store_url(long_url, shortcode)
    shortened_url = '/{}'.format(shortcode)
    return jsonify({'shortened_url': shortened_url})


@app.route('/<shortcode>')
def redirect_to_long_url(shortcode):
    long_url = url_mappings.get(shortcode)
    ##print("Long URL:", long_url)  # used in debugging
    if long_url:
        return redirect(long_url, code=301)
    return 'Shortcode not found'


@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form['long_url']
    if not long_url.startswith('http://') and not long_url.startswith('https://'):
        long_url = 'https://' + long_url

    shortcode = generate_shortcode()
    store_url(long_url, shortcode)
    shortened_url = '/{}'.format(shortcode)

    # Generate QR code and save it to BytesIO
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(long_url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a BytesIO object
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes)
    qr_bytes.seek(0)

    # Save the QR code to a file
    qr_filename = 'qrcodes/qrcode_{}.png'.format(shortcode)
    qr_img.save(qr_filename)

    return jsonify({
        'shortened_url': shortened_url,
        'qr_code_bytes': qr_bytes.read().decode('ISO-8859-1'), # Return QR code as base64 encoded string
        'qr_code_url': qr_filename
    })
    
# Add a route to serve QR code images
@app.route('/qrcodes/<filename>')
def get_qrcode(filename):
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    load_url_mappings_from_csv()
    app.run(debug=True)
