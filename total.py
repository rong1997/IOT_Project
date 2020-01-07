#import necessary packages
import pdfkit
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from gpiozero import Button
from gpiozero import MotionSensor
from picamera import PiCamera
from time import sleep
from signal import pause
import RPi.GPIO as GPIO
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import qrcode 
GPIO.setmode(GPIO.BCM)

#create objects that refer to a button,
#a motion sensor and the PiCamera
button = Button(17)
pir = MotionSensor(4)
#camera = PiCamera()

#start the camera
#camera.rotation = 180
#camera.start_preview()
#camera.start_preview()

#set the servo
CONTROL_PIN = 21  #yellow
FREQ = 50
GPIO.setup(CONTROL_PIN,GPIO.OUT)
p = GPIO.PWM(CONTROL_PIN,50) #frequency = 50
p.start(0)

#image names
i = 0

#count of people
count = 0

#qrcode
def qrCode(name,receiver):
    qrc = qrcode.QRCode(
        version = 1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size = 10,
        border = 4)
    html_str = """
    <center>
    <head>
        <p font size = "5">Visitor Name: {name}</p>
        <p font size = "5">Email: {receiver}</p>
    </head>
    <img src='/home/pi/Desktop/image.jpg' width = '50%'>
    </center>
    """.format(name=name,receiver=receiver)
    
    Html_file = open("/home/pi/Documents/html.html","w")
    Html_file.write(html_str)
    Html_file.close()
    
    url = name
    #confg = pdfkit.configuration(wkhtmltopdf = "/home/pi/Downloads/wkhtmltox_0.12.5-1.raspbian.stretch_armhf.deb")
    #pdfkit.from_url("/home/pi/Documents/html.html","/home/pi/Documents/information.pdf",configuration = confg)
    pdfkit.from_url("/home/pi/Documents/html.html","/home/pi/Documents/information.pdf")
    qrc.add_data(url)
    #picture_file.close()
    qrc.make(fit=True)
    img = qrc.make_image()
    img.save("/home/pi/Desktop/qrr.jpg")

#send Email method
def sendMail(r):
    #To use Gmail to send
    smtpHost = 'smtp.gmail.com'
    
    sender = 'janice02101998@gmail.com'
    password = "19980210candy"
    receiver = r
    
    msg = MIMEMultipart('related')
    msg['Subject'] = 'Visitor Card'
    msg['From'] = sender
    msg['To'] = receiver
    
    #to load the qrcode picture
    fp = open("/home/pi/Desktop/qrr.jpg","rb")
    msgImage = MIMEImage(fp.read())
    fp.close()
    
    msg.attach(msgImage)
    
    directory = "/home/pi/Documents/information.pdf"
    with open(directory,"rb") as opened:
        openedfile = opened.read()
    attachedfile = MIMEApplication(openedfile,_subtype = "pdf")
    
    msg.attach(attachedfile)
    
    #smtp port 587
    smtpServer = smtplib.SMTP(smtpHost,587)
    #important! send SMTP "ehlo" command to Gmail
    smtpServer.ehlo()
    smtpServer.starttls()

    smtpServer.login(sender,password)
    smtpServer.sendmail(sender,receiver,msg.as_string())
    print("send success")
    smtpServer.quit()



#servo method
def servoOn():
    p.ChangeDutyCycle(7.5)  # 90 degree
    sleep(3)
    p.ChangeDutyCycle(2.5)  # 0 degree
    sleep(1)

def detect():
    #set smile detect parameter
    face_cascade = cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_frontalface_default.xml")
    smile_cascade = cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_smile.xml")
    
    global count
    count += 1
    #detect the count 
    if count <= 3:
        cam = cv2.VideoCapture(0)
        taken = 0

        while True:
            prv,img = cam.read()
    
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            detect_face = face_cascade.detectMultiScale(gray)

            cv2.imshow("detect",img)            
            decodedObjects = pyzbar.decode(img)
            for obj in decodedObjects:
                print(obj.data)
                taken = 2
            
            for(fx,fy,fw,fh) in detect_face:
        
                #cv2.rectangle(img,(fx,fy),(fx+fw,fy+fh),(0,0,255),2)
                sleep(0.5)
                face_gray = gray[fy:fy+fh,fx:fx+fw]
                face_color = img[fy:fy+fh,fx:fx+fw]
        
                detect_smile = smile_cascade.detectMultiScale(face_gray)
                sleep(0.5)        
                for(sx,sy,sw,sh) in detect_smile:
                    #cv2.rectangle(face_color,(sx,sy),(sx+sw,sy+sh),(0,255,0),2)
                    img_name = "/home/pi/Desktop/image.jpg"
                    cv2.imwrite(img_name,img)
                    print("take photo",count)
                    taken = 1

            wk = cv2.waitKey(30) & 0xff
            if wk ==27:
                break
            if taken ==1 or taken ==2:
                break
        cam.release()
        cv2.destroyAllWindows()
        servoOn()
        if taken == 1:
            user = input("Please enter your name:")
            receiver = input("Your mail: ")
            qrCode(user,receiver)
            sendMail(receiver)
    else:
        print("Too many people")
          
def goOut():
    global count
    count = count-1
    servoOn()

        
#stop the camera when the pushbutton is pressed
def stop_camera():
    camera.stop_preview()
    print("camera stop")
    #exit the program
    p.stop()
    GPIO.cleanup()
    exit()

#assign a function that runs when motion is detected
pir.when_motion = detect

#pir.when_no_motion ?

    
button.when_pressed = goOut

pause()