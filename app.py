from flask import Flask, render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import dlib,cv2
import numpy as np
import os
from flask.helpers import flash, get_flashed_messages, send_from_directory


UPLOAD_FOLDER = './uploads'
UPLOAD_VIDEO = './video'
DOWNLOAD = './result'
ALLOWED_FILEEXTENSIONS = set(['jpg','jpeg'])
ALLOWED_VIDEOEXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_VIDEO'] = UPLOAD_VIDEO
app.config['DOWNLOAD'] = DOWNLOAD

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')



def find_faces(image,name):

    dets = detector(image, 1)

    if len(dets) == 0:
        return np.empty(0), np.empty(0), np.empty(0)
    if len(dets) > 1:
        print("Please change image: " + name + " - it has " + str(len(dets)) + " faces; it can only have one")

    
    rects, shapes = [], []
    shapes_np = np.zeros((len(dets), 68, 2), dtype=np.int)
    for k, d in enumerate(dets):
        rect = ((d.left(), d.top()), (d.right(), d.bottom()))
        rects.append(rect)

        shape = sp(image, d)
        
       
        for i in range(0, 68):
            shapes_np[k][i] = (shape.part(i).x, shape.part(i).y)

        shapes.append(shape)
        
    return rects, shapes, shapes_np


def encode_faces(img, shapes):
    face_descriptors = []
    for shape in shapes:
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        face_descriptors.append(np.array(face_descriptor))

    return np.array(face_descriptors)


def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds) 


def allowed_file1(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_FILEEXTENSIONS

def allowed_file2(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOEXTENSIONS






@app.route('/current')
def current():
    return render_template('current.html')


@app.route('/master')
def current1():
    return render_template('output.html')



@app.route('/upload', methods=['POST'])
def train():
    filelist = [f for f in os.listdir('uploads/')]
    for f in filelist:
        os.remove(os.path.join('uploads/', f))
    
    
    if request.method == 'POST':
        
        uploaded_files = request.files.getlist("file")
        for f in uploaded_files:
            if f and allowed_file1(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Invalid Input File Format; only jpeg or jpg supported")
                print("Invalid Input File Format; only jpeg or jpg supported")
                return redirect(url_for('current'))
        
        myimages = []
        dirfiles = os.listdir('uploads/')
        sorted(dirfiles)
        for files in dirfiles:
            if '.jpg' in files:
                myimages.append(files)
            if '.jpeg' in files:
                myimages.append(files)
        no_of_images = len(myimages)
        if no_of_images > 2:
            flash('Maximum Number of Images is 2')
            print("Maximum Number of Images is 2 ")
            filelist = [f for f in os.listdir('uploads/')]
            for f in filelist:
                os.remove(os.path.join('uploads/', f))
            return redirect(url_for('current'))


        names = [x[:-4] for x in myimages]
        paths = ['uploads/' + x for x in myimages]
        print(names) 
    
        descs = {}

        for i in range(0,no_of_images):    
            img_bgr = cv2.imread(paths[i])
            image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            if len(detector(image, 1)) > 1 :
                flash('Please change image: ' + myimages[i] + ' - it has ' + str(len(detector(image, 1))))
                print("Please change image: " + myimages[i] + " - it has " + str(len(detector(image, 1))) + " faces; it can only have one")
                return redirect(url_for('current'))

            _ ,img_shapes, _ = find_faces(image,myimages[i])
            descs[i] = encode_faces(image, img_shapes)[0]
        if request.form['action'] == 'Request_Video':
            np.save('third/username.npy', descs)

            return render_template('output.html')




           
        elif request.form['action'] == "Upload":
            np.save('train/descs.npy', descs)
            descs = np.load('train/descs.npy',allow_pickle=True)[()]
            filelist2 = [f for f in os.listdir('video/')]
            for f in filelist2:
                os.remove(os.path.join('video/', f))

            videos = request.files.getlist("videos")
            f = videos[0]
            if len(videos) == 1 :
                    if not allowed_file2(f.filename):
                        flash('Invalid Video Format ;Only Mp4 Supported')
                        print("Invalid Video Format ;Only Mp4 Supported")
                        return redirect(url_for('current'))
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_VIDEO'], filename))
                    video_path = 'video/'+ f.filename
                    print(video_path)
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        flash('Video cannot Open')
                        print("Video cannot Open")
                        return redirect(url_for('current'))
        
                    _, img_bgr = cap.read()
                    padding_size = 0
                    resized_width = 1920
                    video_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1]))
                    output_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1] + padding_size * 2))

                    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                    writer = cv2.VideoWriter('result/output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)
                    m=-1
                    i=1
                    s=0
                    while True:
                        
                        ret, img_bgr = cap.read()
                        if not ret:
                            break
    
                        img_bgr = cv2.resize(img_bgr, video_size)
                        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                        dets = detector(img_bgr, 1)

                        for k, d in enumerate(dets):
                            shape = sp(img_rgb, d)
                            face_descriptor = facerec.compute_face_descriptor(img_rgb, shape)

                            last_found = {'name': 'unknown', 'dist': 0.45, 'color': (0,0,255)}

                            for name, saved_desc in descs.items():
                                dist = np.linalg.norm([face_descriptor] - saved_desc, axis=1)

                                if dist < last_found['dist']:
                                    last_found = {'name': "Target", 'dist': dist, 'color': (255,255,255)}
                                    if m == -1:
                                        s = i
                                        m=0
                                    
                            cv2.rectangle(img_bgr, pt1=(d.left(), d.top()), pt2=(d.right(), d.bottom()), color=last_found['color'], thickness=2)
                            cv2.putText(img_bgr, last_found['name'], org=(d.left(), d.top()), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=last_found['color'], thickness=2)
                        i=i+1
                        writer.write(img_bgr)
                    
                
                    cap.release()
                    writer.release()
                    time = convert(s/24)
                    print(convert(s/24)) 
                    success = "You have successfully Processed the Video"
                    return render_template('output.html',success = success, time = time)

            else:
                flash('Only one video can upload')
                print("Only one video can upload")
                return redirect(url_for('current'))






        elif request.form['action'] == "ON":
            np.save('train/descs.npy', descs)
            descs = np.load('train/descs.npy',allow_pickle=True)[()]
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                flash('Camera is not working')
                print("Camera is not working")
                return redirect(url_for('current'))
        
            _, img_bgr = cap.read()
            padding_size = 0
            resized_width = 1360
            video_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1]))
            output_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1] + padding_size * 2))

            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            writer = cv2.VideoWriter('result/output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)
            m=-1
            i=1
            s=0
            while True:
                        
                ret, img_bgr = cap.read()
                if not ret:
                    break

                img_bgr = cv2.resize(img_bgr, video_size)
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                dets = detector(img_bgr, 1)

                for k, d in enumerate(dets):
                    shape = sp(img_rgb, d)
                    face_descriptor = facerec.compute_face_descriptor(img_rgb, shape)

                    last_found = {'name': 'unknown', 'dist': 0.45, 'color': (0,0,255)}

                    for name, saved_desc in descs.items():
                        dist = np.linalg.norm([face_descriptor] - saved_desc, axis=1)

                        if dist < last_found['dist']:
                            last_found = {'name': "Target", 'dist': dist, 'color': (255,255,255)}
                            if m == -1:
                                s = i
                                m=0
                                    
                    cv2.rectangle(img_bgr, pt1=(d.left(), d.top()), pt2=(d.right(), d.bottom()), color=last_found['color'], thickness=2)
                    cv2.putText(img_bgr, last_found['name'], org=(d.left(), d.top()), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=last_found['color'], thickness=2)
                i=i+1
                writer.write(img_bgr)
                cv2.imshow('img', img_bgr)
                if cv2.waitKey(1) == ord('q'):
                    break
                    
                
            cap.release()
            writer.release()
            time = convert(s/24)
            print(convert(s/24)) 
            success = "You have successfully Processed the Video"
            return render_template('output.html',success = success, time = time)

        
    else:
        print("Error")
        exit()







@app.route('/result/<path:filename>', methods=['GET', 'POST'])
def download(filename):

    return send_from_directory(directory='result', filename=filename)





        



if(__name__ == "__main__"):
    app.run(debug=True)
