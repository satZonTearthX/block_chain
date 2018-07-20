from flask import Flask,render_template
import os
from datetime import timedelta
app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY']=os.urandom(24)   #设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=7)

@app.route('/')
def hello_world():
    return render_template('index.html')

from app.mod_user.UserController import *
from app.mod_qrcode.QrcodeController import *
from app.mod_goods.GoodsController import *
