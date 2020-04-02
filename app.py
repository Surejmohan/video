from flask import Flask, render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import dlib,cv2
import numpy as np
import os
from flask.helpers import send_from_directory


UPLOAD_FOLDER = './uploads'
UPLOAD_VIDEO = './video'
DOWNLOAD = './result'

app = Flask(__name__)
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
         exit()

    
    rects, shapes = [], []
    shapes_np = np.zeros((len(dets), 68, 2), dtype=np.int)
    for k, d in enumerate(dets):
        rect = ((d.left(), d.top()), (d.right(), d.bottom()))
        rects.append(rect)

        shape = sp(image, d)
        
        # convert dlib shape to numpy array
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




@app.route('/current')
def current():
    return render_template('current.html')





@app.route('/upload', methods=['POST'])
def train():
    filelist = [f for f in os.listdir('uploads/')]
    for f in filelist:
        os.remove(os.path.join('uploads/', f))
    
    
    if request.method == 'POST':
        
        uploaded_files = request.files.getlist("file")
        for f in uploaded_files:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
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
            print("Maximum Number of Images is 2 ")
            filelist = [f for f in os.listdir('uploads/')]
            for f in filelist:
                os.remove(os.path.join('uploads/', f))
            exit()


        names = [x[:-4] for x in myimages]
        paths = ['uploads/' + x for x in myimages]
        print(names) 
    
        descs = {}

        for i in range(0,no_of_images):    
            img_bgr = cv2.imread(paths[i])
            image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            _ ,img_shapes, _ = find_faces(image,myimages[i])
            descs[i] = encode_faces(image, img_shapes)[0]
        if request.form['action'] == 'Request_Video':
            np.save('third/username.npy', descs)

            return render_template('current.html')




           
        elif request.form['action'] == "Upload":
            np.save('train/descs.npy', descs)
            descs = np.load('train/descs.npy',allow_pickle=True)[()]
            filelist2 = [f for f in os.listdir('video/')]
            for f in filelist2:
                os.remove(os.path.join('video/', f))

            videos = request.files.getlist("videos")
            f = videos[0]
            if len(videos) == 1 :
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_VIDEO'], filename))
                    video_path = 'video/'+ f.filename
                    print(video_path)
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        print("Video cannot Open")
                        exit()
        
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
                    print(convert(s/24)) 

            else:
                print("Only one video can upload")
                exit()






        elif request.form['action'] == "ON":
            np.save('train/descs.npy', descs)
            descs = np.load('train/descs.npy',allow_pickle=True)[()]
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Camera is not working")
                exit()
        
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
            print(convert(s/24)) 


            return render_template('current.html')






        
        



        return render_template('current.html')



def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds) 


@app.route('/master')
def master():
    return '<a class="label label-primary" href="/result/output.mp4" download target="_blank"  style="margin-right: 5px;">Download video </a>'


@app.route('/result/<path:filename>', methods=['GET', 'POST'])
def download(filename):

    return send_from_directory(directory='result', filename=filename)





        



if(__name__ == "__main__"):
    app.run(debug=True)
