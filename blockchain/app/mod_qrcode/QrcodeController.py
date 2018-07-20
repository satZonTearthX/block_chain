from app import app
from flask import request,render_template
from app.mod_qrcode.qrcode import QrCode

@app.route('/qrcode',methods=['POST','GET'])
def create_qrcode():
    print(request.get_data())
    #product_id = request.form['product_id']
    product_id='qrcode'
    data = {
        'product_id':product_id
    }
    path='app/static/img/'+product_id+'.jpg'
    QrCode().simpleQRMake(data,path)
    return "/static/img/"+product_id+'.jpg'