from flask import Flask,render_template,flash, redirect,url_for,session,logging,request, Response
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import UserMixin
from sqlalchemy import create_engine
# from datetime import datetime, date
from werkzeug.utils import secure_filename
from config import config
from formbuilder import formLoader
import json
import face_recognition
import os, sys
import cv2.cv2 as cv
import numpy as np
import math


app = Flask(__name__,static_folder='src')
app.secret_key = 'Sh3r1n4Mun4F'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)

class user(db.Model,UserMixin):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))

class Hackathon(db.Model):
    __tablename__="hackathon"
    id = db.Column(db.Integer, primary_key=True)
    hackathon = db.Column(db.String(100))
    mode = db.Column(db.String(20))
    address = db.Column(db.String(600))
    desc = db.Column(db.String(1000))
    date = db.Column(db.String(30))
    time = db.Column(db.String(20))
    qual = db.Column(db.String(600))
    exp = db.Column(db.String(600))
    skills = db.Column(db.String(600))
    number = db.Column(db.Integer)
    evaluation = db.Column(db.String(100))

class Participant(db.Model,UserMixin):
    __tablename__="participants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    tname = db.Column(db.String(80))
    code = db.Column(db.String(6))


@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        login = user.query.filter_by(username=uname, password=passw).first()
        print(login)
        if login is not None:
            # flash("Successfully logged in!")
            return redirect(url_for("list"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = user(username = uname, email = mail, password = passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/cllg", methods=["GET", "POST"])
def cllg():
    evaluation = ""
 
    if request.method == "POST":
        
        hname = request.form.get('hname')
        mode = request.form.get('college')
        address = request.form.get('loc')
        desc = request.form.get('desc')
        date = request.form.get('date')
        time = request.form.get('time')
        qual = request.form.get('eval')
        exp = request.form.get('yrs')
        skills = request.form.get('skills')
        evaluation = request.form.get('evaluation')
        number = request.form.get('no')
       
        

        

        hack = Hackathon(hackathon = hname, mode= mode, address = address,desc = desc,date=date,time=time,qual=qual,exp=exp,skills=skills,number=number,evaluation=evaluation)
        print(hack)
        db.session.add(hack)
        
        db.session.commit()
        print(evaluation)

        if evaluation=='coding':
            return redirect(url_for("coding"))
        elif (evaluation=='quiz'):
             return redirect(url_for("quiz"))
        else:  
            return redirect(url_for("resume"))
        
    return render_template("cllg.html")


@app.route('/coding')
def coding():
     return render_template("coding.html")


@app.route('/quiz')
def quiz():

	return render_template('quiz.html', base_url=config['base_url'])

@app.route('/save', methods=['POST'])
def save():
	if request.method == 'POST':
		formData = request.form.get('formData')

		if formData == 'None':
			return 'Error processing request'

		session['form_data'] = formData

		return 'tes'

@app.route('/render')
def render():
    if not session['form_data']:
             redirect('/')
             print("g")
    form_data = session['form_data']
    session['form_data'] = None
    form_loader = formLoader(form_data, '{0}/submit'.format(config['base_url']))
    render_form = form_loader.render_form()
    return render_template('render.html', render_form=render_form)

@app.route('/submit', methods=['POST'])
def submit():
     if request.method == 'POST':
        form = json.dumps(request.form)
        return form




@app.route('/resume')
def resume():
     return render_template("resume.html")

@app.route('/hack', methods=["GET"])
def hack():
    hackathons = Hackathon.query().all()
    print(hackathons)

@app.route('/create',methods=['GET','POST'])
def create():
   

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        tname = request.form.get('tname')
        code = request.form.get('code')

       

        part = Participant(name = name, email = email, tname=tname,code=code)
        db.session.add(part)
        db.session.commit()

        return redirect(url_for("resume_template"))

    return render_template("create.html")


@app.route('/join',methods=['GET','POST'])
def join():
    if request.method=='POST':
         return redirect(url_for("resume_template"))

    return render_template("join.html")


@app.route('/resume_1')
def resume_1():
    return render_template("resume_1.html")

@app.route('/resume_2')
def resume_2():
    return render_template("resume_2.html")

@app.route('/resume_template')
def resume_template():
    return render_template("resume_template.html")

@app.route('/list')
def list():
    return render_template("hackathons_list.html")
@app.route('/hack_details/<id>')

def hack_details(id):
    return render_template("hackathon.html")

def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        for image in os.listdir('static/faces'):
            face_image = face_recognition.load_image_file(f"static/faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]

            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)
        print(self.known_face_names)
    
    def run_recognition(self):
        video_capture = cv.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('Video source not found...')

        while True:
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    confidence = 'Unknown'

                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Create the frame with the name
                cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv.FILLED)
                cv.putText(frame, name, (left + 6, bottom - 6), cv.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            # Display the resulting image
            cv.imshow('Face Recognition',frame)

            # Hit 'q' on the keyboard to quit!
            if cv.waitKey(1) == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv.destroyAllWindows()

@app.route("/quizzing")
def quiz():
    fr = FaceRecognition()
    fr.run_recognition()
    return render_template("quizzing.html")

if __name__ == '__main__':
    app.run(debug= True)
    


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)