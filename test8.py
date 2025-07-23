import os
import cv2
import numpy as np
import time
import random
import threading
from pynput import keyboard as kb
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
import mss
import contextlib
import pygame

# Tắt tiếng import pygame
with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        pygame.mixer.init()

keyboard = KeyboardController()
mouse = MouseController()
stop_program = False  # Để bắt phím q

# Nhận lựa chọn màn hình
while True:
    try:
        monitor_index = int(input("🖥️ Bạn có bao nhiêu màn hình? Chọn màn cần quét (1 hoặc 2): "))
        if monitor_index in [1, 2]:
            break
        else:
            print("⚠️ Chỉ chọn 1 hoặc 2.")
    except ValueError:
        print("⚠️ Nhập số.")

print("⏳ Đợi 10s vào game...")
time.sleep(10)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "image")
SOUND_PATH = os.path.join(IMAGE_DIR, "moicau.mp3")

def play_sound_blocking(path):
    try:
        sound = pygame.mixer.Sound(path)
        channel = sound.play()
        while channel.get_busy():
            time.sleep(0.1)
    except Exception:
        pass

def load_template(name, binary=False):
    path = os.path.join(IMAGE_DIR, name)
    img = cv2.imread(path, 0)
    if img is None:
        print(f"❌ Không thể tải ảnh {name}")
        exit(1)
    if binary:
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return img

# Load các template
template5 = load_template("5.png")
template7 = load_template("7.png")
template1 = load_template("1.png")
template2 = load_template("2.png")
template8 = load_template("8.png")

threshold = 0.85

def get_screen_gray(binary=False):
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_index]
        img = np.array(sct.grab(monitor))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        if binary:
            _, gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return gray

def check_template(template, binary=False):
    screen = get_screen_gray(binary=binary)
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    return len(loc[0]) > 0

def wait_for_image(template, timeout_seconds, binary=False):
    start = time.time()
    while time.time() - start < timeout_seconds and not stop_program:
        if check_template(template, binary=binary):
            return True
        time.sleep(0.5)
    return False

def click():
    mouse.press(Button.left)
    time.sleep(0.05)
    mouse.release(Button.left)

def hold_click(duration):
    mouse.press(Button.left)
    time.sleep(duration)
    mouse.release(Button.left)

def repeat_hold_click_until_template_gone(template_check, binary=False):
    while check_template(template_check, binary=binary) and not stop_program:
        hold_click(random.uniform(0.5, 0.7))
        time.sleep(random.uniform(0.4, 0.6))

def press_tab_until_5_or_7_detected(max_tries=20):
    tries = 0
    while tries < max_tries and not stop_program:
        keyboard.press(Key.tab)
        time.sleep(0.05)
        keyboard.release(Key.tab)
        time.sleep(0.45)
        tries += 1
        if check_template(template5) or check_template(template7):
            print("✅ Xác định được mồi câu")
            play_sound_blocking(SOUND_PATH)
            return True
    return False

def restart_loop():
    print("🎣 Đã hoàn thành 1 lần câu cá")
    print("⏳ Đợi 5s trước khi lặp...")
    time.sleep(5)
    print("🔁 Lặp lại vòng mới...")

def listen_for_q():
    def on_press(key):
        global stop_program
        if key == kb.Key.esc or (hasattr(key, 'char') and key.char == 'q'):
            print("🛑 Đã nhấn 'q' để thoát.")
            stop_program = True
            return False
    with kb.Listener(on_press=on_press) as listener:
        listener.join()

# Bắt đầu lắng nghe phím q
threading.Thread(target=listen_for_q, daemon=True).start()

print("🚀 Bắt đầu bot câu cá... Nhấn Q để thoát.")

try:
    while not stop_program:
        if not press_tab_until_5_or_7_detected():
            print("❌ Không xác định được mồi câu. Thoát.")
            break

        if stop_program: break

        keyboard.press('2')
        time.sleep(0.05)
        keyboard.release('2')
        time.sleep(1)

        if stop_program: break

        if check_template(template8):
            repeat_hold_click_until_template_gone(template8)
            restart_loop()
            continue

        if not wait_for_image(template1, 170):
            restart_loop()
            continue

        hold_click(random.uniform(0.8, 1.2))
        time.sleep(1)

        if not wait_for_image(template2, 230):
            restart_loop()
            continue

        click()
        time.sleep(1)

        if check_template(template8):
            repeat_hold_click_until_template_gone(template8)

        restart_loop()

except KeyboardInterrupt:
    print("🛑 Đã dừng bot.")

finally:
    cv2.destroyAllWindows()
    print("✅ Kết thúc chương trình.")
