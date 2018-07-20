import qrcode
import image

class QrCode:
    def QRMake(self,data, filename):
        qr = qrcode.QRCode(version=6, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        img.save(filename)

    def simpleQRMake(self,data, filename):
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=100,
                           border=8,
                           )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        img.save(filename)