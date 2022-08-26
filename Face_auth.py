import cv2
import numpy as np
import face_recognition
import os
import json
import time
from datetime import datetime
# from PIL import ImageGrab
 
# path = 'users'
# images = []
# classNames = []
# myList = os.listdir(path)
# for cl in myList:
#     curImg = cv2.imread(f'{path}/{cl}')
#     images.append(curImg)
#     classNames.append(os.path.splitext(cl)[0])
# print(classNames)
 
# def findEncodings(images):
#     encodeList = []
#     for img in images:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         encode = face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
#     return encodeList
 
# def markAttendance(name):
#     with open('Attendance.csv','r+') as f:
#         myDataList = f.readlines()
#         nameList = []
#         for line in myDataList:
#             entry = line.split(',')
#             nameList.append(entry[0])
#         if name not in nameList:
#             now = datetime.now()
#             dtString = now.strftime('%H:%M:%S')
#             f.writelines(f'\n{name},{dtString}')
 
# #### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# # def captureScreen(bbox=(300,300,690+300,530+300)):
# #     capScr = np.array(ImageGrab.grab(bbox))
# #     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
# #     return capScr
 
# encodeListKnown = findEncodings(images)
# print('Encoding Complete')

def img_resize(path):
    pathnew = path
    img = cv2.imread(pathnew)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    #resizing the image with custom width and height
    return cv2.resize(img, (width, height))

user_face_lst =[]
def face_getencode(path,name):
    global user_face_lst
    img = img_resize(path)
    user_face_det={
    "name":name,
    "encoding":list(face_recognition.face_encodings(img)[0])
    }
    user_face_lst.append(user_face_det)

def capture_face(img):
    global user_face_lst
    # img = img_resize(path)
    user_face_det = {
            "encoding": list(face_recognition.face_encodings(img)[0])
        }
    # user_face_lst.append(user_face_det)
    captured = json.dumps(user_face_det, indent=4)
    with open("temp_face_encode.json", "w") as outfile:
        outfile.write(captured)



    '''with open("sample.json", "r+") as file:
    data=json.load(file)
    data.append(user_face_det)
    json_object = json.dumps(data)
    json.dump(json_object)'''


# face_getencode("users/Madhoora.jpg","Madhoora")
# face_getencode("users/Elon.jpg","Elon")
# face_getencode("users/vinu.jpg","vinu")
#
# json_object = json.dumps(user_face_lst)
# with open("db.json", "a") as outfile:
#     outfile.write(","+json_object)

def login():

    return 
name =''

def face_auth():
    global name
    name = ""

    with open('db.json') as f:
        data = json.loads(f.read())
    encodeListKnown = []
    userListKnown = []
    for i in range(len(data)):
        userListKnown.append(data[i]["name"])
        encodeListKnown.append(data[i]["encoding"])

    cap = cv2.VideoCapture(0)
    
    #for i in encodeListKnown:
    while True:
        f = open('logincapture.json', "r")
        # Reading from file
        logindata = json.loads(f.read())
        # print(logindata)
        if logindata['findface'] == 'True':
            proceed = True
        else:
            proceed = False
        success, img = cap.read()
        #img = captureScreen()
        imgS = cv2.resize(img,(0,0),None,0.25,0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        cv2.rectangle(img, (0,-20), (img.shape[0]+int(0.4*img.shape[0]),img.shape[1]-int(0.94*img.shape[1]) ), (0, 255, 0), -1)

        if proceed:

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

            for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
                #print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = userListKnown[matchIndex]
                    #.upper()
                    #print(name)
                    y1,x2,y2,x1 = faceLoc
                    y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    print(name)
                    logindata['findface'] = 'False'
                    json_object = json.dumps(logindata, indent=4)
                    with open("logincapture.json", "w") as outfile:
                        outfile.write(json_object)
                    f = open('captured_face.json', "r")
                    userID = json.loads(f.read())
                    userID['userID'] = name
                    captured = json.dumps(userID, indent=4)
                    with open("captured_face.json", "w") as outfile:
                        outfile.write(captured)
                    username = {'username': name}
                    active_user = json.dumps(username, indent=4)
                    with open("username.json", "w") as outfile:
                        outfile.write(active_user)
                    with open('db.json') as f:
                        reg_database = json.loads(f.read())
                    active_user_details = {}
                    for user in reg_database:
                        if user['name'] == name:
                            active_user_details = user.copy()
                    if len(active_user_details) > 0:
                        af = open('activeUser.json', "r")
                        active_user_Data = json.loads(af.read())
                        active_user_Data[name] = active_user_details
                        json_object = json.dumps(active_user_Data, indent=4)
                        with open("activeUser.json", "w") as outfile:
                            outfile.write(json_object)
                    else:
                        pass



                    # login(name)
        # if success == True:
        #     cv2.imshow('Webcam', img)
        #     cv2.waitKey(1)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     # if the 'q' is pressed quit.'OxFF' is for 64 bit.[if waitKey==True] is condition
        #     break
        cv2.rectangle(img, (0, -20), (img.shape[0] + int(0.4 * img.shape[0]), img.shape[1] - int(0.94 * img.shape[1])),
                      (0, 0, 0), -1)
        cv2.putText(img, "Hi, "+name, (20, 30), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
        if success == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break
    cap.release()
    cv2.destroyAllWindows()


final_captured_img = []
def snapshot():
    global final_captured_img
    display_text = "take a snap of your face"
    cap = cv2.VideoCapture(0)

    while True:
        f = open('snap_state.json', "r")
        # Reading from file
        snapdata = json.loads(f.read())
        # print(logindata)
        if snapdata['captured'] == 'True':
            proceed = True
        else:
            proceed = False
        success, img = cap.read()
        # img = captureScreen()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)


        if proceed:
            try:
                capture_face(imgS)
                    # final_captured_img = img
                    # img = final_captured_img

                new_json = {'captured' : 'False'}
                captured = json.dumps(new_json, indent=4)
                with open("snap_state.json", "w") as outfile:
                    outfile.write(captured)
                display_text = "Your face has been captured"


            except:
                new_json = {'captured': 'True'}
                captured = json.dumps(new_json, indent=4)
                with open("snap_state.json", "w") as outfile:
                    outfile.write(captured)
                display_text = "Capturing..."

                    # login(name)
        # if success == True:
        #     cv2.imshow('Webcam', img)
        #     cv2.waitKey(1)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     # if the 'q' is pressed quit.'OxFF' is for 64 bit.[if waitKey==True] is condition
        #     break
        cv2.rectangle(img, (0, -20), (img.shape[0] + int(0.4 * img.shape[0]), img.shape[1] - int(0.94 * img.shape[1])),
                          (0, 0, 0), -1)
        cv2.putText(img, display_text, (20, 30), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
        if success == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break
    cap.release()
    cv2.destroyAllWindows()



def face_match(img,username):
            with open("db.json") as f:
                db = json.loads(f.read())
            for i in range(len(db)):
                if db[i]["name"] == username:
                    enc = db[i]["encoding"]
                    break
            try:
                enc1 = np.array(face_recognition.face_encodings(img))
                matches = face_recognition.compare_faces(enc, enc1)
                if matches[0]:
                    # print("match")
                    return (True,"match")
                else:
                    return (False,"no match")
            except:
                return (True,"no face")




# face_auth()
