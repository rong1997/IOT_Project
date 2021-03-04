# IOT_Project
## 陌生訪客登記系統
當訪客被入口處的感測器偵測到後，會自動開啟相機，訪客微笑三秒即自動拍照並傳到電腦，由訪客輸入自己的相關資訊，隨後大門開啟，做好的臨時訪客證與QRcode會傳到訪客輸入的信箱裡，之後訪客即可以使用QRcode掃描代替拍照入場。<br />

Video: https://youtu.be/ml0Z3P2g3Io <br />

所需材料:<br />
樹莓派 * 1 <br />
麵包板 * 1 <br />
鏡頭 * 1 <br />
人體紅外線感應 * 1 <br />
伺服馬達 * 1 <br />
輕觸開關 * 1 <br />
杜邦線 * 15 <br />

### 步驟一: 安裝opencv相關套件
參考網址: https://github.com/amymcgovern/pyparrot/issues/34 <br />
Install opencv <br />
`pip3 install opencv-python` <br />
Install all dependencies <br />
`sudo apt-get install libatlas-base-dev` <br />
`sudo apt-get install libjasper-dev` <br />
`sudo apt-get install libqtgui4` <br />
`sudo apt-get install python3-pyqt5` <br />
`sudo apt-get install libqt4-test` <br />

### 步驟二: 安裝pdfkit
參考網址: https://github.com/twtrubiks/python-pdfkit-example <br />
Install pdfkit <br />
`pip3 install pdfkit` <br />

### 步驟三: 下載偵測笑容所需xml檔
參考網址: https://github.com/opencv/opencv/tree/master/data/haarcascades <br />
`haarcascade_frontalface_default.xml` <br />
`haarcascade_smile.xml` <br />

### 步驟四: 撰寫模擬門打開(伺服馬達啟動)的程式
參考網址: https://rpi.science.uoit.ca/lab/servo/ <br />
Import所需套件 <br />
`import RPi.GPIO as GPIO` <br />
設定GPIO的模式 <br />
`GPIO.setmode(GPIO.BCM)` <br />
設定伺服馬達的PIN、頻率 <br />
`CONTROL_PIN = 21` <br />
`FREQ = 50` <br />
`GPIO.setup(CONTROL_PIN,GPIO.OUT)` <br />
`p = GPIO.PWM(CONTROL_PIN,50)` <br /> 
設定轉到90度的位置 <br />
`p.ChangeDutyCycle(7.5)` <br />
設定轉回0度的位置 <br />
`p.ChangeDutyCycle(2.5)` <br />

### 步驟五: 撰寫笑容偵測並拍照的程式
參考網址: https://www.youtube.com/watch?v=nPxmjo1VVtc <br />
Import所需套件 <br />
`import cv2` <br />
`from time import sleep` <br />
接著設定相關的xml檔案 <br />
`face_cascade = cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_frontalface_default.xml")` <br />
`smile_cascade = cv2.CascadeClassifier("/home/pi/Downloads/haarcascade_smile.xml")` <br />
將笑容檢測執行程式包在`detect()`裡面 <br />
`gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)` <br />
`detect_face = face_cascade.detectMultiScale(gray)` <br />
將鏡頭拍攝到的畫面投影在螢幕上 <br />
`cv2.imshow("detect",img)` <br />
偵測笑容前，要先偵測到臉部，相關程式包在for迴圈裡面 <br />
`for(fx,fy,fw,fh) in detect_face:` <br />
設定相關數值 <br />
`face_gray = gray[fy:fy+fh,fx:fx+fw]` <br />
`face_color = img[fy:fy+fh,fx:fx+fw]` <br />
`detect_smile = smile_cascade.detectMultiScale(face_gray)` <br />
偵測笑容 <br />
`for(sx,sy,sw,sh) in detect_smile:` <br />
偵測到笑容後使用`cv2.imwrite()`拍下照片 <br />
拍完照後呼叫`servoOn()`把伺服馬達啟動 <br />
`cam.release()` `cv2.destroyAllWindows()`將鏡頭關閉並退出鏡頭畫面視窗 <br />

### 步驟六: 撰寫製作臨時訪客證(html轉pdf)與QRcode的程式(安裝QRcode套件)
參考網址1: https://stackoverflow.com/questions/16523939/how-to-write-and-save-html-file-in-python <br />
參考網址2: https://note.nkmk.me/en/python-pillow-qrcode/ <br />
參考網址3: https://github.com/twtrubiks/python-pdfkit-example <br />
Install qrcode <br />
`pip3 install qrcode` <br />
Install pdfkit <br />
`pip3 install pdfkit` <br />
Import所需套件 <br />
`import qrcode` <br />
`import pdfkit` <br />
將製作的程式包在`qrCode()`裡面 <br />
qrcode大小等設定並指給qrc <br />
`qrc = qrcode.QRCode()` <br />
將資料傳進QRcode裡 <br />
`qrc.add_data(url)` <br />
將QRcode製成圖片並存檔 < br />
`img = qrc.make_image()` <br />
`img.save("/home/pi/Desktop/qrr.jpg")` <br />

將訪客的照片以及輸入的資料放進html <br />
`html_str = """` <br />
     `<center>` <br />
     `<head>` <br />
        `<p font size = "5">Visitor Name: {name}</p>` <br />
        `<p font size = "5">Email: {receiver}</p>` <br />
     `</head>` <br />
     `<img src='/home/pi/Desktop/image.jpg' width = '50%'>` <br />
     `</center>` <br />
     `""".format(name=name,receiver=receiver)` <br />
將寫好的html存檔 <br />
`Html_file = open("/home/pi/Documents/html.html","w")` <br />
`Html_file.write(html_str)` <br />
`Html_file.close()` <br />
將html轉成pdf檔案以方便後面寄信 <br />
`pdfkit.from_url("/home/pi/Documents/html.html","/home/pi/Documents/information.pdf")` <br />

### 步驟七: 撰寫寄信的程式
參考網址: https://blog.taiker.space/python-how-to-send-an-email-with-python/ <br />
Import所需套件 <br />
`from email.mime.text import MIMEText` <br />
`from email.mime.application import MIMEApplication` <br />
`from email.mime.multipart import MIMEMultipart` <br />
`from email.mime.image import MIMEImage` <br />
寄信程式包在`sendMail()`裡面 <br />
設定用gmail寄信 <br />
`smtpHost = 'smtp.gmail.com'` <br />
設定信件的標題、寄件者，收件者 <br />
`msg = MIMEMultipart('related')` <br />
`msg['Subject'] = 'Visitor Card'`<br />
`msg['From'] = sender` <br />
`msg['To'] = receiver` <br />
用attach把QRcode放進信件裡 <br />
`fp = open("/home/pi/Desktop/qrr.jpg","rb")` <br />
`msgImage = MIMEImage(fp.read())` <br />
`fp.close()` <br />
`msg.attach(msgImage)` <br />
臨時訪客證是pdf步驟會比較麻煩 <br />
`directory = "/home/pi/Documents/information.pdf"` <br />
先把pdf打開並讀取 <br />
`with open(directory,"rb") as opened:` <br />
`  openedfile = opened.read()` <br />
再將資料指給attachedfile，要特別標明後面的_subtype = "pdf" <br />
`attachedfile = MIMEApplication(openedfile,_subtype = "pdf")` <br />
`msg.attach(attachedfile)` <br />

設定port為587 <br />
`smtpServer = smtplib.SMTP(smtpHost,587)` <br />
Important! Send SMTP "ehlo" command to Gmail <br />
`smtpServer.ehlo()` <br />
`smtpServer.starttls()` <br />
用設定過的的帳號密碼登入 <br />
`smtpServer.login(sender,password)` <br />
將信寄出去 <br />
`smtpServer.sendmail(sender,receiver,msg.as_string())` <br />
`smtpServer.quit()` <br />

### 步驟八: 撰寫鏡頭讀取QRcode的程式
參考網址: https://pysource.com/2019/02/28/scanning-qr-code-opencv-with-python/ <br />
安裝pyzbar <br />
`sudo pip3 install pyzbar` <br />
Import所需套件 <br />
`import pyzbar.pyzbar as pyzbar` <br />
將鏡頭拍攝到的影像decode <br />
`prv,img = cam.read()` <br />
`decodedObjects = pyzbar.decode(img)` <br />
decode完執行`servoOn()` <br />

### 步驟九: 執行total.py
完成IOT專案: 陌生訪客登記系統
