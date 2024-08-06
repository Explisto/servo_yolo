# Создание системы слежения на Raspberry Pi 4

Сделано на основе статей:

#https://habr.com/ru/articles/821971/#

#https://habr.com/ru/articles/714232/#


_Необходимые устройства_

1. Микрокомпьютер Raspberry Pi 4
2. Два сервопривода SG90
3. Драйвер для сервоприводов PCA9685
4. Переходник TSL
5. Специальные крепления из КИТ набора
6. Набор батареек и батарейный отсек на 2 штуки
7. Провода для подключения

_Текущие задачи_

1. Установить ОС Debian крайней версии на Raspberry Pi 4
2. Провести обновление системы в командной строке
   ```
   sudo apt update
   ```
4. Включить в настройках i2c - интерфейс (команда для открытия меню настроеек прописана ниже)
    ```
   sudo raspi-config
   ```
5. Собираем механизм
6. Скачиваем библиотеки отдельно (из-за особенностей архитектуры процессора ARM-64 нужно скачать данные библиотеки через менеджер пакетов apt)
   * sudo apt install python3-opencv
   * sudo apt install python3-pillow
   * sudo apt install python3-PyYAML
   * sudo apt install python3-scipy
   * sudo apt install python3-torch
   * sudo apt install python3-torchvision
   * sudo apt install python3-tqdm
   * sudo apt install libcap-dev
7. Переходим в папку проекта командой cd
   ```
   cd Documents/projects/<name folder>
   ```
8. Для работы проекта необходимо создать виртуальное окружение с помощью команды
   ```
   python3 -m venv <имя окружения> --system_site_packages
   ```
   И активируем его
   ```
   source <имя окружения>/bin/activate
   ```
9. После этого установить библиотеки
   ```
   pip install picamera2
   pip install ultralitics
   ```
10. Скачиваем датасет для обучения нейронной сети модели YOLOv8 с сайта kaggle
  ```
  https://www.kaggle.com/datasets/muki2003/yolo-drone-detection-dataset
  ```
11. Разделяем изображения на 3 папки: тренировочные, валидные и тестовые
12. Обучаем нейронную сеть
    ```
    yolo task=detect mode=train model=yolov8n.pt imgsz=640 data=custom_data.yaml epochs=10 batch=8 name=yolov8n_custom
    ```
13. После получения файла с расширением pt помещаем его в директорию проекта
14. Запускаем проект в виртуальной среде с помощью команды
    ```
    python3 <имя исполняемого файла>
     ```
Доработки:
- [ ] Сделать запись видео применения со всеми отметками
- [ ] Сделать автозапуск скрипта после активации микрокомпьютера
- [ ] Создать механизм крепления

   
