import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, request , jsonify, make_response
from sqlalchemy import Column, Integer, String
import jwt
import datetime
from functools import wraps
from config import *
import uuid


app = Flask(__name__)

app.config['SECRET_KEY'] = 'c26f180cc68f419f89cf4c76f3fd346e'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    id                  = Column(Integer, primary_key=True)
    public_id           = Column(String(50), unique=True)
    email               = Column(String(40))
    name                = Column(String(50))
    password            = Column(String(80))
    location            = Column(String(80))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        token_value = request.cookies.get('token')

        if token_value:
            token = token_value

        if token is None:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except: 
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
    

@app.route('/')
def users_get():
    return render_template("login.html")

@app.route('/', methods = ["POST"])
def users_post():
    email = request.form['email']
    password = request.form['password']
    hashed_password=hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = User.query.filter_by(email = email).first()


    if not user:
        message = "Invalid Credentials"
        return render_template("login.html", message = message)
         
    if user.password == hashed_password:
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=120)}, 
        app.config['SECRET_KEY'])

        resp = make_response(redirect("/dashboard"))
        resp.set_cookie('token', token)
        
        return resp
    else:
        message = "Password did not match"
        return render_template("login.html", message = message)

@app.route('/register')
def user_create():
    return render_template("register.html")

@app.route('/register', methods = ["POST"])
def user_create_post():
    unhashed_password = request.form['password']
    data = {
        'name' : request.form['name'],
        'email' : request.form['email'],
        'location' : request.form['location'],
        'public_id' : str(uuid.uuid4()),
        'password' :  hashlib.sha256(unhashed_password.encode('utf-8')).hexdigest()
    }
    users = User(**data)
    db.session.add(users)
    db.session.commit()
    

    return render_template("register.html")

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    return render_template("dashboard.html", current_user = current_user)



if __name__ == '__main__':
    app.run(debug=True)