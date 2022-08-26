import time
import cv2
import os
from flask import Flask, render_template,request, Response,url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from tester import default_detection
from reg_user_tester import custom_detection_
from atbswp.atbswp import start_recording
from Face_auth import face_auth,snapshot
from addmotiongesture import addmotiongesture
import json
import sqlite3
#from tester import predicter

app = Flask(__name__, static_url_path='/static')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config["UPLOAD_FOLDER"] = "static/uploads/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

state = "Stop detection"

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('SignUp')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            return 'UserID already exists'
        else:
            return ''
            # raise ValidationError(
            #     'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):

    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

def update_active_user(ges_data):
    global cur_user
    if cur_user=='':
        f = open('username.json', "r")
        userID = json.loads(f.read())
        cur_user = userID['username']
    af = open('activeUser.json', "r")
    active_user_Data = json.loads(af.read())
    data = {
        "user" : cur_user
    }
    data["key"] = ges_data

    active_user_Data[cur_user] = data

    out = open('db.json', "r")
    reg_data = json.loads(out.read())
    for i in range(len(reg_data)):
        if reg_data[i]['name'] == cur_user:
            reg_data[i]["key"] = ges_data
    final_reg_data = json.dumps(reg_data, indent=4)
    json_object = json.dumps(active_user_Data, indent=4)
    with open("db.json", "w") as out:
        out.write(final_reg_data)
    with open("activeUser.json", "w") as outfile:
        outfile.write(json_object)
    user_data = {
        "username": cur_user
    }
    user_data_object = json.dumps(user_data, indent=4)
    with open("username.json", "w") as outfil:
        outfil.write(user_data_object)

def update_registered_user(ges_data):
    with open('db.json') as f:
        reg_database = json.loads(f.read())
        print(reg_database)
    with open('temp_face_encode.json') as a:
        temp_user_data = json.loads(a.read())
    d = {
        "name" :  temp_user_data["username"],
        "encoding": temp_user_data["encoding"],
        "key": ges_data
    }
    reg_database.append(d)
    # updated_db = updated_db[:-1] + "," + str(d) + "]"
    json_object = json.dumps(reg_database, indent=4)
    with open("db.json", "w") as outfile:
        outfile.write(json_object)

def get_active_user(username):
    with open('db.json') as f:
        reg_database = json.loads(f.read())
    active_user_details = {}
    for user in reg_database:
        if user['name']==username:
            active_user_details = user.copy()
    if len(active_user_details)>0:
        af = open('activeUser.json', "r")
        active_user_Data = json.loads(af.read())
        active_user_Data[username] = active_user_details
        json_object = json.dumps(active_user_Data, indent=4)
        with open("activeUser.json", "w") as outfile:
            outfile.write(json_object)
        user_data = {
            "username": username
        }
        user_data_object = json.dumps(user_data, indent=4)
        with open("username.json", "w") as outfil:
            outfil.write(user_data_object)
    else:
        pass


cur_user = ''

@app.route('/')
def index():
    """home page."""
    user_data = {
        "username" : ""
    }
    user_data_object = json.dumps(user_data, indent=4)
    with open("username.json", "w") as outfil:
        outfil.write(user_data_object)
    return render_template('Homepage.html')

@app.route('/default_detection',methods=['GET', 'POST'])

def default_detect():
    """Default page"""
    statesInfo = {
    "state": "active"
}
    json_object = json.dumps(statesInfo, indent=4)
    with open("switchdata.json", "w") as outfile:
        outfile.write(json_object)
    if request.method=='POST':
        try:
            start_recording()
        except:
            return render_template('defaultDetection.html')
    return render_template('defaultDetection.html')
@app.route('/default_statesInfo/<string:statesInfo>',methods=['GET', 'POST'])
def get_statesInfo(statesInfo):
    statesInfo = json.loads(statesInfo)
    print(statesInfo['state'])
    json_object = json.dumps(statesInfo, indent=4)
    with open("switchdata.json", "w") as outfile:
        outfile.write(json_object)
    return "sucessful"
@app.route('/default__video_feed')
def default_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(default_detection(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/registered_user', methods = ['POST', 'GET'])
def registered_user():
    global cur_user
    findface = {
        "findface": "False"
    }
    json_object = json.dumps(findface, indent=4)
    with open("logincapture.json", "w") as outfile:
        outfile.write(json_object)
    error = ''
    f = open('captured_face.json', "r")
    userID = json.loads(f.read())
    result = userID['userID']
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                cur_user = str(form.username.data)
                get_active_user(cur_user)
                return redirect(url_for('gestures'))
            else:
                error = 'Password is incorrect'
        else:
            error = 'User does not exist'
    # logout_user()

    return render_template('login.html',result=result,form=form,error=error)

@app.route('/get_loginCaptureInfo/<string:statesInfo>',methods=['GET', 'POST'])
def get_loginCaptureInfo(statesInfo):
    statesInfo = json.loads(statesInfo)
    print(statesInfo['findface']," flask")
    json_object = json.dumps(statesInfo, indent=4)
    with open("logincapture.json", "w") as outfile:
        outfile.write(json_object)
    return "sucessful"
@app.route('/reg_users__video_feed')
def reg_users_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(face_auth(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/new_user',methods = ['POST', 'GET'])
def new_user():
    form = RegisterForm()
    error = ''
    # if request.method == 'POST':
    #     # check if the post request has the file part
    #     if 'file' not in request.files:
    #         flash('No file part')
    #         return redirect(request.url)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        error = form.validate_username(form.username)
        if error != '':
            return render_template('SignUp.html', form=form, error=error)
        db.session.add(new_user)
        db.session.commit()
        f = open('temp_face_encode.json', "r")
        face_encode = json.loads(f.read())
        new_json = {
            "username": form.username.data,
            "encoding": face_encode['encoding']
        }
        json_object = json.dumps(new_json, indent=4)
        with open("temp_face_encode.json", "w") as outfile:
            outfile.write(json_object)
        return redirect(url_for('reg_gestures'))

    return render_template('SignUp.html',form = form,error = error)
@app.route('/new_user_video_feed')
def new_user_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(snapshot(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/new_user_statesInfo/<string:statesInfo>',methods=['GET', 'POST'])
def new_user_statesInfo(statesInfo):
    statesInfo = json.loads(statesInfo)
    json_object = json.dumps(statesInfo, indent=4)
    with open("snap_state.json", "w") as outfile:
        outfile.write(json_object)
    return "sucessful"

@app.route('/custom_detection',methods=['GET', 'POST'])

def custom_detection():
    """Default page"""
    statesInfo = {
    "state": "active"
}
    volumeInfo = {
        "volume": "muted"
    }
    f = open('username.json', "r")
    userID = json.loads(f.read())
    if userID['username'] == "":
        return render_template('Homepage.html')
    json_object = json.dumps(statesInfo, indent=4)
    with open("switchdata.json", "w") as outfile:
        outfile.write(json_object)
    json_object = json.dumps(volumeInfo, indent=4)
    with open("volume.json", "w") as outfile:
        outfile.write(json_object)
    uf = open('username.json', "r")
    userID = json.loads(uf.read())

    f = open('activeUser.json', "r")
    data = json.loads(f.read())
    key_data = data[userID["username"]]['key']
    return render_template('CustomDetection.html',keys = key_data,username = userID["username"])
@app.route('/custom_statesInfo/<string:statesInfo>',methods=['GET', 'POST'])
def get_customstatesInfo(statesInfo):
    statesInfo = json.loads(statesInfo)
    print(statesInfo['volume'])
    json_object = json.dumps(statesInfo, indent=4)
    with open("volume.json", "w") as outfile:
        outfile.write(json_object)
    return "sucessful"
@app.route('/custom_video_feed')
def custom_video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(custom_detection_(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/custom_detection/profile',methods=['GET', 'POST'])
def profile():
    ges_list = {
    "labels": [],
    "freq": []
}
    f = open('username.json', "r")
    userID = json.loads(f.read())
    test = ''
    error = ''
    password = ''
    connection = sqlite3.connect("database.db")
    crsr = connection.cursor()
    crsr.execute("SELECT * FROM user")
    ans = crsr.fetchall()
    g = open('gestures.json', "r")
    ges_list = json.loads(g.read())
    if request.method == 'POST':
        password = request.form.get('cur_password')
        for row in ans:
            if userID["username"] in row:
                if not bcrypt.check_password_hash(row[-1],password):
                    if len(password)>7:
                        print(password)
                        crsr.execute('''UPDATE user SET password = "{}" WHERE username="{}";'''.format(bcrypt.generate_password_hash(password).decode('utf-8'),userID["username"]))
                        error = "Your new password has been updated!"
                        connection.commit()
                    else:
                        error = "Password must contain atleast 8 characters"
                    # print(bcrypt.check_password_hash(bcrypt.generate_password_hash('vinuvinu').decode('utf-8'),'vinuvinu'))
                    print("password updated!")
                    return render_template('profile.html', username=userID["username"], test=password,error=error,labels=ges_list["labels"],freq=ges_list["freq"])
        connection.commit()
        connection.close()
    print(ges_list["labels"][0:5])
        # return render_template('profile.html', username=userID["username"], test=password)
    return render_template('profile.html',username = userID["username"],test=password,error=error,labels=ges_list["labels"],freq=ges_list["freq"])
@app.route('/reg_gestures',methods=['GET', 'POST'])
def reg_gestures():
    if request.method == 'POST':
        ges1 = request.form.get('ges1')
        ges2 = request.form.get('ges2')
        ges3 = request.form.get('ges3')
        ges4 = request.form.get('ges4')
        ges5 = request.form.get('ges5')
        ges6 = request.form.get('ges6')
        ges7 = request.form.get('ges7')
        ges8 = request.form.get('ges8')
        ges9 = request.form.get('ges9')
        ges10 = request.form.get('ges10')
        ges_data = {
            "ges1" : str(ges1),
            "ges2" : str(ges2),
            "ges3": str(ges3),
            "ges4": str(ges4),
            "ges5": str(ges5),
            "ges6": str(ges6),
            "ges7": str(ges7),
            "ges8": str(ges8),
            "ges9": str(ges9),
            "ges10": str(ges10),
        }
        update_registered_user(ges_data)
        return redirect(url_for('registered_user'))
    return render_template('reg_gestures.html')
@app.route('/gestures',methods=['GET', 'POST'])
def gestures():
    statesInfo = {
        "captured": "False"
    }
    json_object = json.dumps(statesInfo, indent=4)
    with open("ges_captured.json", "w") as outfile:
        outfile.write(json_object)
    f = open('username.json', "r")
    userID = json.loads(f.read())
    a = open('addedGesture.json', "r")
    add_ges = json.loads(a.read())
    # for i in add_ges:
    #     if i['name']==userID['username']:
    if request.method == 'POST':
        ges1 = request.form.get('ges1')
        ges2 = request.form.get('ges2')
        ges3 = request.form.get('ges3')
        ges4 = request.form.get('ges4')
        ges5 = request.form.get('ges5')
        ges6 = request.form.get('ges6')
        ges7 = request.form.get('ges7')
        ges8 = request.form.get('ges8')
        ges9 = request.form.get('ges9')
        ges10 = request.form.get('ges10')
        ges11 = request.form.get('ges11')
        ges_data = {
            "ges1" : str(ges1),
            "ges2" : str(ges2),
            "ges3": str(ges3),
            "ges4": str(ges4),
            "ges5": str(ges5),
            "ges6": str(ges6),
            "ges7": str(ges7),
            "ges8": str(ges8),
            "ges9": str(ges9),
            "ges10": str(ges10),
            "ges11": str(ges11)
        }
        update_active_user(ges_data)
        return redirect(url_for('custom_detection'))
    uf = open('username.json', "r")
    userID = json.loads(uf.read())
    f = open('activeUser.json', "r")
    data = json.loads(f.read())
    try:
        key_data = data[userID["username"]]['key']
    except:
        # return redirect(url_for('registered_user')
        pass
    with open("added_keys.json", "r")as fr:
        new_keys = json.loads(fr.read())
    return render_template('gestures.html',keys = key_data ,new_keys=new_keys)
@app.route('/addMotionGesture',methods=['GET', 'POST'])
def addMotionGesture():
    return render_template('newMotiongesture.html')
@app.route('/addMotionGestureInfo/<string:statesInfo>',methods=['GET', 'POST'])
def addMotionGestureInfo(statesInfo):
    statesInfo = json.loads(statesInfo)
    json_object = json.dumps(statesInfo, indent=4)
    with open("ges_captured.json", "w") as outfile:
        outfile.write(json_object)
    return "sucessful"
@app.route('/addMotionGesture_feed')
def addMotionGesture_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(addmotiongesture(),mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/custom_keys',methods=['GET', 'POST'])
def custom_keys():
    error =""
    if request.method == 'POST':
        key1 = request.form.get('key1')
        key2 = request.form.get('key2')
        key3 = request.form.get('key3')
        if key2=="none":
            if key3 == "none":
                key=key1
            else:
                key=str(key1)+"+"+str(key3)
        else:
            if key3 == "none":
                key=str(key1)+"+"+str(key2)
            else:
                key = str(key1) + "+" + str(key2) + "+" + str(key3)


        key=key.lower()
        with open("added_keys.json") as f:
            cust_keys = json.loads(f.read())
        if key not in cust_keys:
            cust_keys.append(key)
            json_object = json.dumps(cust_keys, indent=4)
            with open("added_keys.json", 'w') as fw:
                fw.write(json_object)
            return redirect(url_for('gestures'))
        else:
            error = "shortcut already exists"
            return render_template('custom_keys.html', error=error)
    return render_template('custom_keys.html')

if __name__=='__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=80)