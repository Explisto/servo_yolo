import PCA9685
import ServoPCA9685
import time
import smbus
import cv2
import numpy as np
import sys

# Подключение модуля камеры
from picamera2 import Picamera2

# Модель YOLO
from ultralytics import YOLO

# Многопоточность в видео
cv2.startWindowThread()

# Вызов видео в отдельном потоке
# Инициализация объекта - камеры
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Определение основных цветов
color_red=(0, 0, 255)
color_blue=(255, 0, 0)


i2cBus=smbus.SMBus(1)
# Активация сервоприводов и создание объектов класса
pca9685 = PCA9685.PCA9685(i2cBus, 0x70)
servo_oX = ServoPCA9685.ServoPCA9685(pca9685, PCA9685.CHANNEL00, 130, 500)
time.sleep(0.05)
servo_oY = ServoPCA9685.ServoPCA9685(pca9685, PCA9685.CHANNEL01, 130, 500)
time.sleep(0.05)

# Загрузка модели YOLOv8
model = YOLO('best.pt')
# Создание файла
f = open('text.txt', 'w')

def Camera():

    angle_oX = 90
    angle_oY = 90

    # Инициализация функции для работ с камерой
    while True:

        # Захват кадра
        frame = picam2.capture_array()                                                                              # Получение картинки из видеопотока
        height, widht = frame.shape[:2]                                                                             # Нахождение размеров картинки
        Centr_X = int(widht / 2)
        # Определение контрольных точек
        Centr_Y = int(height / 2)

        start_point = (Centr_X - 20,Centr_Y - 20)
        end_point = (Centr_X + 20, Centr_Y + 20)

        # Обработка кадра с помощью модели YOLO
        results = model(frame)

        annotaded_frame = results[0].plot()

        boxes = results[0].boxes.xyxy.cpu().numpy()

        if len(boxes) > 0:
            x_1 = int(boxes[0][0])
            y_1 = int(boxes[0][1])
            x_2 = int(boxes[0][2])
            y_2 = int(boxes[0][3])
            print("Координаты = ", x_1, y_1, x_2, y_2)

            # f.write(str(x_1), str(y_1), str(x_2), str(y_2))


            '''
            cv2.circle(img, (x, y), 5, color_blue, 2)
            # Отображение информации на экране
            cv2.putText(img, "x color%d;y color%d" % (x, y), (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
            color_blue, 2)
            cv2.line(img, (x, y), (Centr_X, Centr_Y), color_blue, 2)
            cv2.putText(img, "x cells %d;y cells%d" % (Centr_X - x, Centr_Y - y), (Centr_X + 10,Centr_Y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 1, color_red, 2)
            cv2.rectangle(img, start_point, end_point, color_red, 2)
            '''
            x = (x_1 + x_2) / 2
            y = (y_1 + y_2) / 2
            # Вызов функции для поиска смещения
            d_x, d_y = Vector(Centr_X - x, Centr_Y - y)
            
            # Приращение текущей коодинате полученного значения
            angle_oX = angle_oX + d_x
            angle_oY = angle_oY + d_y
            
            # Ограничения для работы сервопривода
            if angle_oX >= 180: 
                angle_oX = 180

            if angle_oX <= 0:
                angle_oX = 0

            if angle_oY >= 180:
                angle_oY = 180

            if angle_oY <= 0:
                angle_oY = 0
            
            # Установка углов сервоприводов
            print('angle_oX = ', angle_oX)
            print('angle_oY = ', angle_oY)
            servo_oX.set_angle(angle_oX)
            servo_oY.set_angle(angle_oY)
            
        # Отображение картинки с камеры
        cv2.imshow('Camera', annotaded_frame)

        video_writer = cv2.VideoWriter("inf.avi", -1, 40, (640,480))
        ch = cv2.waitKey(1)

        # Условие окончания работы программы
        if ch == 27:
            video_writer.release()
            break

# Определение функции для расчета приращения координат
def Vector(X, Y):
    
    delta_x = 0
    delta_y = 0
    vector = np.array([X, Y])
    LEN = int(np.sqrt(pow(vector[0], 2) + pow(vector[1], 2)))
    # Расчет расстояния между центром экрана и точкой слежения
    k = int(np.log(LEN) / 2)
    # Расчет приращения
    if LEN <= 40:
        None

    # Добавление приращения к углу отклонения сервоприводов
    elif LEN > 40 and X < 0 and Y > 0:
        delta_x -= k
        delta_y -= k

    elif LEN > 40 and X > 0 and Y > 0:
        delta_x += k
        delta_y -= k
    
    elif LEN > 40 and X < 0 and Y < 0:
        delta_x -= k
        delta_y += k
    
    elif LEN > 40 and X > 0 and Y < 0:
        delta_x += k
        delta_y += k
    
    return delta_x, delta_y

# Основное тело функции
if __name__ == '__main__':
    try:
        Camera()
        servo_oX.disable()
        servo_oY.disable()
        
    except KeyboardInterrupt:
        print('Exit pressed Ctrl+C')
        cv2.destroyAllWindows()