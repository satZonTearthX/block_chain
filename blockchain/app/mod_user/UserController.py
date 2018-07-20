from flask import request,redirect,url_for,render_template,g,session
from app.mod_mysql.mysql_service import Mysql_service
from app import app


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        # add into the mysql
        mysql=Mysql_service()
        mysql.register(username,password,email,role)
        return redirect(url_for('login'))

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template('sign_in.html')
    else:
        username=request.form['username']
        password=request.form['password']
        role=request.form['role']
        mysql = Mysql_service()
        [name, real_pass, role, email, address, account, credit]=mysql.getUserInfoByUsername(username)
        if password==real_pass:
            print('role')
            if role == 'Product':
                session['username'] = name
                return render_template('signin_sailer_index.html')
        else:
            print("fail")
            return render_template('sign_in.html', res="fail")



#transport

#goods
#search_for_commodity_byseller
