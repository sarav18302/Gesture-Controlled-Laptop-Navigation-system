import cv2
import mediapipe as mp
import time
import os
from csv import writer
import json
import numpy as np
import pickle
import pyautogui
from math import hypot
from playsound import playsound
import pyttsx3
import gtts

# import ctypes
# ctypes.windll.user32.LockWorkStation()

width,height = pyautogui.size()
W,H = pyautogui.size()

def default_detection():

    cap = cv2.VideoCapture(0)

    model_file_name = 'new_gesture_model.sav'
    model = pickle.load(open(model_file_name, 'rb'))

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    sTime = time.time()

    class_names = {0: "gest1", 1: "gest2", 2: "gest3", 3: "gest4", 4: "gest5", 5: "gest6", 6: "gest7"}

    pivot_x = 0

    pivot_y = 0

    row_list = []
    power_seq = ""
    match_power_seq1 = "111211"
    match_power_seq1_alt = "121112"

    # line
    prev_len = 0
    cur_len = 0
    old_x = 100
    old_y = 500

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

    mous = False

    zoom_in =0
    zoom_out = 0

    f1_x, f1_y = 0, 0
    f2_x, f2_y = 0, 0

    screen_width, screen_height = pyautogui.size()
    index_y = 0
    index_x = 0
    thumb_x = 0
    thumb_y = 0
    ring_x = 0
    ring_y = 0
    mouse = True
    mousedown = False

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (185, 50)
    color = (0, 0, 255)
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
        ret, img = cap.read()
        img = cv2.resize(img, (960, 540))
        frame_height, frame_width, _ = img.shape
        x, y, c = img.shape
        t_elapsed = abs(sTime - time.time())

        # if t_elapsed>120:
        #     break
        cTime = time.time()
        #print(img.shape)
        x, y = frame_width, frame_height
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
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
                            x_ = int(lms.x * x)
                            y_ = int(lms.y * y)
                            thumb_x = screen_width - (screen_width / frame_width * x_)
                            thumb_y = screen_height / frame_height * y_
                            # print('outside', abs(index_y - thumb_y))
                        if id==12:
                            f3_x = lms.x
                            f3_y = lms.y
                            if mouse:
                                cv2.circle(img, (int(lms.x * w), int(lms.y * h)), 10, (225, 225, 0), cv2.FILLED)
                                x_ = int(lms.x * frame_width)
                                y_ = int(lms.y * frame_height)
                                ring_x = screen_width - (screen_width / frame_width * x_)
                                ring_y = screen_height / frame_height * y_

                        if id==8:
                            f2_x = lms.x
                            f2_y = lms.y
                            f2_x_ = lms.x*x
                            f2_y_ = lms.y*y
                            # cv2.circle(img, (int(lms.x * w), int(lms.y * h)), 10, (225, 225, 0), cv2.FILLED)
                            cv2.circle(img, (int(lms.x * x), int(lms.y * y)), 10, (225, 225, 0), cv2.FILLED)
                    break
                # Predict gesture
                prediction = model.predict([row_list])
                # print(prediction)
                classID = np.argmax(prediction)
                row_list=[]
                # cv2.putText(img, str(prediction[0]), org, font, fontScale=1, thickness=2, color=color)
                # print(prediction[0])
                # SLiding bar
                if prediction[0]==10 and proceed:
                    cv2.circle(img, (int(f1_x * w), int(f1_y * h)), 10, (225, 225, 0), cv2.FILLED)
                    cv2.circle(img, (int(f2_x * w), int(f2_y * h)), 10, (225, 225, 0), cv2.FILLED)
                    cv2.line(img,(int(f1_x * w), int(f1_y * h)),(int(f2_x * w), int(f2_y * h)),(225, 225, 0),10)
                    length = hypot(f2_x-f1_x,f2_y-f1_y)
                    #print(length)
                    if length>0.16:
                        zoom_in+=1
                        zoom_out=0
                        if zoom_in>10:
                            pyautogui.hotkey('ctrl', '+')
                            zoom_in = 0
                    elif length<0.06:
                        zoom_out+=1
                        zoom_in=0
                        if zoom_out>10:
                            pyautogui.hotkey('ctrl', '-')
                            zoom_out = 0
                if prediction[0]==0 and proceed:
                    ges_1 += 1
                    if ges_1 > 12:
                        cv2.putText(img, 'Gesture 1', org, font, fontScale=1, thickness=2, color=color)
                        ges_1 = 0
                        zoom_in = 0
                        zoom_out = 0
                        pyautogui.hotkey('ctrl','c')
                        power_seq = ""
                        # playsound('mixkit-long-pop-2358.wav')
                        t1 = gtts.gTTS("Copied")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                elif prediction[0]==1 and proceed:
                    ges_2 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_2 > 12:
                        cv2.putText(img, 'Gesture 2', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('ctrl', 'v')
                        t1 = gtts.gTTS("Pasted")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_2 = 0
                elif prediction[0]==2 and proceed:
                    ges_3 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_3 > 12:
                        cv2.putText(img, 'Gesture 3', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('ctrl', 'x')
                        t1 = gtts.gTTS("Cut")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_3 = 0
                elif prediction[0]==3 and proceed:
                    ges_4 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_4 > 12:
                        cv2.putText(img, 'Gesture 4', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('winleft', 'shift','s')
                        t1 = gtts.gTTS("Screenshot")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_4 = 0
                elif prediction[0]==4 and proceed:
                    ges_5 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_5 > 12:
                        cv2.putText(img, 'Gesture 5', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('ctrl', 'o')
                        t1 = gtts.gTTS("Opened")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_5 = 0
                elif prediction[0]==5 and proceed:
                    ges_6 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_6 > 12:
                        cv2.putText(img, 'Gesture 6', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('ctrl', 'z')
                        t1 = gtts.gTTS("Undo")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_6 = 0
                elif prediction[0]==6 and proceed:
                    ges_7 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_7 > 12:
                        cv2.putText(img, 'Gesture 7', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.press('esc')
                        t1 = gtts.gTTS("Escaped")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_7 = 0
                elif prediction[0]==7 and proceed:
                    ges_8 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_8 > 12:
                        cv2.putText(img, 'Gesture 8', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('ctrl', 'f5')
                        pyautogui.hotkey('ctrl', 's')
                        t1 = gtts.gTTS("Saved")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_8 = 0
                elif prediction[0]==8 and proceed:
                    ges_9 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_9 > 12:
                        cv2.putText(img, 'Gesture 9', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('enter')
                        t1 = gtts.gTTS("Enter")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_9 = 0
                elif prediction[0]==9 and proceed:
                    ges_10 += 1
                    zoom_in = 0
                    zoom_out = 0
                    if ges_10 > 12:
                        cv2.putText(img, 'Gesture 10', org, font, fontScale=1, thickness=2, color=color)
                        pyautogui.hotkey('alt', 'f4')
                        t1 = gtts.gTTS("Closed")
                        os.remove("tmp.mp3")
                        t1.save("tmp.mp3")
                        playsound("tmp.mp3")
                        power_seq = ""
                        ges_10 = 0
                elif prediction[0]==12:
                    ges_12 += 1
                    zoom_in = 0
                    zoom_out = 0
                    text = "Turned off"
                    if ges_12 > 12:
                        cv2.putText(img, 'Gesture 12', org, font, fontScale=1, thickness=2, color=color)
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
                    if prediction[0] == 1:
                        if mousedown == True:
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

