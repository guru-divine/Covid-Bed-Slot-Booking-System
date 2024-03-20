from flask import Flask, request, redirect, render_template, flash, session, render_template_string
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager, current_user
import json
from flask_mail import Mail, Message
# from werkzeug.security import generate_password_hash, check_password_hash

#my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "divyaraj"

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-pswd']
)
mail = Mail(app)

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
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(20))
    email = db.Column(db.String(20))
    pswd = db.Column(db.String(20))
    dob = db.Column(db.Date)

class Hospitaluser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    hname = db.Column(db.String(100))
    hlink = db.Column(db.String(100))
    email = db.Column(db.String(20))
    pswd = db.Column(db.String(20))
    authorised = db.Column(db.Integer)

class Hospitaldetails(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    nbed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        dob = request.form.get('dob')
        pswd = request.form.get('pswd')

        user = User.query.filter_by(srfid=srfid).first()
        if(user and user.srfid==srfid):
            flash("User already exists", "warning")
            return render_template("usersignup.html") 
        # print(srfid, fname, lname, email, dob, pswd)
        new_user = User(srfid=srfid, fname=fname, lname=lname, email=email, dob=dob, pswd=pswd)
        db.session.add(new_user)
        db.session.commit()
        return render_template("index.html")
    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        srfid = request.form.get('srf')
        pswd = request.form.get('pswd')

        user = User.query.filter_by(srfid=srfid).first()
        if(user and user.pswd==pswd):
            session['user'] = srfid
            session['role'] = 'u'
            return redirect(url_for('home'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html") 
    
    return render_template("userlogin.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        print(username, password)
        if(username == params['username']  and password == params['password']):
            session['admin'] = username
            return redirect(url_for('addHospitalUser'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template("admin.html")
    
    return render_template("admin.html")

@app.route('/logoutadmin')
def logoutadmin():
    session.pop('admin')
    flash("Logout Successful", "success")
    return redirect('/admin')


@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('role')
    flash("Logout Successful", "success")
    return redirect(url_for('login'))

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    cur_user = User.query.filter_by(srfid=session['user']).first()
    # cur_user = User.query.first(session['user']) 
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
        
    return render_template("usersettings.html", cur_user=cur_user)


@app.route('/addHospitalUser', methods=['POST', 'GET'])
def addHospitalUser():
    if('admin' in session and session['admin'] == params['username']):
        if request.method == "POST":
            hname = request.form.get('hname')
            hcode = request.form.get('hcode')
            hlink = request.form.get('hlink')
            email = request.form.get('email')
            pswd = request.form.get('pswd')
            print(hname, hcode, hlink, email, pswd)
            user = Hospitaluser.query.filter_by(hcode=hcode).first()
            if(user and user.hcode == hcode):
                flash("User already exists", "warning")
                return render_template("addHospitalUser.html")
            new_user = Hospitaluser(hname=hname, hcode=hcode, hlink=hlink, email=email, pswd=pswd, authorised=1)
            db.session.add(new_user)
            db.session.commit()

            msg = Message('COVID CARE CENTER',
                sender=params['gmail-user'],
                recipients=[email],
                body=f"Thanks for Joining Us.\n\n\n"
                     f"Your Login Credentials are: \n\n"
                     f"\tUsername: {hcode}\n"
                     f"\tEmail: {email}\n"
                     f"\tPassword: {pswd}\n\n"
                     f"Do not share these credentials with anyone. \n"
                     f"This is auto-generated email. Please do not reply"
                  )
            mail.send(msg)

            flash("Hospital Added", "info")
            return render_template("addHospitalUser.html")
            # pass

        return render_template("addHospitalUser.html")
    else:
        flash("Login and Try Again", "warning")
        return redirect('/admin')

    # return render_template("addHospitalUser.html")

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        hcode = request.form.get('hcode')
        email = request.form.get('email')
        pswd = request.form.get('pswd')

        hospital = Hospitaluser.query.filter_by(hcode=hcode, email=email, pswd=pswd).first()
        if hospital:
            if hospital.authorised == 1:
                login_user(hospital)
               

                session['hospital'] = hcode
                session['role'] = 'h'
                return redirect('/hospitaldetails')
            else:
                flash("Please wait for the Admin to approve", "danger")
                return render_template("hospitallogin.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")

@app.route('/logouthospital')
def logouthospital():
    session.pop('hospital')
    session.pop('role')
    flash("Logout Successful", "success")
    return redirect('/hospitallogin')

@app.route('/hospitalapply', methods=["POST", "GET"])
def hospitalapply():
    if request.method == "POST":
        hname = request.form.get('hname')
        hcode = request.form.get('hcode')
        hlink = request.form.get('hlink')
        email = request.form.get('email')
        pswd = request.form.get('pswd')
        user = Hospitaluser.query.filter_by(hcode=hcode).first()
        if(user and user.hcode==hcode):
            flash("Hospital already exists!", "danger")
            return render_template("hospitalapply.html")
        else:
            new_user = Hospitaluser(hname=hname, hcode=hcode, hlink=hlink, email=email, pswd=pswd, authorised=0)
            db.session.add(new_user)
            db.session.commit()
            return render_template_string("""
                <script>
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 5000);
                </script>
                """)
        
    return render_template("hospitalapply.html")

@app.route("/hospitaldetails", methods=["POST", "GET"])
def hospitaldetails():
    if 'hospital' in session:
        return render_template("hospitaldetails.html")
    else:
        flash("Login and Try Again", "warning")
        return redirect('/hospitallogin')
    
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
