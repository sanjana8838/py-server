from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import send_file, flash
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
from flask import current_app
app = Flask(__name__)
import requests
import json
import face_recog_firebase as frf


UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '123'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def hello():
    url1 = "http://22d14db794c7.ngrok.io/getid"
    s = requests.session()
    r = s.get(url1)
    esp_id = r.text
    s.delete(url1)
    ploads = frf.face_recog(esp_id)
    url2= "http://22d14db794c7.ngrok.io/gettexts"
    s = requests.session()
    #r = requests.request("POST", url, params=ploads, headers=headers)
    r = s.post(url2, params=ploads)
    y = str(r.text)
    s.delete(url2)

    return y

@app.route('/getposts', methods=['GET','POST'])
def hi():
    return render_template('form.html')


