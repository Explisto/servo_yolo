from ultralytics import YOLO

# Подключение модуля камеры
from picamera2 import Picamera2

import cv2

# Вызов видео в отдельном потоке
# Инициализация объекта - камеры
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Загрузка модели YOLOv8
model = YOLO('best.pt')

while True:
    # Захват кадра
    frame = picam2.capture_array()   

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


    # Отображение картинки с камеры
    cv2.imshow('Camera', annotaded_frame)
    ch = cv2.waitKey(1)

    # Условие окончания работы программы
    if ch == 27:
        break

# Освобождение ресурсов и закрытие окон
cv2.destroyAllWindows()