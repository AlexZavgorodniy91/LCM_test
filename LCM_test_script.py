#!/usr/bin/env python3
import lgpio
import time
import threading
import serial
import signal
import sys
from datetime import datetime

# Настройки GPIO
PULSE_GPIO = 26   # Выходной пин для 1 Гц
PPS_GPIO = 11     # Вход PPS
CHIP = 0          # GPIO-чип 0

# Настройки UART
GPS_PORT = "/dev/ttyAMA4"
GPS_BAUDRATE = 9600

# Состояние
stop_event = threading.Event()

# Инициализация
h = lgpio.gpiochip_open(CHIP)
lgpio.set_mode(h, PULSE_GPIO, lgpio.OUTPUT)
lgpio.set_mode(h, PPS_GPIO, lgpio.INPUT)

def generate_pulse():
    while not stop_event.is_set():
        lgpio.gpio_write(h, PULSE_GPIO, 1)
        time.sleep(0.1)
        lgpio.gpio_write(h, PULSE_GPIO, 0)
        time.sleep(0.9)

def read_pps():
    while not stop_event.is_set():
        level = lgpio.gpio_read(h, PPS_GPIO)
        global last_pps
        last_pps = level
        time.sleep(0.1)

def read_gps():
    try:
        ser = serial.Serial(GPS_PORT, GPS_BAUDRATE, timeout=1)
    except serial.SerialException:
        return None
    while not stop_event.is_set():
        line = ser.readline().decode(errors='ignore').strip()
        if line.startswith("$GPGGA"):
            global last_nmea
            last_nmea = line
        time.sleep(0.1)
    ser.close()

# Переменные состояния
last_pps = 0
last_nmea = ""

# Запуск потоков
pulse_thread = threading.Thread(target=generate_pulse)
pps_thread = threading.Thread(target=read_pps)
gps_thread = threading.Thread(target=read_gps)

pulse_thread.start()
pps_thread.start()
gps_thread.start()

print("=== LCM Test Script Started ===")
print("GPIO26 — импульсы 1 Гц | GPIO11 — PPS вход | Данные GPS — /dev/ttyAMA4")
print("Нажмите Ctrl+C для выхода.\n")
print("=" * 100)
print("Время      | PPS   | Реле ЛВМ  | Данные GPS")
print("=" * 100)

# Основной цикл
try:
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        gps_data = last_nmea.ljust(80)
        print(f"{now}   | {last_pps}     | 1         | {gps_data}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nЗавершение по Ctrl+C")
    stop_event.set()
    pulse_thread.join()
    pps_thread.join()
    gps_thread.join()
    lgpio.gpiochip_close(h)
    print("GPIO очищены, выход.")
    sys.exit(0)
