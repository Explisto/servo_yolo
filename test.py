import PCA9685
import ServoPCA9685
import time
import smbus

import sys



i2cBus=smbus.SMBus(1)
# Активация сервоприводов и создание объектов класса
pca9685 = PCA9685.PCA9685(i2cBus, 0x70)
servo_oX = ServoPCA9685.ServoPCA9685(pca9685, PCA9685.CHANNEL00, 130, 510)
time.sleep(0.5)
servo_oY = ServoPCA9685.ServoPCA9685(pca9685, PCA9685.CHANNEL01, 130, 510)
time.sleep(0.5)




servo_oX.disable()
servo_oY.disable()