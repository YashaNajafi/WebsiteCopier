#----------<Library>----------
from flask import Flask,render_template,request,redirect
import random,string,os
#----------<Config>----------
chars = string.ascii_uppercase + string.digits + string.ascii_lowercase

app = Flask(__name__)
app.secret_key = ''.join(random.choices(chars,k=44))
#----------<Route>----------
@app.route("/Download",methods=["POST","GET"])
def Download():
        # -----------<get ip>--------
    ip = ""

    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
        
