import cv2
import cvui
import numpy as np
import threading
import time
import serial
import serial.tools.list_ports
import sys

# UI CONST
WINDOW_NAME = "Face_Rec"
VIDEO_WIDTH = 800
VIDEO_HEIGHT = 600
WINDOW_WIDTH = VIDEO_WIDTH + 400
WINDOW_HEIGHT = VIDEO_HEIGHT + 40
TEXT_WIDTH = WINDOW_WIDTH - 10 - int(VIDEO_WIDTH + 21)
TEXT_HEIGHT = int((WINDOW_WIDTH - 10 - int(VIDEO_WIDTH + 21))/6)

# Lists for UI
cam_track = [5.0]
counter_value = [2]
success = True

# Text images
curr_camera_text = cv2.imread('curr_camera.jpg')
curr_camera_text = cv2.resize(curr_camera_text, (TEXT_WIDTH, TEXT_HEIGHT))

preview_window_text = cv2.imread('prevew_window.jpg')
preview_window_text = cv2.resize(preview_window_text, (TEXT_WIDTH, TEXT_HEIGHT))


# Connect to serial
available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
com = serial.Serial(available_ports[0][0], 9600)

# Data for message to Arduino
direction = "None"
distanceX = 0
distanceY = 0

# State of program
is_end = False


def msg_output(distance, angle, curr_time):
    print(f"{curr_time} | direction = {direction} | dst = {distance} | msg = {angle} ")


def ard_msg():
    global direction
    global distanceX
    global distanceY
    global is_end
    angle = 0
    print("ard_msg thread started")
    while not is_end:
        time.sleep(0.5)
        curr_time = time.strftime("%X")

        # 1 grad == 10px
        if direction == "UP":
            angle = str(round(distanceY / 10))
            angle += str(1)
            msg_output(distanceY, angle, curr_time)
            com.write(bytes(angle, 'utf-8'))
            print(str(curr_time) + " | Ard answer : " + str(com.readline()))

        elif direction == "DOWN":
            angle = str(round(distanceY / 10))
            angle += str(2)
            msg_output(distanceY, angle, curr_time)
            com.write(bytes(angle, 'utf-8'))
            print(str(curr_time) + " | Ard answer : " + str(com.readline()))

        elif direction == "LEFT":
            angle = str(round(distanceX / 10))
            angle += str(3)
            msg_output(distanceX, angle, curr_time)
            com.write(bytes(angle, 'utf-8'))
            print(str(curr_time) + " | Ard answer : " + str(com.readline()))

        elif direction == "RIGHT":
            angle = str(round(distanceX / 10))
            angle += str(4)
            msg_output(distanceX, angle, curr_time)
            com.write(bytes(angle, 'utf-8'))
            print(str(curr_time) + " | Ard answer : " + str(com.readline()))


def breakout(cap):
    cap.release()
    cv2.destroyAllWindows()
    global direction

    print("Breakout start")

    direction = "None"
    time.sleep(1)


    com.write(bytes("1003", 'utf-8'))
    print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))

    com.write(bytes("654", 'utf-8'))
    print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))

    com.write(bytes("1001", 'utf-8'))
    print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))

    com.write(bytes("652", 'utf-8'))
    print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))
    sys.exit()


def main():
    global direction
    global distanceX
    global distanceY
    global is_end

    frame = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), np.uint8)
    cvui.init(WINDOW_NAME)
    face_cascade_db = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    is_preview_window_show = [True]
    is_end = False

    # Check num of video input's
    success = True
    cam_count = 0
    while success:
        success, img = cv2.VideoCapture(cam_count + 1).read()
        cam_count += 1
    cam_count -= 1

    counter_value_prev = counter_value[0] - 1

    producer_thread_ard = threading.Thread(target=ard_msg, daemon=True)
    producer_thread_ard.start()

    while(True):
        frame[:] = (49, 52, 49)
        if counter_value_prev != counter_value[0]:
            cap = cv2.VideoCapture(int(counter_value[0]))

        success, video_raw = cap.read()
        if success:
            video = video_raw

        video = cv2.resize(video, (VIDEO_WIDTH, VIDEO_HEIGHT))

        img_gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
        faces = face_cascade_db.detectMultiScale(img_gray, 1.1, 20)
        for (x, y, w, h) in faces:
            cv2.rectangle(video, (x, y), (x + w, y + h), (0, 255, 0), 2)

            distanceX = abs(x + int(w / 2) - int(VIDEO_WIDTH / 2))
            cv2.putText(video, "x=" + str(distanceX), (int(x + w + 10), int(y + h - 40)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

            distanceY = abs(y + int(h / 2) - int(VIDEO_HEIGHT / 2))
            cv2.putText(video, "y=" + str(distanceY), (int(x + w + 10), int(y + h)), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

            if x > int(VIDEO_WIDTH / 2):
                direction = "RIGHT"
            elif x + w < int(VIDEO_WIDTH / 2):
                direction = "LEFT"
            elif y > int(VIDEO_HEIGHT / 2):
                direction = "DOWN"
            elif y + h < int(VIDEO_HEIGHT / 2):
                direction = "UP"
            else:
                direction = "None"

            cv2.putText(video, "Direction:" + direction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (30, 105, 210), 2)

        # VIDEO FRAME
        cvui.window(frame, 10, 10, VIDEO_WIDTH + 1, VIDEO_HEIGHT, 'Video')
        if is_preview_window_show[0]:
            cv2.rectangle(video, (int(VIDEO_WIDTH / 2) - 1, int(VIDEO_HEIGHT / 2) - 1),
                      (int(VIDEO_WIDTH / 2) + 1, int(VIDEO_HEIGHT / 2) + 1), (0, 0, 255), 2)
            cvui.image(frame, 11, 30, video)

        # SETTINGS FRAME
        cvui.window(frame, VIDEO_WIDTH + 21, 10, WINDOW_WIDTH - 10 - int(VIDEO_WIDTH + 21), WINDOW_HEIGHT - 20, 'Settings')

        counter_value_prev = counter_value[0]
        cvui.image(frame, VIDEO_WIDTH + 21, 50, curr_camera_text)
        cvui.trackbar(frame, VIDEO_WIDTH + 21, 100, WINDOW_WIDTH - VIDEO_WIDTH - 30, counter_value, 1., float(cam_count), 1, '%.1Lf',
                      cvui.TRACKBAR_DISCRETE, 1)

        cvui.image(frame, VIDEO_WIDTH + 21, 150, preview_window_text)
        cvui.checkbox(frame, VIDEO_WIDTH + 21 + int(TEXT_WIDTH/2), 200, "", is_preview_window_show)

        if cvui.button(frame, VIDEO_WIDTH + int(TEXT_WIDTH/2), 300, 'EXIT'):
            is_end = True

        # Show UI on main window
        cvui.update()
        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(20) == 27 or is_end:
            breakout(cap)
            break


if __name__ == '__main__':
    producer_thread_main = threading.Thread(target=main, daemon=True)
    producer_thread_main.start()
    producer_thread_main.join()

