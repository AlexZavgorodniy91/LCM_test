import RPi.GPIO as GPIO
import time

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.IN)         # GPIO11 — вход
GPIO.setup(23, GPIO.OUT)        # GPIO23 — выход
GPIO.output(23, GPIO.LOW)       # Начальное состояние выхода

pulse_duration = 0.1            # Длительность импульса (в секундах)
check_interval = 0.5            # Интервал между проверками

print("Старт мониторинга GPIO11. Нажмите Ctrl+C для выхода.\n")

try:
    while True:
        input_state = GPIO.input(11)
        print(f"[{time.strftime('%H:%M:%S')}] GPIO11 = {input_state}")

        if input_state == GPIO.HIGH:
            print(" → Импульс на GPIO23")
            GPIO.output(23, GPIO.HIGH)
            time.sleep(pulse_duration)
            GPIO.output(23, GPIO.LOW)

        time.sleep(check_interval)

except KeyboardInterrupt:
    print("\nЗавершение по Ctrl+C")

finally:
    GPIO.cleanup()
    print("GPIO очищены")