import RPi.GPIO as GPIO
import time
import threading
import sys
import serial

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN)         # GPIO11 — вход PPS
GPIO.setup(26, GPIO.OUT)        # GPIO26 — выход на реле
GPIO.output(26, GPIO.LOW)

gpio26_state = False
latest_gpgga = "ожидание..."
lock = threading.Lock()

pulse_on = 0.5     # 0.5 сек HIGH
pulse_off = 0.5    # 0.5 сек LOW (итого 1 Гц)

def pulse_generator():
    global gpio26_state
    while True:
        with lock:
            gpio26_state = True
        GPIO.output(26, GPIO.HIGH)
        time.sleep(pulse_on)

        with lock:
            gpio26_state = False
        GPIO.output(26, GPIO.LOW)
        time.sleep(pulse_off)

def gps_reader():
    global latest_gpgga
    try:
        with serial.Serial('/dev/ttyAMA4', 9600, timeout=1) as ser:
            while True:
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("$GPGGA"):
                    with lock:
                        latest_gpgga = line
    except Exception as e:
        with lock:
            latest_gpgga = f"GPS ошибка: {e}"

def print_table_header():
    print("=" * 100)
    print("{:<10} | {:<5} | {:<9} | {:<70}".format("Время", "PPS", "Реле ЛВМ", "Данные GPS"))
    print("=" * 100)

def monitor_input():
    print_table_header()
    while True:
        with lock:
            output_state = int(gpio26_state)
            gps_data = latest_gpgga
        input_state = GPIO.input(11)
        t = time.strftime("%H:%M:%S")
        row = "{:<10} | {:<5} | {:<9} | {:<70}".format(t, input_state, output_state, gps_data)
        sys.stdout.write("\r" + row[:100])  # обрезаем до ширины терминала
        sys.stdout.flush()
        time.sleep(0.2)

try:
    print("=== LCM Test Script Started ===")
    print("GPIO26 — импульсы 1 Гц | GPIO11 — PPS вход | Данные GPS — /dev/ttyAMA4")
    print("Нажмите Ctrl+C для выхода.\n")

    threading.Thread(target=pulse_generator, daemon=True).start()
    threading.Thread(target=gps_reader, daemon=True).start()
    monitor_input()

except KeyboardInterrupt:
    print("\nЗавершение по Ctrl+C")

finally:
    GPIO.cleanup()
    print("GPIO очищены, выход.")
