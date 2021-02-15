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

@app.route('/posts', methods=['POST', 'GET'])
def hh():
    if request.method == 'POST':
        print(request.files)
        data = request.form.to_dict()
        print(data)
       #f = request.files['rec00002.wav']
       #f.save(secure_filename(f.filename))
    return 'file uploaded successfully'


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "/audio111.wav"
    return send_file(path, as_attachment=True)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)

if __name__ == '__main__':

    app.run()
