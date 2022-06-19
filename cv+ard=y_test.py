import sys
import cv2
import time
import threading
import serial

com = serial.Serial('COM4', 9600)

direction = "None"
distanceX = 0
distanceY = 0

is_end = False


def msg_output(distance, angle, curr_time):
    print(f"{curr_time} | direction = {direction} | dst = {distance} | msg = {angle} ")


def ard_msg():
    global direction
    global distanceX
    global distanceY
    global is_end
    # distance = 0
    angle = 0
    while not is_end:
        time.sleep(0.2)
        curr_time = time.strftime("%X")

        # 1 grad == 10px
        if direction == "UP":
            angle = str(round(distanceY / 10))
            angle += str(1)
            msg_output(distanceY, angle, curr_time)
            com.write(bytes(angle, 'utf-8'))
            print(str(curr_time) + " | Ard answer : " + str(com.readline()))
            # time.sleep(1)

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

        # print(com.readline())
#     com.write(bytes(angle, 'utf-8'))




face_cascade_db = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(2)
monX = 640
monY = 480
delta = 50

producer_thread = threading.Thread(target=ard_msg, daemon=True)
producer_thread.start()

while not is_end:
    success, img = cap.read()
    cv2.rectangle(img, (int(monX / 2) - 1, int(monY / 2) - 1), (int(monX / 2) + 1, int(monY / 2) + 1), (0, 0, 255), 2)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade_db.detectMultiScale(img_gray, 1.1, 20)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # cv2.line(img, (int(monX / 2), y + int(h/2)), (int(monX / 2), int(monY / 2)), (255, 0, 0), 2)


        distanceX = abs(x + int(w / 2) - int(monX / 2))
        distanceY = abs(y+ int(h / 2) - int(monY / 2))

        cv2.putText(img, "x=" + str(distanceX), (int(x + w + 10), int(y + h - 40)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        distanceY = abs(y + int(h / 2) - int(monY / 2))
        cv2.putText(img, "y=" + str(distanceY), (int(x + w + 10), int(y + h)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)



        # cv2.rectangle(img, (cenfaceX - delta, cenfaceY - delta), (cenfaceX + delta, cenfaceY + delta), (0, 0, 255), 2)
        # if cenfaceX - delta < int(monX/2) < cenfaceX + delta and cenfaceY - delta < int(monY/2) < cenfaceY + delta:
        #    print("dead_inside")

        # if not(y < int(monY/2) < y + h):
        #     print("no one dead inside")

        if x > int(monX/2):
            direction = "RIGHT"
        elif x + w < int(monX/2):
            direction = "LEFT"
        elif y > int(monY/2):
            direction = "DOWN"
        elif y + h < int(monY/2):
            direction = "UP"
        else:
            direction = "None1"

        cv2.putText(img, "Direction:" + direction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (30, 105, 210), 2)

    cv2.imshow('Face_Rec', img)
    # cv2.waitKey()
    if cv2.waitKey(1) & 0xff == 27:
        is_end = True
        print("Is end switched")

cap.release()
cv2.destroyAllWindows()

print("Exiting")
# time.sleep(0.1)
com.write(bytes("1003", 'utf-8'))
print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))
# time.sleep(0.1)
com.write(bytes("604", 'utf-8'))
print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))
# time.sleep(0.1)
com.write(bytes("1001", 'utf-8'))
print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))
# time.sleep(0.1)
com.write(bytes("602", 'utf-8'))
print(str(time.strftime("%X")) + " | Ard answer : " + str(com.readline()))
sys.exit()

