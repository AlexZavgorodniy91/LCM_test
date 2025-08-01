import os

CONFIG_PATH = "/boot/firmware/config.txt"
LINE_TO_ADD = "dtoverlay=uart4"

def add_dtoverlay_uart4():
    if not os.path.exists(CONFIG_PATH):
        print(f"Файл {CONFIG_PATH} не найден.")
        return

    with open(CONFIG_PATH, "r") as file:
        lines = file.readlines()

    if any(LINE_TO_ADD in line for line in lines):
        print("Строка уже присутствует в config.txt.")
    else:
        with open(CONFIG_PATH, "a") as file:
            file.write("\n" + LINE_TO_ADD + "\n")
        print("Строка добавлена в config.txt.")

if __name__ == "__main__":
    add_dtoverlay_uart4()
