import cv2
import mediapipe as mp
import pyautogui


W,H = pyautogui.size()
print(W,H)
f_x,f_y = 0,0
def mouse_control():
    cap = cv2.VideoCapture(0)
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils
    font = cv2.FONT_HERSHEY_SIMPLEX
    while (cap.isOpened()):
        ret, img = cap.read()
        frame_height, frame_width, _ = img.shape
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        cv2.rectangle(img, (frame_width//4,frame_height//4), (int((3/4)*frame_width),int((3/4)*frame_height)), (0,225,0), 2)
        x, y = frame_width, frame_height
        if results.multi_hand_landmarks != 0:
            if results.multi_hand_landmarks:
                for handlms in results.multi_hand_landmarks:
                    for id, lms in enumerate(handlms.landmark):
                        mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)
                        if id==8:
                            f_x = lms.x*x
                            f_y = lms.y*y
                            cv2.circle(img, (int(lms.x * x), int(lms.y * y)), 10, (225, 225, 0), cv2.FILLED)
                if (f_x<int((3/4)*frame_width) and f_x>(frame_width//4)) and (f_y<int((3/4)*frame_height) and f_y>(frame_height//4)):
                    try:
                        # print(f_x,f_y)
                        pyautogui.moveTo(W - (((2*W)//frame_width)*(f_x-frame_width//4)),((2*H)//frame_height)*(f_y-frame_height//4)*1.3)
                    except:
                        pass
        cv2.imshow('output',img)
        # print(img.shape)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # if the 'q' is pressed quit.'OxFF' is for 64 bit.[if waitKey==True] is condition
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    mouse_control()
