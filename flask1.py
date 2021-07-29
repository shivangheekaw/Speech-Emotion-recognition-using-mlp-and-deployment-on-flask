from flask import Flask,render_template,request,session,g,url_for
from werkzeug.utils import secure_filename
import json
import MySQLdb
import pickle
import random
import sys
import librosa
import numpy as np
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

# UPLOAD_FOLDER = r"C:\Users\pc\Downloads"
# ALLOWED_EXTENSIONS = {'wav'}
with open('C:\\Users\\pc\\PycharmProjects\\pythonProject1\\templates\\config.json', 'r') as c:
    params=json.load(c)["params"]

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/speech_db'
db = SQLAlchemy(app)
MySQLdb.connect(host="localhost",user="root",password="",db="speech_db")


# signup user info gets saved in this class
class User(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    ph_no = db.Column(db.String(12), nullable=False)
    pswd = db.Column(db.String(12), nullable=False)
    age = db.Column(db.String(3), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(30), nullable=False)


# app.config['UPLOAD_FOLDER'] = "UPLOAD_FOLDER"

model=pickle.load(open('model.model','rb'))


def extract_feature(file_name, mfcc, chroma, mel):

    X, sample_rate = librosa.load(os.path.join(file_name), res_type='kaiser_fast')
    if chroma:
        stft = np.abs(librosa.stft(X))
    result = np.array([])
    if mfcc:
        mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
        result = np.hstack((result, mfccs))
    if chroma:
        chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
        result = np.hstack((result, chroma))
    if mel:
        mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T, axis=0)
        result = np.hstack((result, mel))
    return result


## Route for home page
@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return render_template('index.html',name1=username,link1="#", name2="Logout", link2="/logout", name3="Check Emotion", link3="/speechrecog")

        #return render_template('index.html', name1="Login", link1="/LoginFront.html", name2="Signup",link2="/SignupFront.html")
    else:
        return render_template('index.html', name1="Login", link1="/LoginFront.html", name2="Signup",link2="/SignupFront.html", name3="Home", link3="/")


    #return render_template('index.html', name1="Login", link1="/LoginFront.html", name2="Signup", link2="/SignupFront.html")



@app.route('/SignupFront', methods =['GET', 'POST'])
def signupfront():
    if(request.method=='POST'):
        First_Name=request.form.get('First_Name')
        Last_Name = request.form.get('Last_Name')
        email = request.form.get('email')
        mobileNumber = request.form.get('mobileNumber')
        age = request.form.get('age')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')
        if(password == confirmPassword):
            entry = User(fname=First_Name, lname=Last_Name, email=email, ph_no=mobileNumber, age=age, gender=gender, pswd=password)
        db.session.add(entry)
        db.session.commit()

    return render_template('/LoginFront.html')


@app.route('/SignupFront.html')
def signupfront1():
    return render_template('SignupFront.html')


@app.route('/LoginFront.html')
def loginfront():
    return render_template('LoginFront.html')


@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('LoginFront.html')



@app.route('/Login', methods =['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        peter=User.query.filter_by(email=email).first()

        if (email==peter.email):
            username=peter.fname
            session['username']=username
            return render_template('SpeechrecogFront.html',info=username)
        else:
            return render_template('SignupFront.html')



@app.route('/uploader', methods =['GET', 'POST'])
def uploader():
    if (request.method == 'POST'):
        f=request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        #return "uploaded"
        path=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))

        feature=np.array([extract_feature(path, mfcc=True, chroma=True, mel=True)])
        #feature= extract_feature(path, mfcc=True, chroma=True, mel=True)
        #X.append(feature)
        y_pred = model.predict(feature)

#enter data simultaneously into userhistory table
        username = session["username"]

        path1=path[50:]


        entry = User_history(fname=username, audio_file=path, emotion=y_pred[0], playing_path=path1)
        db.session.add(entry)
        db.session.commit()

        s = ""
        if y_pred[0] == "angry":
            s = "Hey!What happened? Why are you angry today?"
        elif y_pred[0] == "fear":
            s = "Buddy!don't get scared!!!"
        elif y_pred[0] == "happy":
            s = "Be happy always!!!"
        elif y_pred[0] == "calm":
            s = "Feeling calm today!!!"
        elif y_pred[0] == "disgust":
            s = "Don't feel disgust today!!! Be happy!!!"
        elif y_pred[0] == "neutral":
            s = "Great,feeling neutral!!!"
        elif y_pred[0] == "sad":
            s = "why are you sad today!!!"
        elif y_pred[0] == "suprise":
            s = "what made you feel Suprised?"



        #return render_template('SpeechrecogFront.html', info=y_pred)
        #return render_template('ans.html', info=y_pred)
        return render_template('ans.html', info=s, name=username)



class User_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    audio_file = db.Column(db.String(1000), nullable=False)
    emotion = db.Column(db.String(20), nullable=False)
    #date = db.Column(db.String(30), nullable=True)
    playing_path = db.Column(db.String(200), nullable=False)



@app.route('/user_history', methods =['GET'])
def userhistory():
    username= session["username"]
    user_history=User_history.query.filter_by(fname=username).all()[0:5]

    return render_template('history.html',user_history=user_history, name=username)



@app.route('/ContactUs.html')
def contactus():
    return render_template('ContactUs.html')


class Contact_form_info(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(1000), nullable=False)
    comments = db.Column(db.String(20), nullable=False)


@app.route('/contact', methods =['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('your_name')
        email = request.form.get('your_email')
        phone = request.form.get('your_phone')
        comments = request.form.get('comments')

        entry = Contact_form_info(name=name, email=email, phone=phone, comments=comments)
        db.session.add(entry)
        db.session.commit()

    return render_template('index.html')



@app.route('/speechrecog')
def speechrecog():
    username = session["username"]
    return render_template('SpeechrecogFront.html', info=username)




















## Route for results
@app.route("/predict",methods=['POST','GET'])
def results():
    """
    This route is used to save the file, convert the audio to 16000hz monochannel,
    and predict the emotion using the saved binary model
    """
    f = request.files['file']

    filename = secure_filename(f.filename)
    f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))


    wav_file_pre  = os.listdir("./audio")[0]
    wav_file_pre = f"{os.getcwd()}/audio/{wav_file_pre}"

    model = pickle.load(open(f"{os.getcwd()}/model.model", "rb"))
    x_test =extract_feature(wav_file_pre, mfcc=True, chroma=True, mel=True)
    y_pred=model.predict(np.array([x_test]))
    os.remove(wav_file_pre)
    return render_template('index.html', value=y_pred[0])


if __name__ == "__main__":
    app.debug = True
    app.run()
