from flask import Flask, request, redirect, render_template, flash
from flask.helpers import url_for
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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(20))
    pswd = db.Column(db.String(20))
    dob = db.Column(db.Date)

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        pswd = request.form.get('pswd')

        user = User.query.filter_by(srfid=srfid).first()
        if(user and user.srfid==srfid):
            flash("User already exists", "warning")
            return render_template("usersignup.html") 
        print(srfid, email, dob, pswd)
        new_user = User(srfid=srfid, email=email, dob=dob, pswd=pswd)
        db.session.add(new_user)
        db.session.commit()
        return render_template()
    # flash("SignUp successful", "success")
    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        srfid = request.form.get('srf')
        pswd = request.form.get('pswd')

        user = User.query.filter_by(srfid=srfid).first()
        print(user)
        # return render_template("index.html")
        if(user and user.pswd==pswd):
            login_user(user)
            # flash("Login Successful", "success")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html") 
    
    return render_template("userlogin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "success")
    return redirect(url_for('login'))

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if request.method == "POST":
        oldPassword = request.form.get('oldPassword')
        newPassword = request.form.get('newPassword')
        reNewPassword = request.form.get('reNewPassword')
        if oldPassword == current_user.pswd and newPassword==reNewPassword:
            user = User.query.get(current_user.id)
            user.pswd = newPassword
            db.session.commit()
            flash("Password Changed Successfully", "success")
            return render_template("usersettings.html")
        else:
            if oldPassword != "":
                flash("Password didn't match. Try again!", "alert")
            return render_template("usersettings.html")
        
    return render_template("usersettings.html")

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
