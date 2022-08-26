import cv2
import mediapipe as mp
import pandas as pd
import json
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
from csv import writer
import numpy as np
import shutil

def addmotiongesture():
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    sTime = time.time()

    pivot_x = 0
    pivot_y = 0

    row_list =[]
    shutil.copyfile('gestures_landmarks.csv', 'gestures_landmarks_new.csv')

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (50, 40)
    color = (255, 255, 255)
    train = False
    while (cap.isOpened()):
        ret, img = cap.read()
        img = cv2.resize(img, (960, 540))
        x, y, c = img.shape
        t_elapsed = abs(sTime - time.time())
        cv2.rectangle(img, (0, -20),
                      (img.shape[0] + int(1.3 * img.shape[0]), img.shape[1] - int(0.93 * img.shape[1])),
                      (0, 0, 0), -1)
        f = open('ges_captured.json', "r")
        data = json.loads(f.read())
        if data['captured']=="True":
            if t_elapsed<=10:
                cv2.putText(img, 'Get ready to show gesture for right hand', org, font, fontScale=1, thickness=2, color=color)
            elif t_elapsed>10 and t_elapsed<51:
                cv2.putText(img, 'Show the gesture in right hand', org, font, fontScale=1, thickness=2, color=color)
            elif t_elapsed>50 and t_elapsed<61:
                cv2.putText(img, 'Get ready to show gesture for left hand', org, font, fontScale=1, thickness=2, color=color)
            elif t_elapsed>60 and t_elapsed<101:
                cv2.putText(img, 'Show the gesture in left hand', org, font, fontScale=1, thickness=2, color=color)
            elif t_elapsed>101:
                cv2.putText(img, 'Gesture captured', org, font, fontScale=1, thickness=2, color=color)
                train = True
            cTime = time.time()
            #print(img.shape)

            imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            if results.multi_hand_landmarks!=0 and not train:
                if results.multi_hand_landmarks:
                    for handlms in results.multi_hand_landmarks:
                        for id,lms in enumerate(handlms.landmark):
                            #print(id,lms)
                            h,w,c = img.shape
                            #print(img.shape)
                            cx,cy = int(lms.x*w),int(lms.y*h)
                            #print("id:",id,", x:",cx,", y:",cy)
                            if id==0:
                                pivot_x = int(lms.x * x)
                                pivot_y = int(lms.y * y)
                                mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
                                if t_elapsed>10:
                                    row_list.append(str(pivot_x))
                                    row_list.append(str(pivot_y))
                            else:
                                lmx = int(lms.x * x)
                                lmy = int(lms.y * y)
                                mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
                                if t_elapsed>10:
                                    row_list.append(str(pivot_x-lmx))
                                    row_list.append(str(pivot_y-lmy))
                        row_list.append("15")
                        break
                if t_elapsed>10 and results.multi_hand_landmarks!=0:
                    with open("gestures_landmarks_new.csv", "a") as f:
                        if len(row_list)>0:
                            f.write(",".join(row_list)+"\n")
                row_list=[]
            if train:
                df = pd.read_csv('gestures_landmarks_new.csv')
                df.drop(['0_x', '0_y'], axis=1, inplace=True)
                x_train, x_test, y_train, y_test = train_test_split(df.drop('class_id', axis=1), df['class_id'],
                                                                    test_size=0.30, random_state=1)
                logmodel = LogisticRegression()
                logmodel.fit(x_train, y_train)
                prediction = logmodel.predict(x_test)
                accuracy = accuracy_score(y_test, prediction)
                print(accuracy)

                filename = 'new_gesture_model.sav'
                pickle.dump(logmodel, open(filename, 'wb'))
                statesInfo = {
                            "captured": "False"
                        }
                json_object = json.dumps(statesInfo, indent=4)
                with open("ges_captured.json", "w") as outfile:
                    outfile.write(json_object)
        #cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_DUPLEX,3,(225,0,225),3)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # if the 'q' is pressed quit.'OxFF' is for 64 bit.[if waitKey==True] is condition
            break
        # if ret == True:
        #     cv2.imshow("result",img)
        #     pass
        if ret == True:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
