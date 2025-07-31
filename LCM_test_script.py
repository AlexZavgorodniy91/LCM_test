import RPi.GPIO as GPIO
import time
import threading
import sys

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN)         # GPIO11 — вход
GPIO.setup(26, GPIO.OUT)        # GPIO26 — выход
GPIO.output(26, GPIO.LOW)

# Состояние выхода (будет обновляться из потока)
gpio26_state = False
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

def print_table_header():
    print("=" * 50)
    print("{:<10} | {:<10} | {:<10}".format("Время", "PPS", "Реле ЛВМ"))
    print("=" * 50)

def monitor_input():
    print_table_header()
    while True:
        input_state = GPIO.input(11)
        with lock:
            output_state = int(gpio26_state)
        t = time.strftime("%H:%M:%S")
        row = "{:<10} | {:<10} | {:<10}".format(t, input_state, output_state)
        sys.stdout.write("\r" + row)
        sys.stdout.flush()
        time.sleep(0.2)

try:
    print("=== LCM Test Script Started ===")
    print("Импульсы на Реле ЛВМ (GPIO23 - 1 Гц) + мониторинг PPS (GPIO11)")
    print("Нажмите Ctrl+C для выхода.\n")

    threading.Thread(target=pulse_generator, daemon=True).start()
    monitor_input()

except KeyboardInterrupt:
    print("\nЗавершение по Ctrl+C")

finally:
    GPIO.cleanup()
    print("GPIO очищены, выход.")
