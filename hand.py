import cv2                              # библиотека opencv (получение и обработка изображения)
import mediapipe as mp                  # библиотека mediapipe (распознавание рук)
import serial                           # библиотека pyserial (отправка и прием информации)


camera = cv2.VideoCapture(0)            # получаем изображение с камеры (0 - порядковый номер камеры в системе)
mpHands = mp.solutions.hands            # подключаем раздел распознавания рук
hands = mpHands.Hands()                 # создаем объект класса "руки"
mpDraw = mp.solutions.drawing_utils     # подключаем инструменты для рисования


portNo = "COM8"                         # указываем последовательный порт, к которому подключена Arduino
uart = serial.Serial(portNo, 9600)      # инициализируем последовательный порт на скорости 9600 Бод


p = [0 for i in range(21)]              # создаем массив из 21 ячейки для хранения высоты каждой точки
finger = [0 for i in range(5)]          # создаем массив из 5 ячеек для хранения положения каждого пальца

# функция, возвращающая расстояние по модулю (без знака)
def distance(point1, point2):
    return abs(point1 - point2)


while True:
    good, img = camera.read()                                   # получаем один кадр из видеопотока
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)               # преобразуем кадр в RGB


    results = hands.process(imgRGB)                             # получаем результат распознавания
    if results.multi_hand_landmarks:                            # если обнаружили точки руки
        for handLms in results.multi_hand_landmarks:            # получаем координаты каждой точки

            # при помощи инструмента рисования проводим линии между точками
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # работаем с каждой точкой по отдельности
            # создаем список от 0 до 21 с координатами точек
            for id, point in enumerate(handLms.landmark):
                # получаем размеры изображения с камеры и масштабируем
                width, height, color = img.shape
                width, height = int(point.x * height), int(point.y * width)

                p[id] = height           # заполняем массив высотой каждой точки
                if id == 8:              # выбираем нужную точку
                    # рисуем нужного цвета кружок вокруг выбранной точки
                    cv2.circle(img, (width, height), 15, (255, 0, 255), cv2.FILLED)
                if id == 12:
                    cv2.circle(img, (width, height), 15, (0, 0, 255), cv2.FILLED)

            # получаем расстояние, с которым будем сравнивать каждый палец
            distanceGood = distance(p[0], p[5]) + (distance(p[0], p[5]) / 2)
            # заполняем массив 1 (палец поднят) или 0 (палец сжат)
            finger[1] = 1 if distance(p[0], p[8]) > distanceGood else 0
            finger[2] = 1 if distance(p[0], p[12]) > distanceGood else 0
            finger[3] = 1 if distance(p[0], p[16]) > distanceGood else 0
            finger[4] = 1 if distance(p[0], p[20]) > distanceGood else 0
            finger[0] = 1 if distance(p[4], p[17]) > distanceGood else 0

            # готовим сообщение для отправки
            msg = ''
            # 0 - большой палец, 1 - указательный, 2 - средний, 3 - безымянный, 4 - мизинец
            # жест "коза" - 01001
            if not (finger[0]) and finger[1] and not (finger[2]) and not (finger[3]) and finger[4]:
                msg = '@'
            if finger[0] and not (finger[1]) and not (finger[2]) and not (finger[3]) and not (finger[4]):
                msg = '^'
            if not(finger[0]) and finger[1] and finger[2] and not(finger[3]) and not(finger[4]):
                msg = '$' + str(width) + ';'
            if not(finger[0]) and finger[1] and not(finger[2]) and not(finger[3]) and not(finger[4]):
                msg = '#' + str(width) + ';'

            # отправляем сообщение в Arduino
            if msg != '':
                msg = bytes(str(msg), 'utf-8')
                uart.write(msg)
                print(msg)

    cv2.imshow("Image", img)           # выводим окно с нашим изображением
    if cv2.waitKey(1) == ord('q'):     # ждем нажатия клавиши q в течение 1 мс
        break                          # если нажмут, всё закрываем