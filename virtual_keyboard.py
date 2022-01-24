import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import numpy as np
import cvzone
from pynput.keyboard import Key, Controller

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=1)

finalText = ""

keyboard = Controller()


def drawAll(img, buttonList):
    imgNew = np.zeros_like(img, np.uint8)
    for button in buttonList:
        x, y = button.pos
        cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0, colorC=(255, 255, 255))
        cv2.rectangle(imgNew, button.pos, (x + button.size[0], y + button.size[1]),
                      (234, 178, 34), cv2.FILLED)
        cv2.putText(imgNew, button.text, (x + 40, y + 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    print(mask.shape)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
    return out


class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


timePrev = 0
keyUp = 0
keys = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "(", "<"],
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", ")", "#"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "=", "_"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "^", ">"]]
while True:
    buttonList = []
    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

    success, img = cap.read()
    img = cv2.resize(img, (1920, 1080))
    img = img[100:1000, 250:1670]
    img = detector.findHands(img)
    lmList, bboxInfo = detector.findPosition(img)
    img = drawAll(img, buttonList)

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (234, 178, 34), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(l)

                timer = time.time() - timePrev
                if l < 50 and timer > 1:
                    timePrev = time.time()
                    if button.text != "^" and button.text != "<" and button.text != "#" and button.text != "_" and button.text != ">" and button.text != ".":
                        keyboard.press(button.text)
                    if button.text == "<":
                        keyboard.press(Key.backspace)
                    if button.text == "#":
                        keyboard.press(Key.enter)
                    if button.text == "_":
                        keyboard.press(Key.space)
                    if button.text == ">":
                        keyboard.press(Key.tab)
                    if button.text == ".":
                        keyboard.press('.')
                        keyboard.release('.')
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text
                    if button.text == "^":
                        if keyUp == 1:
                            keys = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "(", "<"],
                                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", ")", "#"],
                                    ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "=", "_"],
                                    ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "^", ">"]]
                            keyUp = 0
                        else:
                            keys = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "(", "<"],
                                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", ")", "#"],
                                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "=", "_"],
                                    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "^", ">"]]
                            keyUp = 1

    #cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    #cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Virtual Keyboard", img)
    cv2.waitKey(1)