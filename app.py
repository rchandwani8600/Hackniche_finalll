from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import UserMixin
from sqlalchemy import create_engine
# from datetime import datetime, date
from werkzeug.utils import secure_filename

app = Flask(__name__)
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
            return redirect(url_for("cllg"))
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
    print("x")
    if request.method == "POST":
        print("a")
        hname = request.form.get('hname')
        mode = request.form.get('college')
        address = request.form.get('loc')
        desc = request.form.get('desc')
        date = request.form.get('date')
        time = request.form.get('time')
        qual = request.form.get('eval')
        exp = request.form.get('yrs')
        skills = request.form.get('skills')
        print(5)
        number = request.form.get('no')
        print(3)
        

        

        hack = Hackathon(hackathon = hname, mode= mode, address = address,desc = desc,date=date,time=time,qual=qual,exp=exp,skills=skills,number=number)
        print(hack)
        db.session.add(hack)
        print(1)
        db.session.commit()
        print(2)
        return redirect(url_for("login"))
    return render_template("cllg.html")

@app.route('/hack', methods=["GET"])
def hack():
    hackathons = Hackathon.query().all()
    print(hackathons)


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)