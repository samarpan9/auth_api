import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, request , jsonify, make_response, session
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from config import *


app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'

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
        
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if token is None:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            print("hello")
            data = jwt.decode(token, app.config['SECRET_KEY'])
            print("current user")

            current_user = User.query.filter_by(public_id=data['public_id']).first()
            print("current user")
            print(current_user)
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

    print("this is user",user)
    if not user:
        message = "Invalid Credentials"
        return render_template("login.html", message = message)
         
    if user.password == hashed_password:
        print(user.public_id)
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 
        app.config['SECRET_KEY'])
        print("token is:", token)
    return render_template("login.html")

@app.route('/register')
def user_create():
    return render_template("register.html")

@app.route('/dashboard')
@token_required
def dashboard():
    return render_template("dashboard.html")



if __name__ == '__main__':
    app.run(debug=True)