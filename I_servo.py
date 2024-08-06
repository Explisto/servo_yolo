import PCA9685
import ServoPCA9685
import time
import smbus
import cv2
import numpy as np
import sys

# Подключение модуля камеры
from picamera2 import Picamera2

# Многопоточность в видео
cv2.startWindowThread()

# Вызов видео в отдельном потоке
# Инициализация объекта - камеры
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
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

def Camera(angle_oX, angle_oY):
    # Инициализация функции для работ с камерой
    while True:
        img = picam2.capture_array()                                                                                # Получение картинки из видеопотока
        height, widht = img.shape[:2]                                                                               # Нахождение размеров картинки
        Centr_X = int(widht / 2)
        # Определение контрольных точек
        Centr_Y = int(height / 2)
        start_point = (Centr_X - 20,Centr_Y - 20)
        end_point = (Centr_X + 20, Centr_Y + 20)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Определение цвета для поиска
        h_min = np.array((45, 100, 50), np.uint8)
        h_max = np.array((75, 255, 255), np.uint8)
        # Нахождение координат отслеживаемого цвета
        thresh = cv2.inRange(hsv, h_min, h_max)
        moments = cv2.moments(thresh, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']
    
        if dArea > 100:             # Если был найден отслеживаемый цвет
            # Вычисление координат
            x = int(dM10 / dArea)
            y = int(dM01 / dArea)

            cv2.circle(img, (x, y), 5, color_blue, 2)

            # Отображение информации на экране
            cv2.putText(img, "x color%d;y color%d" % (x, y), (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
            color_blue, 2)
            cv2.line(img, (x, y), (Centr_X, Centr_Y), color_blue, 2)
            cv2.putText(img, "x cells %d;y cells%d" % (Centr_X - x, Centr_Y - y), (Centr_X + 10,Centr_Y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 1, color_red, 2)
            cv2.rectangle(img, start_point, end_point, color_red, 2)

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
        cv2.imshow('Camera', img)
        ch = cv2.waitKey(1)

        # Условие окончания работы программы
        if ch == 27:
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
        Camera(90, 90)
        servo_oX.disable()
        servo_oY.disable()
    except KeyboardInterrupt:
        print('Exit pressed Ctrl+C')
        cv2.destroyAllWindows()