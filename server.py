# 📁 server.py -----

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

from flask import Flask, request ,redirect,url_for, render_template, request, sessions
from sqlalchemy.sql.expression import select
from datetime import datetime
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
from os import path


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)



app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# 👆 We're continuing from the steps above. Append this to your server.py file.

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/")
def home():
    return render_template("home.html", session=session.get('user'))

# 👆 We're continuing from the steps above. Append this to your server.py file.


# create db for tasks  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
dbt = SQLAlchemy(app)

# db model 
class Tasks(dbt.Model):
    id = dbt.Column(dbt.Integer, primary_key=True)
    title = dbt.Column(dbt.String(100), nullable=False)
    content = dbt.Column(dbt.Text, nullable=False)
    date_created = dbt.Column(dbt.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
            return f"Post('{self.title}', '{self.content}')"
dbt.create_all(app=app)





@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    msg = request.form.get('Body')

    # Create reply
    resp = MessagingResponse()
    tasks_lst = list()
    tasks_content = dbt.session.query(Tasks.content).all()
    tasks_title = dbt.session.query(Tasks.title).all()


    for i,  in tasks_content: 
            tasks_lst.append(i)

    if '--Tasks'.lower() in msg:
        resp.message(f'Hello, Your tasks are \n { tasks_lst}')
    elif '--Task completed'.lower() in msg:
        resp.message(f'Task marked as completed!')
    elif '--Contact teacher'.lower() in msg:
        resp.message(f"Your Teacher's contact no. is +1 1111111111 ")
    elif '--help'.lower() in msg:
        resp.message(f"COMMAND: \n --Tasks: To show all remaining tasks \n --Task completed: To mark a task as completed \n --Contact teacher: To contact your teacher \n --Help: Shows a list of commands")


    else: 
        resp.message(f"I'm sorry, but I can't help with that. Type --help to show a list of all commands")



    return str(resp)



# add tasks 
 
@app.route("/tasks", methods=['POST', 'GET'])
def add_tasks():
    if request.method == 'POST':
        name = request.form.get("name")
        body = request.form.get("desc")

        new_task = Tasks(title=name, content=body)
        dbt.session.add(new_task)
        dbt.session.commit()
        return render_template('msg.html')
    else:
        return render_template('tasks.html',)
      

@app.route("/contact", methods=["GET", "POST"])
def contact():
        return render_template("contact.html")
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))