from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

#my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "divyaraj"

# this is for getting the unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/covid'
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(20))
    pswd = db.Column(db.String(20))
    dob = db.Column(db.Date)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        pswd = request.form.get('pswd')

        # print(srfid, email, dob, pswd)
        new_user = User(srfid=srfid, email=email, dob=dob, pswd=pswd)
        db.session.add(new_user)
        db.session.commit()
        return f'USER ADDED with {pswd}'
    
    return render_template("usersignup.html")

#testing whether db is connected
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return 'My Database is Connected'
    except Exception as e:
        print(e)
        return f'My Databse is not Connected {e}'

app.run(debug=True)
