from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

#my database connection
local_server = True
app = Flask(__name__)
app.secret_key = "divyaraj"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/covid'
db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

@app.route("/")
def home():
    return render_template("index.html")

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
