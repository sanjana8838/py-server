def face_recog(esp_id):
    import pyrebase
    import cv2
    from imutils import paths
    from imutils.video import VideoStream
    import face_recognition
    import pickle
    import os
    import time
    import matplotlib.pyplot as plt
    import numpy as np
    import datetime
    import shutil
    import requests

    config = {
        "apiKey": "AIzaSyDa-6ZzY5bIhknMuy_zYJbqlUqwdEV7gGQ",
        "authDomain": "sonorous-dragon-296110.firebaseapp.com",
        "databaseURL": "https://sonorous-dragon-296110.firebaseio.com",
        "projectId": "sonorous-dragon-296110",
        "storageBucket": "sonorous-dragon-296110.appspot.com",
        "messagingSenderId": "858984143988",
        "appId": "1:858984143988:web:d7b23c780ed874c2254521",
        "measurementId": "G-JLWH0VHYXE",
        "serviceAccount": "C:/Users/Ramesh PC/Downloads/sonorous-dragon-296110-firebase-adminsdk-s4t49-39994f1dd8.json"
    }

    firebase = pyrebase.initialize_app(config)

    storage = firebase.storage()
    path_on_cloud = "found"
    url= "http://718e608f448f.ngrok.io/gettexts"

    print('Fetching database')
    db = firebase.database()
    all_objects = db.child('all_devices').child('%s' %(esp_id)).child('database').get()
    dirs = []
    for obj in all_objects.each():
        dirs.append(obj.key())
        #print(dirs)

    if (set(os.listdir('db_fr')) == set(list(filter(None, dirs)))):
        print('delete directory NOT entered')
    else:
        print('delete directory entered')
        delete = []
        for j in os.listdir('db_fr'):
            if j not in list(filter(None, dirs)):
                delete.append(j)
        for a in delete:
            shutil.rmtree("db_fr/%s" %(a))

    for obj in all_objects.each():
        print(obj.key())
        l = []
        if not os.path.exists('db_fr/%s' %(obj.key())):
            os.mkdir('db_fr/%s' %(obj.key()))
            print('File does not exist so directory created')
            #print(obj.key())
        objs2 = db.child('all_devices').child('%s' %(esp_id)).child('database').child(obj.key()).get() 
        for ob in objs2.each():
            l.append(ob.val())
            #print(l)
        if (set(os.listdir('db_fr/%s' %(obj.key()))) == set(list(filter(None, l)))):
            print('delete NOT entered')
        else:
            print('delete entered')
            delete = []
            for j in os.listdir('db_fr/%s' %(obj.key())):
                if j not in list(filter(None, l)):
                    delete.append(j)
            for a in delete:
                os.remove("db_fr/%s/%s" %(obj.key(),a))
        for ob in objs2.each():
            #print(ob.key(), ob.val())
            if ((os.path.isfile("db_fr/%s/%s" %(obj.key(),ob.val()))) or (ob.key() == 0)):
                continue
            else:
                #print(ob.val())
                print('Downloading')
                storage.child('database/%s/%s' %(obj.key(), ob.val())).download("db_fr/%s/%s" %(obj.key(),ob.val()))

    imagePaths = list(paths.list_images('C:/Users/Ramesh PC/Documents/AVRN/db_fr'))
    knownEncodings = []
    knownNames = []

    print('Extracting Features')
    for (i, imagePath) in enumerate(imagePaths):
        name = imagePath.split(os.path.sep)[-2]
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb,model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()

    cascPathface = os.path.dirname(
    cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    faceCascade = cv2.CascadeClassifier(cascPathface)
    data = pickle.loads(open('face_enc', "rb").read())
    

    print("Streaming started")
    # insert streaming link
    video_capture = VideoStream('http://718e608f448f.ngrok.io/mjpeg/1').start()
    #video_capture = VideoStream(0).start()
    print('Recognition started')
    while True:
        frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, (320, 220)) #reduces lag
        #frame = cv2.resize(frame, (1600, 1200))
        faces = faceCascade.detectMultiScale(gray,
                                            scaleFactor=1.1,
                                            minNeighbors=5,
                                            minSize=(60, 60),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"],
            encoding)
            name = "Unknown"
            if True in matches:
                print('found')
                ploads = {
                    "found":"1",
                    "submit":"Submit"
                }
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            else:
                ploads = {
                    "found":"0",
                    "submit":"Submit"
                }
            names.append(name)
            for ((x, y, w, h), name) in zip(faces, names):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (0, 255, 0), 2)
            outfile = '%s.jpg' % (name) 
            cv2.imwrite(outfile,frame)
            path_on_cloud = "found/%s_%s.jpg" % (name,datetime.datetime.now())
            storage.child(path_on_cloud).put(outfile)
        cv2.imshow("Frame", frame)
        
        #if 'ploads' in locals():
           #break

        if cv2.waitKey(1) & ('ploads' in locals()):
            break
    #video_capture.release()
    video_capture.stop()
    cv2.destroyAllWindows()
    return ploads

#if __name__ == '__main__':
 #   face_recog()