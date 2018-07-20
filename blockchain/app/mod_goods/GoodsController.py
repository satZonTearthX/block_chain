from app import app
from flask import Flask,render_template,g,session
from app.mod_mysql.mysql_service import Mysql_service
from app.mod_qrcode import QrcodeController
@app.route('/signin_sailer_goods')
def signin_sailer_goods():
    return render_template('signin_sailer_goods.html')


@app.route('/signin_sailer_trans')
def signin_sailer_trans():
    return render_template('signin_sailer_trans.html')

@app.route('/signin_sailer_sails')
def signin_sailer_sails():
    path=QrcodeController.create_qrcode()
    return render_template('signin_sailer_sails.html',qrcode=path)

@app.route('/signin_sailer_system')
def signin_sailer_system():
    username = session['username']
    mysql=Mysql_service()
    [name, password, role, email, address, account, credit]=mysql.getUserInfoByUsername(username)
    return render_template('signin_sailer_system.html',username=username,credit=credit)