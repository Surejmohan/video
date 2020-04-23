#import libraries

from flask import Flask, render_template,request,redirect,url_for
from werkzeug.utils import secure_filename
import dlib,cv2
import numpy as np
import os
from flask.helpers import flash, get_flashed_messages, send_from_directory
from flask import url_for,session,logging,request
from _datetime import datetime
from flask_sqlalchemy import SQLAlchemy

#end


#intialise direectories and keys

UPLOAD_FOLDER = './uploads'
UPLOAD_VIDEO = './video'
DOWNLOAD = './result'
THIRDVIDEO = './third_video'
ALLOWED_FILEEXTENSIONS = set(['jpg','jpeg'])
ALLOWED_VIDEOEXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_VIDEO'] = UPLOAD_VIDEO
app.config['DOWNLOAD'] = DOWNLOAD
app.config['THIRDVIDEO'] = THIRDVIDEO

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret'

#end

#import ML models 
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('models/dlib_face_recognition_resnet_model_v1.dat')
#end

#database models
db = SQLAlchemy(app)
#db is the refrence

#User table
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(50),unique=True, nullable=False,primary_key=True)
    password = db.Column(db.String(15),nullable=False)
    type = db.Column(db.String(15),nullable=False)

    def __init__(self,username,password,type):
        self.username=username
        self.password=password
        self.type=type
    
#Admin Table
class Admin(db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    mail = db.Column(db.String(50))
    admin_id = db.Column(db.String(20))
    usr_name = db.Column(db.String, db.ForeignKey('User.username'),nullable=False)

    def __init__(self,usr_name,fname,lname,phone,mail,admin_id):
        self.usr_name=usr_name
        self.fname=fname
        self.lname=lname
        self.phone=phone
        self.mail=mail
        self.admin_id=admin_id 
        
#Authority Table
class Authority(db.Model):
    __tablename__ = 'Authority'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    phone = db.Column(db.Integer)
    mail = db.Column(db.String(50))
    job = db.Column(db.String(50))
    proof=db.Column(db.String(40))
    confirm=db.Column(db.Boolean,unique=False, default=False)
    usr_name = db.Column(db.String, db.ForeignKey('User.username'),nullable=False)
    

    def __init__(self,usr_name,fname,lname,phone,mail,job,proof,confirm):
        self.usr_name=usr_name
        self.fname=fname
        self.lname=lname
        self.phone=phone
        self.mail=mail
        self.job=job
        self.proof=proof 
        self.confirm=confirm


#Ordinary Table
class Ordinary(db.Model):
    __tablename__ = 'Ordinary'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    fname = db.Column(db.String(30))
    lname = db.Column(db.String(30))
    phone = db.Column(db.Integer)
    mail = db.Column(db.String(30))
    state = db.Column(db.String(30))
    city = db.Column(db.String(30))
    proof=db.Column(db.String(40))
    address=db.Column(db.String(50))
    zip = db.Column(db.Integer)
    confirm=db.Column(db.Boolean,unique=False, default=False)
    usr_name = db.Column(db.String, db.ForeignKey('User.username'),nullable=False)
    

    def __init__(self,usr_name,fname,lname,phone,mail,state,city,address,zip,proof,confirm):
        self.usr_name=usr_name
        self.fname=fname
        self.lname=lname
        self.phone=phone
        self.mail=mail
        self.state=state
        self.proof=proof    
        self.address=address
        self.city=city
        self.zip=zip
        self.confirm=confirm


#Other Table
class Other(db.Model):
    __tablename__ = 'Other'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_approval = db.Column(db.String(5))
    admin_id =  db.Column(db.String(20))
    no_of_video_upload = db.Column(db.Integer)
    no_of_video_request = db.Column(db.Integer)
    third_party_issue_id = db.Column(db.Integer)
    third_party_pending_order = db.Column(db.String(10))
    third_party_response = db.Column(db.String(20))  #video available or not
    date= db.Column(db.String(20))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    live_recording_no=db.Column(db.Integer)
    usr_name = db.Column(db.String, db.ForeignKey('User.username'),nullable=False)
    

    def __init__(self,admin_approval,admin_id,no_of_video_upload,no_of_video_request,third_party_issue_id,third_party_pending_order,third_party_response,date,start_time,end_time,live_recording_no,usr_name):
        self.admin_approval=admin_approval
        self.admin_id=admin_id
        self.no_of_video_request=no_of_video_upload
        self.third_party_issue_id=third_party_issue_id
        self.third_party_pending_order=third_party_pending_order
        self.third_party_response=third_party_response
        self.date=date    
        self.start_time=start_time
        self.end_time=end_time
        self.live_recording_no=live_recording_no
        self.usr_name=usr_name


#Third table
class Third(db.Model):
    __tablename__ = 'Third'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    dept = db.Column(db.String(50))
    name = db.Column(db.String(50))
    mail = db.Column(db.String(50))
    third_party_id = db.Column(db.String(20))
    phone = db.Column(db.Integer)
    usr_name = db.Column(db.String, db.ForeignKey('User.username'),nullable=False)

    def __init__(self,usr_name,dept,name,mail,third_party_id,phone):
        self.usr_name=usr_name
        self.dept=dept
        self.name=name
        self.phone=phone
        self.mail=mail
        self.third_party_id=third_party_id


#Count table
class Count(db.Model):
    __tablename__ = 'Count'
    id = db.Column(db.Integer, primary_key=True)
    Ordinary = db.Column(db.Integer)
    Authority = db.Column(db.Integer)
    Admin = db.Column(db.Integer)
    Third_party = db.Column(db.Integer)
    Total_Real= db.Column(db.Integer)
    Total_upload = db.Column(db.Integer)
    Total_request = db.Column(db.Integer)

    def __init__(self,id,Ordinary,Authority,Admin,Third_party,Total_Real,Total_upload,Total_request):
        self.id = id
        self.Ordinary = Ordinary
        self.Authority = Authority
        self.Admin = Admin
        self.Third_party = Third_party
        self.Total_Real = Total_Real
        self.Total_upload = Total_upload
        self.Total_request = Total_request
        
#end


#ML Functions

# findface function
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
#end


# encode face function
def encode_faces(img, shapes):
    face_descriptors = []
    for shape in shapes:
        face_descriptor = facerec.compute_face_descriptor(img, shape)
        face_descriptors.append(np.array(face_descriptor))

    return np.array(face_descriptors)

# convert to time format
def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds) 
#end

#allowed files
def allowed_file1(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_FILEEXTENSIONS
#end

#allowed videos
def allowed_file2(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEOEXTENSIONS
#end

#end




#contollers


#Thirdparty Page

@app.route('/thirdparty')
def  thirddashboard():
    all = Other.query.filter_by(third_party_issue_id = 'Railway_1',third_party_pending_order = 'no').all()
    len1 = len(all)
    if (len1 == 0):
        value = 'None'
        flash("You do not have any Request")
        return render_template('newthird.html',all=all,value = value)

    else:
        value = 'success'
        flash("You Have " + str(len1) + " Request")
        return render_template('newthird.html',all=all,value = value)



@app.route('/thirdparty/pendinguser',methods=['POST'])
def  PendingUser():

        if request.method == 'POST':

            file = request.files['video']
            userid = request.form['userid']
            username = request.form['username']
            response = request.form['response']
            print(file.filename)
            print(username)
            if request.form['accept'] == "accept":

                    if not allowed_file2(file.filename):
                        flash('Invalid Video Format ;Only Mp4 Supported')
                        print("Invalid Video Format ;Only Mp4 Supported")
                        category = 'errorvideo'
                        return render_template('newthird.html',category = category)
                    file.filename = username + ".mp4"
                    print(file.filename)
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['THIRDVIDEO'], filename))
                    ord = Other.query.filter_by(id = userid).first()
                    ord.third_party_pending_order = 'yes'
                    ord.third_party_response = response
                    db.session.add(ord)
                    db.session.commit()
                    category = 'success1'
                    flash("You have successfully submit Video")
                    return render_template('newthird.html',category = category)
            elif request.form['accept'] == "reject":
                    ord = Other.query.filter_by(id = userid).first()
                    ord.third_party_pending_order = 'reject'
                    ord.third_party_response = response
                    db.session.add(ord)
                    db.session.commit()
                    category = 'success2'
                    flash("You have successfully  Sent your Response ")
                    return render_template('newthird.html',category = category)

            


@app.route('/thirdparty/realtimevideo',methods=['POST'])
def  reatimevideo():

    filelist = [f for f in os.listdir('uploads/')]
    for f in filelist:
        os.remove(os.path.join('uploads/', f))

    if request.method == 'POST':
        
        uploaded_files = request.files.getlist("livefile")
        for f in uploaded_files:
            if f and allowed_file1(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash("Invalid Input File Format; only jpeg or jpg supported")
                print("Invalid Input File Format; only jpeg or jpg supported")
                category = 'errorimage'
                return render_template('newthird.html',category = category)
        
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
            category = 'errornumber'
            return render_template('newthird.html',category = category)


        names = [x[:-4] for x in myimages]
        paths = ['uploads/' + x for x in myimages]
        print(names) 
    
        descs = {}

        for i in range(0,no_of_images):    
            img_bgr = cv2.imread(paths[i])
            image = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            if len(detector(image, 1)) > 1 :
                flash('Please change image: ' + myimages[i] + ' - it has ' + str(len(detector(image, 1))) + " faces")
                print("Please change image: " + myimages[i] + " - it has " + str(len(detector(image, 1))) + " faces; it can only have one")
                category = 'errorface'
                return render_template('newthird.html',category = category)

            _ ,img_shapes, _ = find_faces(image,myimages[i])
            descs[i] = encode_faces(image, img_shapes)[0]
        if request.form['subm'] == 'submit':
            np.save('train/descs.npy', descs)
            descs = np.load('train/descs.npy',allow_pickle=True)[()]
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                flash('Camera is not working')
                print("Camera is not working")
                category = 'errorcamera'
                return render_template('newthird.html',category = category)
        
            _, img_bgr = cap.read()
            padding_size = 0
            resized_width = 1360
            video_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1]))
            output_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1] + padding_size * 2))

            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            writer = cv2.VideoWriter('result/username.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)
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

                    last_found = {'name': 'unknown', 'dist': 0.48, 'color': (0,0,255)}

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
            flash("You have successfully Processed the Video")
            category = 'success3'
            return render_template('newthird.html',category = category)
    


    else:
        print("Error")
        exit()


#end



# Current page 

@app.route('/user/current')
def current():
    all = db.session.query(Third.dept.distinct()).all()
    print(all)
    
    a = []
    len1 = len(all)
    for al in all:
        a.append(Third.query.filter_by(dept = al[0]).all())
    print(a)
    for am in a:
        print(a.index(am))
        for ah in am:
            print(ah.name)
    for al in all:
        print(all.index(al))

    id = User.query.filter_by(username = 'Surejmohan12').first()
    id2 = id.type
    print(id2)
    if(id.type == "Ordinary"):
        pro = Ordinary.query.filter_by(usr_name = 'Surejmohan12').first()
        print(pro)

    if(id.type == "Authority"):
        pro = Authority.query.filter_by(usr_name = 'vidhya1998').first()

    
    if all == []:
        return render_template('current.html',third = "third",profile=pro,id = id2)


    return render_template('current.html',all=all,a=a,profile=pro,id = id2)



@app.route('/user/output')
def output():
    return render_template('output.html')


@app.route('/user/update/profile', methods=['POST'])
def profileupdate():

     if request.method == 'POST':
         typeid = request.form['id']
         if typeid == "Ordinary":
             print(typeid)
             fname = request.form['fname']
             lname = request.form['lname']
             mobile = request.form['mobile']
             email = request.form['email']
             address = request.form['address']
             state = request.form['state']
             city = request.form['city']
             zip = request.form['zip']
             
            

             ordi = Ordinary.query.filter_by(usr_name = 'Surejmohan12').first()
             ordi.fname = fname
             ordi.lname = lname
             ordi.phone = mobile
             ordi.mail = email
             ordi.address = address
             if state != "":
                 ordi.state = state
                 ordi.city = city
             ordi.zip = zip

             db.session.add(ordi)
             db.session.commit()
             flash("Successfully Updated Your Profile",'success')
             return redirect(url_for('current'))

            


         elif typeid == "Authority":
             print(typeid)
             fname = request.form['fname']
             lname = request.form['lname']
             mobile = request.form['mobile']
             email = request.form['email']
             job = request.form['job']
             department = request.form['department']
             

             auth = Authority.query.filter_by(usr_name = 'vidhya1998').first()
             auth.fname = fname
             auth.lname = lname
             auth.phone = mobile
             auth.mail = email
             
             if job != "":
                if job == "Other":
                    job = department
                    auth.job = job
                else:
                    auth.job = job
            
             print(department)

             db.session.add(auth)
             db.session.commit()
             flash("Successfully Updated Your Profile",'success')
             return redirect(url_for('current'))

         


         return typeid



@app.route('/user/update/password', methods=['POST'])
def passwordupdate():

     if request.method == 'POST':
        currentpass = request.form['psw1']
        newpassword = request.form['psw2']
        confpassword = request.form['psw3']

        if newpassword == confpassword:
            user = User.query.filter_by(username = 'Surejmohan12',password = currentpass).first()
            if user:
                if user.password == newpassword:
                    flash("You have Entered same Password, Try some other",'error')
                else:
                    user.password = newpassword
                    db.session.add(user)
                    db.session.commit()
                    flash("Successfully Changed Password",'success')
            else:
                flash("You Entered Wrong Password",'error')

        else:
            flash("New password is not matching",'error')
        
        return redirect(url_for('current'))






@app.route('/user/update/username', methods=['POST'])
def usernameupdate():

    if request.method == 'POST':
        currentuser = request.form['username1']
        newuser = request.form['username2']
        confuser = request.form['username3']

        if newuser == confuser:
          if currentuser == 'Surejmohan12':
            user = User.query.filter_by(username = currentuser).first()
            if user:
              if User.query.filter_by(username = newuser).first():
                  flash("New Username Already exist, Try some other",'error')
                  return redirect(url_for('current'))
              else:
                if user.username == newuser:
                    flash("You have Entered same Username, Try some other",'error')
                    return redirect(url_for('current'))
                else:
                    if user.type == "Ordinary":
                        ord = Ordinary.query.filter_by(usr_name = currentuser).first()
                        oth = Other.query.filter_by(usr_name = currentuser).first()
                        ord.usr_name = newuser
                        oth.usr_name = newuser
                        user.username = newuser
                        db.session.add(user)
                        db.session.add(ord)
                        db.session.add(oth)
                        db.session.commit()
                    
                    if user.type == "Authority":
                        auth = Authority.query.filter_by(usr_name = currentuser).first()
                        oth = Other.query.filter_by(usr_name = currentuser).first()
                        auth.usr_name = newuser
                        oth.usr_name = newuser
                        user.username = newuser
                        db.session.add(user)
                        db.session.add(auth)
                        db.session.add(oth)
                        db.session.commit()
                    
                    
                    flash("Successfully Changed Username",'success')
                    return redirect(url_for('current'))
            else:
                flash("You Entered Wrong Username",'error')
                return redirect(url_for('current'))
          else:
              flash("You Entered Wrong Username",'error')
              return redirect(url_for('current'))

        else:
            flash("New Username is not matching",'error')
            return redirect(url_for('current'))
        
        
    

@app.route('/user/deleteaccount', methods=['POST'])
def delete():

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username ='Surejmohan12',password = password ).first()
        if user:
            delete1 = db.session.query(User).filter(User.username == 'Surejmohan12').first()

            if user.type == "Ordinary":
                delete2 = Ordinary.query.filter(Ordinary.usr_name =='Surejmohan12').first()
                delete3 = Other.query.filter(Other.usr_name == 'Surejmohan12').first()
                count = Count.query.filter(Count.id == 1).first()
                count.Ordinary = count.Ordinary -1

            elif user.type == "Authority":
                delete2 = Authority.query.filter(Authority.usr_name == 'Surejmohan12').first()
                delete3 = Other.query.filter(Other.usr_name == 'Surejmohan12').first()
                count = Count.query.filter(Count.id == 1).first()
                count.Ordinary = count.Ordinary -1
        
            db.session.add(count)
            db.session.delete(delete1)
            db.session.delete(delete2)
            db.session.delete(delete3)
            db.session.commit()

            flash("You have Successfully Deleted Your Account",'success')
            return redirect(url_for('index'))
        
        else: 
            flash("You have entered Wrong Password",'error')
            return redirect(url_for('current'))
        





        return ""




@app.route('/user/result/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='result', filename=filename)



@app.route('/user/upload', methods=['POST'])
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
                flash("Invalid Input File Format; only jpeg or jpg supported",'error')
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
            flash('Maximum Number of Images is 2','error')
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
                flash('Please change image: ' + myimages[i] + ' - it has ' + str(len(detector(image, 1))) + " faces",'error')
                print("Please change image: " + myimages[i] + " - it has " + str(len(detector(image, 1))) + " faces; it can only have one")
                return redirect(url_for('current'))

            _ ,img_shapes, _ = find_faces(image,myimages[i])
            descs[i] = encode_faces(image, img_shapes)[0]
        if request.form['action'] == 'Request_Video':
            np.save('third_image/username.npy', descs)

            dept = request.form['firstList']
            name = request.form['secondList'+ dept]
            date = request.form.get('date')
            start_time = request.form.get('starttime')
            end_time = request.form.get('endtime')


            print(dept)
            print(name)
            print(date)
            print(start_time)
            print(end_time)

            fish = db.session.query(Third.dept.distinct()).all()
            print(fish[int(dept)][0])
            depta = fish[int(dept)][0]

            mass = Third.query.filter_by(dept = depta, name = name).first()
            print(mass.third_party_id)
            ID = mass.third_party_id
            
            send = Other.query.filter_by(usr_name = 'Surejmohan').first()
            send.third_party_issue_id = ID
            send.third_party_pending_order = 'no'
            send.third_party_response = ''
            send.date = date
            send.start_time = start_time
            send.end_time = end_time
            send.no_of_video_request = 1

            db.session.add(send)
            db.session.commit()
            flash("You have successfully submit your request. Please  Wait for the notification Mail ")
            return render_template('output.html' ,output = 1)




           
        elif request.form['action'] == "Upload":
            np.save('train/username.npy', descs)
            descs = np.load('train/username.npy',allow_pickle=True)[()]
            filelist2 = [f for f in os.listdir('video/')]
            for f in filelist2:
                os.remove(os.path.join('video/', f))

            videos = request.files.getlist("videos")
            f = videos[0]
            if len(videos) == 1 :
                    if not allowed_file2(f.filename):
                        flash('Invalid Video Format ;Only Mp4 Supported','error')
                        print("Invalid Video Format ;Only Mp4 Supported")
                        return redirect(url_for('current'))
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_VIDEO'], filename))
                    video_path = 'video/'+ f.filename
                    print(video_path)
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        flash('Video cannot Open','error')
                        print("Video cannot Open")
                        return redirect(url_for('current'))
        
                    _, img_bgr = cap.read()
                    padding_size = 0
                    resized_width = 1920
                    video_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1]))
                    output_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1] + padding_size * 2))

                    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                    writer = cv2.VideoWriter('result/username.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)
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
                flash('Only one video can upload','error')
                print("Only one video can upload")
                return redirect(url_for('current'))






        elif request.form['action'] == "ON":
            np.save('train/username.npy', descs)
            descs = np.load('train/username.npy',allow_pickle=True)[()]
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                flash('Camera is not working','error')
                print("Camera is not working")
                return redirect(url_for('current'))
        
            _, img_bgr = cap.read()
            padding_size = 0
            resized_width = 1360
            video_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1]))
            output_size = (resized_width, int(img_bgr.shape[0] * resized_width // img_bgr.shape[1] + padding_size * 2))

            fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            writer = cv2.VideoWriter('result/username.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)
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

                    last_found = {'name': 'unknown', 'dist': 0.48, 'color': (0,0,255)}

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


#end

#end



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return ""



if(__name__ == "__main__"):
    app.run(debug=True)
