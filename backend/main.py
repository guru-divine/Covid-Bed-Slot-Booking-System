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

class Hospitaldata(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    normalbed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    ventbed = db.Column(db.Integer)

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
            session['role'] = 'a'
            return redirect(url_for('addHospitalUser'))
        else:
            flash("Invalid Credentials", "danger")
            return render_template("admin.html")
    
    return render_template("admin.html")

@app.route('/logoutadmin')
def logoutadmin():
    session.pop('admin')
    session.pop('role')
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
    if 'user' not in session:
        flash("Login first!", "danger")
        return redirect('/login')
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

# Define a function to send email within the application context
def send_email(user):
    with app.app_context():
        msg = Message('DIVINE CARE CENTER',
                      sender=params['gmail-user'],
                      recipients=[user.email],
                      body=f"Thanks for Joining Us.\n\n\n"
                           f"Your Login Credentials are: \n\n"
                           f"\tUsername: {user.hcode}\n"
                           f"\tEmail: {user.email}\n"
                           f"\tPassword: {user.pswd}\n\n"
                           f"Do not share these credentials with anyone. \n\n\n"
                           f"You are kindly requested to update the information of your hospital at your earliest convenience. This will greatly facilitate the smooth functioning and efficient operation of our systems. Thank you for your cooperation.\n\n"
                           f"This is auto-generated email. Please do not reply."
                    )
        mail.send(msg)

@app.route('/addHospitalUser', methods=['POST', 'GET'])
def addHospitalUser():
    if('admin' in session and session['admin'] == params['username']):
        unauthorised_users = Hospitaluser.query.filter_by(authorised=0).all()
        if request.method == 'POST':
            user_id = request.form.get('hid')
            user = Hospitaluser.query.filter_by(id=user_id).first()
            if user and user.id == int(user_id):
                user.authorised = 1
                db.session.commit()
                send_email(user)

            return redirect('/addHospitalUser')

        return render_template("addHospitalUser.html", unauthorised_users=unauthorised_users)
    else:
        flash("Login and Try Again", "warning")
        return redirect('/admin')


@app.route('/add_authorised', methods=['POST'])
def add_authorised():
    if(request.method == 'POST'):
        user_id = request.form.get('user_id')
        user = Hospitaluser.query.get(user_id)
        user = Hospitaluser.query.filter_by(id=user_id).first()
        if user and user.id == user_id:
            user.authorised = 1
            db.session.commit()
    return redirect('/addHospitalUser')

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        hcode = request.form.get('hcode')
        email = request.form.get('email')
        pswd = request.form.get('pswd')

        hospital = Hospitaluser.query.filter_by(hcode=hcode, email=email, pswd=pswd).first()
        if hospital:
            if hospital.authorised == 1:
                # login_user(hospital)
                session['hospital'] = hcode
                session['role'] = 'h'
                return redirect('/')
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
        hospital_user = Hospitaluser.query.filter_by(hcode=session['hospital']).first()
        hospital_data = Hospitaldata.query.filter_by(hcode=session['hospital']).first()
        return render_template("hospitaldetails.html", hospital_user=hospital_user, hospital_data = hospital_data)
    else:
        flash("Login and Try Again", "warning")
        return redirect('/hospitallogin')
    
@app.route('/updatehospitalinfo', methods=["POST", "GET"])
def updatehospitalinfo():
    if 'hospital' not in session:
        flash("Login first!", "danger")
        return redirect('/hospitallogin')
    cur_user = Hospitaldata.query.filter_by(hcode=session['hospital']).first()
    if request.method == "POST":
        normalbed = request.form.get('normalbed')
        icubed = request.form.get('icubed')
        ventbed = request.form.get('ventbed')

        user = Hospitaldata.query.get(cur_user.id)
        user.normalbed = normalbed
        user.icubed = icubed
        user.ventbed = ventbed
        db.session.commit()
        return redirect('/hospitaldetails')

    
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
