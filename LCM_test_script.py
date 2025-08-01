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
gps_running = True

def generate_single_pulse():
    global gpio26_state
    with lock:
        gpio26_state = True
    GPIO.output(26, GPIO.HIGH)
    time.sleep(1)
    with lock:
        gpio26_state = False
    GPIO.output(26, GPIO.LOW)

def gps_reader():
    global latest_gpgga, gps_running
    try:
        with serial.Serial('/dev/ttyAMA4', 9600, timeout=1) as ser:
            while gps_running:
                line = ser.readline().decode(errors='ignore').strip()
                if line.startswith("$GPGGA"):
                    with lock:
                        latest_gpgga = line
    except Exception as e:
        with lock:
            latest_gpgga = f"GPS ошибка: {e}"

def print_table_header():
    print("=" * 90)
    print("{:<10} | {:<5} | {:<65}".format("Время", "PPS", "Данные GPS"))
    print("=" * 90)

def monitor_input(stop_event):
    print_table_header()
    while not stop_event.is_set():
        with lock:
            gps_data = latest_gpgga
        input_state = GPIO.input(11)
        t = time.strftime("%H:%M:%S")
        row = "{:<10} | {:<5} | {:<65}".format(t, input_state, gps_data)
        sys.stdout.write("\r" + row[:90])
        sys.stdout.flush()
        time.sleep(0.2)
    print()

try:
    print("=== LCM Test Script Started ===")
    print("GPIO26 — ручной импульс | GPIO11 — PPS вход | GPS: /dev/ttyAMA4")
    print("Нажмите Ctrl+C для выхода.")
    print("\nДля подачи импульса на реле запуска ЛВМ нажмите [Enter]\n")

    # Запуск GPS потока
    gps_thread = threading.Thread(target=gps_reader, daemon=True)
    gps_thread.start()

    # Таблица
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_input, args=(stop_event,))
    monitor_thread.start()

    input()  # Ждём Enter
    stop_event.set()  # Остановить таблицу
    gps_running = False
    gps_thread.join(timeout=1)

    generate_single_pulse()
    print("Импульс на реле подан.\nРабота скрипта завершена.")

except KeyboardInterrupt:
    print("\nЗавершение по Ctrl+C")

finally:
    GPIO.cleanup()

