import email
import smtplib
import time 
import base64
import re
import os

#เข้ารหัสจาก text เป็น base64
def text_to_encoded_words(text):
    byte_string = text.encode('utf-8')
    encoded_text = base64.b64encode(byte_string)
    return "{encoded_text}".format(encoded_text=encoded_text.decode('ascii'))

#แปลงไฟล์เป็นรหัส base64
def file_to_encoded_words(path):
    byte_file = open(path, 'rb').read() #อ่ายไฟล์
    encoded_text = base64.b64encode(byte_file) #เข้ารหัส base64
    return "{encoded_text}".format(encoded_text=encoded_text.decode('ascii')) #แปลงชนิดข้อมูลจาก byte เป็น ascii

class Mail:
    def __init__(self,email,pwd):
        self.email = email
        self.send = smtplib.SMTP('smtp.gmail.com:587')
        self.send.ehlo()
        self.send.starttls()
        self.send.login(email,pwd)

    def Send(self,Subject='',To='',Text='',Attachment = ''):
        Subject = '=?utf-8?b?%s?='%text_to_encoded_words(Subject) #แปลงตัวหนังสือที่เป็น subject ให้เป็น base64
        From    = self.email
        Text    = text_to_encoded_words(Text) #แปลงตัวหนังสือที่เป็น content ให้เป็น base64

        #ในกรณีที่ไม่มีไฟล์แนบ
        if Attachment == '':
            from1 = self.MailForm(0) #ดึงรูปแบบข้อความที่ต้องส่ง
            msg = from1.format(_from=From,_subject=Subject,_to=To,_text=Text) #เรียบเรียงข้อความที่ต้องส่ง
        #ในกรณีที่มีไฟล์แนบมาด้วย
        else:
            FileText = file_to_encoded_words(Attachment) #เปลี่ยนไฟล์เป็นตัวอักษรที่เข้ารหัส base64
            FileName  = Attachment.split('/')[-1] #ดึงชื่อไฟล์ออกมา
            FileName  = '=?UTF-8?B?%s?='%text_to_encoded_words(FileName) #แปลงชื่อไฟล์เป็น base64
            from1 = self.MailForm(1) #ดึงรูปแบบข้อความที่ต้องส่ง
            msg = from1.format(_from=From,_subject=Subject,_to=To,_text=Text,_filename=FileName,_filetext=FileText) #เรียบเรียงข้อความที่ต้องส่ง
        try:
            self.send.sendmail(From,To,msg) #ส่งข้อความออกไปยังเซิฟเวอร์
            return True
        except:
            return False

    def MailForm(self,select):
    	#ฟอร์มที่ไม่มีไฟล์แนย
        if select == 0:
            from1 = 'By lucifer : 1.0\n'
            from1 += 'From: {_from}\n'
            from1 += 'Subject: {_subject}\n'
            from1 += 'To: {_to}\n'
            from1 += 'Content-Type: text/plain; charset="utf-8"\n'
            from1 += 'Content-Transfer-Encoding: base64\n\n'
            from1 += '{_text}\n\n'
            return from1
            
        #ฟอร์มที่มีไฟล์แนบ
        elif select == 1:
            from1 = 'Content-Type: multipart/mixed; boundary="===============0000000000000000000=="\n'
            from1 += 'By lucifer : 1.0\n'
            from1 += 'From: {_from}\n'
            from1 += 'To: {_to}\n'
            from1 += 'Subject: {_subject}\n\n'
            from1 += '--===============0000000000000000000==\n'
            from1 += 'Content-Type: text/plain; charset="utf-8"\n'
            from1 += 'By lucifer : 1.0\n'
            from1 += 'Content-Transfer-Encoding: base64\n\n'
            from1 += '{_text}\n\n'
            from1 += '--===============0000000000000000000==\n'
            from1 += 'Content-Type: application/octet-stream\n'
            from1 += 'By lucifer : 1.0\n'
            from1 += 'Content-Transfer-Encoding: base64\n'
            from1 += 'Content-Disposition: attachment; filename="{_filename}"\n\n'
            from1 += '{_filetext}\n\n'
            from1 += '--===============0000000000000000000==--\n\n'
            return from1
        else:
            return ''

To = 'example@gmail.com'
Text = 'Hello World'
mail = Mail('your_mail@gmail.com','your_password')
mail.Send(Subject='ทดสอบการส่งเมล',To=To,Text=Text,Attachment = './ทดสอบ.txt')
    