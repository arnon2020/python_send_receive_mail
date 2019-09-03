#https://www.youtube.com/watch?v=tUl98qhTPAs
#https://github.com/byt3bl33d3r/gcat
import email
import imaplib
import smtplib
import time 
import base64, quopri
from urllib.parse import unquote
import re
import os

def text_to_encoded_words(text):
    byte_string = text.encode('utf-8')
    encoded_text = base64.b64encode(byte_string)
    return "{encoded_text}".format(encoded_text=encoded_text.decode('ascii'))

def file_to_encoded_words(path):
    byte_file = open(path, 'rb').read()
    encoded_text = base64.b64encode(byte_file)
    return "{encoded_text}".format(encoded_text=encoded_text.decode('ascii'))

#กรอง unicode ที่ตืดมากับเนื้อหาออกไป
def string_filer(string):
    data = encoded_words_to_text(string) #เปลี่ยนข้อมูลที่เป็น base64 ให้เป็นเนื้อหาที่อ่านได้
    Find_text = re.findall(r"=\w\w=\w\w=\w\w",data) #ค้นหาส่วนที่เป็น unicode ที่ยังมีในเนื้อหา ยกตัวอย่างเช่น =E0=B8=8101a
    Find_text = [i.replace('=','%') for i in Find_text] #เปลี่ยนเครื่องหมาย = ให้เป็น %
    #ลูปสำหรับเปลี่ยนเนื้อหาที่มี unicode ฝังอยู่
    for i in Find_text:
        data = re.sub(r"=\w\w=\w\w=\w\w",i,data,1)
    return unquote(data)

#ฟังก์ชั่นแปลง base64 ให้เป็นเนื้อหาที่อ่านได้
def encoded_words_to_text(encoded_words):
    encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}=' #กำหนดรูปแบบที่ต้องการค้นหา
    try:
        charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups() #ค้นหาตามรูปแบบที่กำหนดโดยใช้ฟังก์ชั่น match
        if encoding is 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding is 'Q':
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset) #ถอดรหัสเป็น utf-8
    except:
        return encoded_words #ถ้าเกิดปัญหาอันเนื่องมาจากรูปแบบไม่ match กันจะคือค่าเดิมออกไป

def encoded_words_to_file(encoded_words):
    try:
        return base64.b64decode(encoded_words.encode('utf-8'))
    except:
        print('error')
        return encoded_words

class msgparser:
    def __init__(self, msg_data):
        self.Attachment = ['',None]
        self.getPayloads(msg_data)
        self.getFromHeader(msg_data)
        self.getSubjectHeader(msg_data)
        self.getDateHeader(msg_data)
    
    #ฟังก์ชั่นสำหรับดึง content ของเมล
    def getPayloads(self, msg_data):
        try:
            for payload in email.message_from_bytes(msg_data[1][0][1]).get_payload()[1:]:
                self.Text = ''
                content = str(email.message_from_bytes(msg_data[1][0][1])) #แปลงเป็น string
                #print(content)
                attachment_filename = re.findall(r'Content-Disposition: attachment; filename="(.*?)"',content)
                #print(attachment_filename)
                if attachment_filename:
                    text_start = re.findall(r'X-Attachment-Id: .*?\n\n',content)
                    start = content.find(text_start[0])#;print(start)
                    stop  = start + content[start:].find('--')#;print(stop)
                    attachment_data = content[start+len(text_start[0]):stop-1].replace('\n','')
                    attachment_data = attachment_data.replace('\r','')
                    self.Attachment = [encoded_words_to_text(attachment_filename[0]),encoded_words_to_file(attachment_data)]

                text_start = re.findall(r'Content-Type: text/plain; charset="UTF-8"\nContent-Transfer-Encoding: base64\n\n',content)
                #print(text_start)
                if text_start:
                    start = content.find(text_start[0])#;print(start)
                    stop  = start + content[start:].find('--')#;print(stop)
                    content_text = content[start+len(text_start[0]):stop-1].replace('\n','')
                    self.Text = encoded_words_to_text('=?UTF-8?B?%s?='%content_text)
                    #self.Text = ''
                    #print(content_text)
                else:
                    text_start = 'Content-Type: text/plain; charset="UTF-8"\n\n'
                    start = content.find(text_start)#;print(start)
                    stop  = start + content[start:].find('--')#;print(stop)
                    self.Text =  content[start+len(text_start):stop-1].replace('\n','')
        except:
            pass
    
    #ดึง address เมลผู้ส่ง
    def getFromHeader(self, msg_data):
        self.From = string_filer(email.message_from_bytes(msg_data[1][0][1])['From'])
    
    #ดึงหัวข้อเมล
    def getSubjectHeader(self, msg_data):
        self.Subject = string_filer(email.message_from_bytes(msg_data[1][0][1])['Subject'])
        #print(email.message_from_bytes(msg_data[1][0][1])['Subject'])

    #ดึงเวลาที่ส่งมา
    def getDateHeader(self, msg_data):
        self.Date = string_filer(email.message_from_bytes(msg_data[1][0][1])['Date'])

class Mail:
    def __init__(self,email,pwd):
        self.email = email
        self.receive = imaplib.IMAP4_SSL('imap.gmail.com',993)#สร้างตัวเชื่อมต่อ server mail ของ google เพื่ออ่านข้อมูล 993 คือ port 
        self.receive.login(email,pwd) #สั่ง login mail
        self.send = smtplib.SMTP('smtp.gmail.com:587')
        self.send.ehlo()
        self.send.starttls()
        self.send.login(email,pwd)
        
    def Receive(self,subject):
        self.receive.select("inbox") #เลือกเช็คเมลใน inbox
        #=======================================================
        term = u"%s"%subject #เปลี่ยนตัวแปรเป็นแบบ unicode เพื่อให้ใช้ภาษาไทยได้
        self.receive.literal = term.encode('utf-8') #แปลงเป็น byte
        #print(self.receive.literal)
        type, data = self.receive.search("utf-8", "UNSEEN SUBJECT") #สั่งค้นหาเมลที่มี subject ตามที่ต้องการซึ่งจะได้ค่าออกมาเป็นหมายเลขเมล
        #=======================================================
        mail = [] #สร้างัวแปรชนิด list เพื่อเก็บเมลที่อ่านเจอ
        #วนลูปตามเลขเมลที่เจอ
        for idn in data[0].split():
            #print(idn)
            msg_data = self.receive.fetch(idn, '(RFC822)')#ดึงข้อมูลของเมลแต่ละฉบับ RFC 822 header ซึ่งเป็นหมายซองจดหมาย โดยจะบอกรายละเอียดผู้รับ
            #print(msg_data)
            try:
                mail.append(msgparser(msg_data)) #เรียกฟังก์ชั่น msgparser เพื่อแปลงข้อมูลที่ดึงมาจากเมลให้อยู่ในรูปแบบที่ใช้งานง่ายขึ้น
            except ValueError:
                pass
        return mail

    def Send(self,Subject='',To='',Text='',Attachment = ''):
        Subject = '=?utf-8?b?%s?='%text_to_encoded_words(Subject)
        From    = self.email
        Text    = text_to_encoded_words(Text)
        if Attachment == '':
            from1 = self.MailForm(0)
            msg = from1.format(_from=From,_subject=Subject,_to=To,_text=Text)
        else:
            FileText = file_to_encoded_words(Attachment)
            FileName  = Attachment.split('/')[-1]
            FileName  = '=?UTF-8?B?%s?='%text_to_encoded_words(FileName)
            from1 = self.MailForm(1)
            msg = from1.format(_from=From,_subject=Subject,_to=To,_text=Text,_filename=FileName,_filetext=FileText)
        try:
            #print(msg)
            self.send.sendmail(From,To,msg)
            #self.send.quit()
            return True
        except:
            return False

    def MailForm(self,select):
        if select == 0:
            from1 = 'By lucifer : 1.0\n'
            from1 += 'From: {_from}\n'
            from1 += 'Subject: {_subject}\n'
            from1 += 'To: {_to}\n'
            from1 += 'Content-Type: text/plain; charset="utf-8"\n'
            from1 += 'Content-Transfer-Encoding: base64\n\n'
            from1 += '{_text}\n\n'
            return from1
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


mail = Mail('your_mail@gmail.com','your_password')
while True:
    data = mail.Receive('test01')
    for d in data:
        From = re.findall(r'<(.*?)>',d.From)[0]
        print('From    : %s '%From)
        print('Subject : %s '%d.Subject)
        print('Date    : %s '%d.Date)
        print('content : %s '%d.Text)
        print('attachment : %s'%d.Attachment[0])
        mail.Send(Subject='ทดสอบการส่งเมล',To=From,Text=d.Text,Attachment = './ทดสอบ.txt')
    time.sleep(10)
    