import cv2
import mediapipe as mp
import time
from csv import writer
import json
import os
import numpy as np
import pickle
import pyautogui
import gtts
import face_recognition
from Face_auth import face_match
from math import hypot
from playsound import playsound
import ctypes

def hold_W (hold_time,key):
    start = time.time()
    pyautogui.press(key,presses=10)
speech_dict = {
    "ctrl+c" : "copied",
    "ctrl+v" : "pasted",
    "ctrl+x" : "cut",
    "ctrl+p" : "printing",
    "ctrl+o" : "opened",
    "ctrl+s" : "saving",
    "ctrl+w" : "tab closed",
    "alt+f"  : "opened menu",
    "ctrl+f5": "reloaded page",
    "alt+e"  : "edit menu opened",
    "f1"     : "help",
    "f2"     : "brightness decreased",
    "f3"     : "brightness increased",
    "f4"     : "f4",
    "f5"     : "f5",
    "f6"     : "mute",
    "f7"     : "f7",
    "f8"     : "f8",
    "f9"     : "f9",
    "f10"    : "f10",
    "f11"    : "f11",
    "f12"    : "f12",
    "i"      : "i",
    "j": "j",
    "k":"k",
    "l":"l",
    "f":"f",
    "t":"t",
    "up": "up",
    "down":"down",
    "left":"left",
    "right":"right",
    "ctrl+d":"bookmark",
    "ctrl+n":"new",
    "ctrl+a":"selected all",
    "ctrl+d":"duplicated",
    "ctrl+b":"bold",
    "ctrl+i":"italic",
    "ctrl+u":"underline",
    "ctrl+f":"find",
    "ctrl+l":"left align",
    "ctrl+y":"Redo",
    "ctrl+z":"undo",
    "esc":"escaped",
    "enter":"enter",
    "space":"space",
    "end":"end",
    "alt+f4":"closed",
    "alt+tab":"switch tab",
    "winkey+tab":"show tabs",
    "winkey+d": "window",
    "winkey+l": "lockscreen",
    "winkey+down":"window down",
    "winkey+up": "window up",
    "winkey+left":"window left",
    "winkey+right":"window right",
    "winkey+printscreen":'screenshot',
    "winkey+ctrl+o": "virtual keyboard",
    "ctrl+alt+delete": "shutting down"
}

def camera_amount():
    '''Returns int value of available camera devices connected to the host device'''
    camera = 0
    while True:
        if (cv2.VideoCapture(camera).grab()) is True:
            camera = camera + 1
        else:
            cv2.destroyAllWindows()
            return(int(camera))

def shutdown():
    import subprocess
    subprocess.call(["shutdown","/s"])
def restart():
    import subprocess
    subprocess.call(["shutdown", "/r"])

def speakout(action):
    try:
        t1 = gtts.gTTS(speech_dict[action])
        os.remove("tmp.mp3")
        t1.save("tmp.mp3")
        playsound("tmp.mp3")
    except:
        pass

width,height = pyautogui.size()
def press(c,voice):
    cl = c.split('+')
    if len(cl)==1:
        if c == "restart":
            restart()
        elif cl[0]=='enter':
            pyautogui.hotkey('enter')
        elif cl[0]=='up' or cl[0]=='down':
            hold_W(0.2,cl[0])
        else:
            pyautogui.press(cl[0])
    elif len(cl)==2:
        if c=="None":
            pass
        # elif c == "ctrl+c" or c == "ctrl+x":
        #     pyautogui.hotkey(cl[0],cl[1])f
        elif c=='winkey+l':
            ctypes.windll.user32.LockWorkStation()
        elif 'winkey' in c:
            cl[0] = 'win'
            pyautogui.hotkey(cl[0], cl[1])
        else:
            pyautogui.hotkey(cl[0], cl[1])
    else:
        if c=="ctrl+alt+delete":
            shutdown()
        pyautogui.hotkey(cl[0], cl[1],cl[2])
    if voice:
        speakout(c)
userListKnown = []
encodeListKnown = []

def get_barchart_data(username):
    global ges_dict
    with open('bar_graph_data.json') as f:
        data = json.loads(f.read())
        try:
            labels = []
            freq = []
            for i in data:
                if i["username"]==username:
                    del i["username"]
                    # ges_dict = i
                    for x in i['labels']:
                        labels.append(x)
                    for y in i['freq']:
                        freq.append(y)
                    for i in range(len(labels)):
                        ges_dict[labels[i]] = freq[i]
                    return True
            return False
        except:
            return False
def update_barchart(username):
    pass

ges_dict = {}
def custom_detection_():
    W, H = pyautogui.size()
    global ges_act_dict
    global ges_dict
    with open('db.json') as f:
        data = json.loads(f.read())
    encodeListKnown = []
    userListKnown = []
    for i in range(len(data)):
        userListKnown.append(data[i]["name"])
        encodeListKnown.append(data[i]["encoding"])
    print(encodeListKnown)
    keyf = open('activeUser.json', "r")
    file = json.loads(keyf.read())
    f = open('username.json', "r")
    userID = json.loads(f.read())
    isexist = get_barchart_data(userID['username'])
    total_camera = camera_amount()
    cap = cv2.VideoCapture(0)
        # for cam in range(1,total_camera):
        #     try:
        #         cap = cv2.VideoCapture(cam)
        #         break
        #     except:
        #         print("yes")
    # try:
    #     s = cap.isOpened()
    # except:
    #     while True:
    #         img = cv2.imread('static/images/nancy.jpg')
    #         cv2.rectangle(img, (0, 0),
    #                       (img.shape[0], img.shape[1]),
    #                       (0, 0, 0), -1)
    #         cv2.putText(img, "Face not detected", (20, 32), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)

    model_file_name = 'new_gesture_model.sav'
    model = pickle.load(open(model_file_name, 'rb'))

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils


    class_names = {0: "ges1", 1: "ges2", 2: "ges3", 3: "ges4", 4: "ges5", 5: "ges6", 6: "ges7", 7: "ges8", 8: "ges9",9: "ges10",15:"ges11"}

    pivot_x = 0

    pivot_y = 0

    row_list = []

    ges_1 = 0
    ges_2 = 0
    ges_3 = 0
    ges_4 = 0
    ges_5 = 0
    ges_6 = 0
    ges_7 = 0
    ges_8 = 0
    ges_9 = 0
    ges_10 = 0
    ges_11 = 0
    ges_12 = 0
    ges15 = 0
    zoom_in =0
    zoom_out = 0

    f1_x, f1_y = 0, 0
    f2_x, f2_y = 0, 0

    proceed = True
    auth = True
    insecure = False
    display_text = ''
    mous = False
    mouse = True
    mousedown = False

    labels = []



    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (185, 50)
    color = (0, 0, 255)
    sTime = time.time()
    while (cap.isOpened()):

        f = open('switchdata.json', "r")
        # Reading from file
        data = json.loads(f.read())
        if data['state']=='active':
            if mous:
                proceed = False
            else:
                proceed = True
        else:
            proceed = False
        v = open('volume.json', "r")
        # Reading from file
        voice_state = json.loads(v.read())
        if voice_state['volume'] == 'unmuted':
            voice = True
        else:
            voice = False
        ret, img = cap.read()
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            for i in range(1,3):
                try:
                    cap1 = cv2.VideoCapture(i)
                    ret, img = cap.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    cap = cap1
                except:
                    pass
                print(i)
            img = cv2.imread('static/images/WEBCAMOCCUPIED.jpg')
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        img = cv2.resize(img, (960, 540))
        frame_height, frame_width, _ = img.shape

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        t_elapsed = abs(sTime - time.time())
        if not mous:
            if not auth:
                # isSecure = face_match(img, userID['username'])
                isSecure = (False,"match")
                if isSecure[1]=="match":
                    auth = True
                elif isSecure[1]=="not match":
                    auth = False
                    cv2.rectangle(img, (0, -20),
                                  (img.shape[0] + int(0.8 * img.shape[0]), img.shape[1] - int(0.95 * img.shape[1])),
                                  (0, 0, 0), -1)
                    cv2.putText(img, "Face not Matched", (20, 32), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
                else:
                    auth = False
                    cv2.rectangle(img, (0, -20),
                                  (img.shape[0] + int(0.8 * img.shape[0]), img.shape[1] - int(0.95 * img.shape[1])),
                                  (0, 0, 0), -1)
                    cv2.putText(img, "Face not detected", (20, 32), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
            if t_elapsed>15:
                # isSecure = checkface(img, userListKnown, encodeListKnown,userID['username'])
                # isSecure = face_match(img,userID['username'])
                isSecure = (False, "match")
                if isSecure[1]=="match":
                    auth = True
                elif isSecure[1]=="not match":
                    auth = False
                    cv2.rectangle(img, (0, -20),
                                  (img.shape[0] + int(0.8 * img.shape[0]), img.shape[1] - int(0.95 * img.shape[1])),
                                  (0, 0, 0), -1)
                    cv2.putText(img, "Face not Matched", (20, 32), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
                else:
                    auth = False
                    cv2.rectangle(img, (0, -20),
                                  (img.shape[0] + int(0.8 * img.shape[0]), img.shape[1] - int(0.95 * img.shape[1])),
                                  (0, 0, 0), -1)
                    cv2.putText(img, "Face not detected", (20, 32), cv2.FONT_HERSHEY_COMPLEX, 1.1, (255, 255, 255), 2)
                t_elapsed = 0
                sTime = time.time()
        else:
            auth = True


        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        x, y = frame_width, frame_height
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks!=0:
            if results.multi_hand_landmarks:
                for handlms in results.multi_hand_landmarks:
                    for id,lms in enumerate(handlms.landmark):
                        #print(id,lms)
                        h,w,c = img.shape
                        #print(img.shape)
                        cx,cy = int(lms.x*w),int(lms.y*h)
                        if id == 0:
                            pivot_x = int(lms.x * x)
                            pivot_y = int(lms.y * y)
                            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
                            # row_list.append(pivot_x)
                            # row_list.append(pivot_y)
                        else:
                            lmx = int(lms.x * x)
                            lmy = int(lms.y * y)
                            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
                            row_list.append(pivot_x - lmx)
                            row_list.append(pivot_y - lmy)
                        if id==4:
                            f1_x = lms.x
                            f1_y = lms.y
                        if id==8:
                            f2_x = lms.x
                            f2_y = lms.y
                            f2_x_ = lms.x * x
                            f2_y_ = lms.y * y

                    break
                # Predict gesture
                prediction = model.predict([row_list])
                # print(prediction)
                classID = np.argmax(prediction)
                row_list=[]
                # cv2.putText(img, str(prediction[0]), org, font, fontScale=1, thickness=2, color=color)
                # print(prediction[0])
                # SLiding bar
                if prediction[0]==10 and proceed and auth:
                    cv2.circle(img, (int(f1_x * w), int(f1_y * h)), 10, (225, 225, 0), cv2.FILLED)
                    cv2.circle(img, (int(f2_x * w), int(f2_y * h)), 10, (225, 225, 0), cv2.FILLED)
                    cv2.line(img,(int(f1_x * w), int(f1_y * h)),(int(f2_x * w), int(f2_y * h)),(225, 225, 0),10)
                    length = hypot(f2_x-f1_x,f2_y-f1_y)
                    #print(length)
                    if length>0.16:
                        zoom_in+=1
                        zoom_out=0
                        if zoom_in>5:
                            pyautogui.hotkey('ctrl', '+')
                            zoom_in = 0
                    elif length<0.06:
                        zoom_out+=1
                        zoom_in=0
                        if zoom_out>5:
                            pyautogui.hotkey('ctrl', '-')
                            zoom_out = 0
                if prediction[0]==0 and proceed and auth:
                    ges_1 += 1
                    if ges_1 > 12:
                        cv2.putText(img, 'Gesture 1', org, font, fontScale=1, thickness=2, color=color)
                        ges_1 = 0
                        zoom_in = 0
                        zoom_out = 0
                        # pyautogui.hotkey('ctrl','c')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]]=='None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]]=1
                        power_seq = ""
                elif prediction[0]==1 and proceed and auth:
                    ges_2 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_2 > 12:
                        cv2.putText(img, 'Gesture 2', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('ctrl', 'v')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_2 = 0
                        # print(ges_dict)
                elif prediction[0]==2 and proceed and auth:
                    ges_3 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_3 > 12:
                        cv2.putText(img, 'Gesture 3', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('ctrl', 'x')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_3 = 0
                elif prediction[0]==3 and proceed and auth:
                    ges_4 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_4 > 8:
                        cv2.putText(img, 'Gesture 4', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('winleft', 'shift','s')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_4 = 0
                elif prediction[0]==4 and proceed and auth:
                    ges_5 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_5 > 12:
                        cv2.putText(img, 'Gesture 5', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('ctrl', 'o')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_5 = 0
                elif prediction[0]==5 and proceed and auth:
                    ges_6 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_6 > 12:
                        cv2.putText(img, 'Gesture 6', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('ctrl', 'z')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_6 = 0
                elif prediction[0]==6 and proceed and auth:
                    ges_7 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_7 > 12:
                        cv2.putText(img, 'Gesture 7', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.press('esc')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_7 = 0
                elif prediction[0]==7 and proceed and auth:
                    ges_8 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_8 > 12:
                        cv2.putText(img, 'Gesture 8', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('ctrl', 's')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_8 = 0
                elif prediction[0]==8 and proceed and auth:
                    ges_9 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_9 > 12:
                        cv2.putText(img, 'Gesture 9', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('enter')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_9 = 0
                elif prediction[0]==9 and proceed and auth:
                    ges_10 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_10 > 12:
                        cv2.putText(img, 'Gesture 10', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('alt', 'f4')
                        press(file[userID['username']]["key"][class_names[prediction[0]]],voice)
                        if file[userID['username']]["key"][class_names[prediction[0]]] == 'None':
                            pass
                        else:
                            if file[userID['username']]["key"][class_names[prediction[0]]] in ges_dict.keys():
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] += 1
                            else:
                                ges_dict[file[userID['username']]["key"][class_names[prediction[0]]]] = 1
                        power_seq = ""
                        ges_10 = 0
                elif prediction[0]==15 and proceed and auth:
                    ges15 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges15 > 12:
                        cv2.putText(img, 'Gesture 15', org, font, fontScale=1, thickness=2, color=color)
                        # t1 = gtts.gTTS("new gesture")
                        # os.remove("tmp.mp3")
                        # t1.save("tmp.mp3")
                        # playsound("tmp.mp3")
                        press(file[userID['username']]["key"][class_names[prediction[0]]], voice)
                        power_seq = ""
                        ges15 = 0
                elif prediction[0]==12 and auth:
                    ges_12 += 1
                    zoom_in = 0
                    zoom_out = 0
                    text = "Turned off"
                    if ges_12 > 12:
                        cv2.putText(img, 'Gesture 10', org, font, fontScale=1, thickness=2, color=color)
                        # pyautogui.hotkey('alt', 'f4')
                        # press(file[userID['username']]["key"][class_names[prediction[0]]])
                        f = open('switchdata.json', "r")
                        data = json.loads(f.read())
                        if data["state"]== "deactive":
                            data['state']="active"
                            text = "Turned on"
                            mouse = True
                        else:
                            data['state'] = 'deactive'
                            text = "turned off"
                            mouse = False
                        json_object = json.dumps(data, indent=4)
                        with open("switchdata.json", "w") as outfile:
                            outfile.write(json_object)
                        t1 = gtts.gTTS(text)
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        # playsound('mixkit-long-pop-2358.wav')
                        power_seq = ""
                        ges_12 = 0
                elif prediction[0]==11:

                    ges_11 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_11 > 12:
                        cv2.putText(img, 'Gesture 11', org, font, fontScale=1, thickness=2, color=color)
                        if mous:
                            mous = False
                            proceed = True
                            t1 = gtts.gTTS("Mouse Control off")
                            os.remove("tmp.mp3")
                            t1.save("tmp.mp3")
                            playsound("tmp.mp3")
                        elif not mous:
                            mous = True
                            proceed = False
                            t1 = gtts.gTTS("mouse control on")
                            os.remove("tmp.mp3")
                            t1.save("tmp.mp3")
                            playsound("tmp.mp3")
                        print(mous,proceed)
                        power_seq = ""
                        ges_11 = 0
                if mous==True and proceed==False and mouse:
                    cv2.rectangle(img, (frame_width // 4, frame_height // 4),(int((3 / 4) * frame_width), int((3 / 4) * frame_height)), (0, 225, 0), 2)
                    if prediction[0]==1:
                        if mousedown==True:
                            pyautogui.mouseUp()
                            mousedown = False
                        else:
                            pyautogui.click()
                            time.sleep(1)
                    elif prediction[0] == 3:
                        pyautogui.click(clicks=2)
                        # pyautogui.dragTo(pyautogui.position()[0], pyautogui.position()[1], button='left')
                        time.sleep(1)
                    elif prediction[0] == 9:
                        pyautogui.click(button='right')
                        time.sleep(1)
                    elif prediction[0] == 2 and not mousedown:
                        pyautogui.mouseDown()
                        mousedown = True
                    # elif prediction[0] == 3:
                    #     start = pyautogui.position()
                    #     pyautogui.dragTo(pyautogui.position()[0],pyautogui.position()[1],button='left')
                    #     print("dragged")
                        # thumb_x = screen_width / frame_width * x_
                    # thumb_y = screen_height / frame_height * y
                        # pyautogui.moveTo(1000, 100)
                    if (f2_x_ < int((3 / 4) * frame_width) and f2_x_ > (frame_width // 4)) and (f2_y_ < int((3 / 4) * frame_height) and f2_y_ > (frame_height // 4)):
                        # print("yes")
                        print(f2_x_,f2_y_)
                        try:
                            pyautogui.moveTo(W - (((2 * W) // frame_width) * (f2_x_ - frame_width // 4)),((2 * H) // frame_height) * (f2_y_ - frame_height // 4) * 1.3)
                        except:
                            pass

            labels = list(ges_dict.keys())
            freq = [ges_dict[x] for x in labels]
            # labels = [str(ges_act_dict[x]) for x in labels1]

            data = {
                "labels" : labels,
                "freq" : freq
            }
            # print(ges_dict)
            with open('bar_graph_data.json') as f:
                db_data = json.loads(f.read())
            if isexist:
                for x in range(len(db_data)):
                    if db_data[x]["username"]==userID['username']:
                        add_data = {
                            "username" : userID['username'],
                            "labels": labels,
                            "freq": freq
                        }
                        db_data[x] = add_data
                        # print(db_data[x])
                        break
                # print(db_data)
                json_object = json.dumps(db_data, indent=4)
                with open("bar_graph_data.json", "w") as outfile:
                    outfile.write(json_object)
                json_object = json.dumps(data, indent=4)
                with open("gestures.json", "w") as outfile:
                    outfile.write(json_object)

            else:
                # print("does not exist")
                with open('bar_graph_data.json') as f:
                    db_data = json.loads(f.read())
                    add_data = {
                                "username" : userID['username'],
                                "labels": labels,
                                "freq": freq
                            }
                    db_data.append(add_data)
                    json_object = json.dumps(db_data, indent=4)
                    with open("bar_graph_data.json", "w") as outfile:
                        outfile.write(json_object)
            # print(labels)
                json_object = json.dumps(data, indent=4)
                with open("gestures.json", "w") as outfile:
                    outfile.write(json_object)
        #cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_DUPLEX,3,(225,0,225),3)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # if the 'q' is pressed quit.'OxFF' is for 64 bit.[if waitKey==True] is condition
            break
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
