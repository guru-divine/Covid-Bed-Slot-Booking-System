from flask import Flask
from flask_mail import Mail, Message
import json

app = Flask(__name__)
app.secret_key = "divyaraj"

# Load email configuration from config.json
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# Configure Flask-Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-pswd']
)
mail = Mail(app)

# Define a function to send email within the application context
def send_email():
    with app.app_context():
        msg = Message('DIVINE CARE CENTER',
                      sender=params['gmail-user'],
                      recipients=['divya.raj5935@gmail.com'],
                      body=f"Thanks for Joining Us.\n\n\n"
                           f"Your Login Credentials are: \n\n"
                           f"\tUsername: Divya Raj\n"
                           f"\tEmail: divya.raj5935@gmail.com\n"
                           f"\tPassword: SexandCity\n\n"
                           f"Do not share these credentials with anyone. \n\n\n"
                           f"You are kindly requested to update the information of your hospital at your earliest convenience. This will greatly facilitate the smooth functioning and efficient operation of our systems. Thank you for your cooperation.\n\n"
                           f"This is auto-generated email. Please do not reply."
                    )
        mail.send(msg)

# Call the function to send email
send_email()
