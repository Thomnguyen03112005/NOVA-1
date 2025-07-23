import os
import cv2
import numpy as np
import time
import random
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
import mss

keyboard = KeyboardController()
mouse = MouseController()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "image")

def load_template(name, binary=False):
    path = os.path.join(IMAGE_DIR, name)
    img = cv2.imread(path, 0)
    if img is None:
        print(f"❌ Không thể tải ảnh {name}")
        exit(1)
    if binary:
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return img

# Load template
template5 = load_template("5.png", binary=True)
template7 = load_template("7.png", binary=True)
template1 = load_template("1.png")
template2 = load_template("2.png")
template3 = load_template("3.png")
template4 = load_template("4.png")
template6 = load_template("6.png")
template8 = load_template("8.png")

threshold = 0.85

def get_screen_gray(binary=False):
    with mss.mss() as sct:
        monitor = sct.monitors[2]  # thay đổi nếu dùng nhiều màn hình
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
    while time.time() - start < timeout_seconds:
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
    print("✊ Bắt đầu giữ chuột trái (lặp) cho đến khi ảnh 8 biến mất...")
    start = time.time()
    while check_template(template_check, binary=binary):
        hold_time = random.uniform(0.6, 1.0)
        release_time = random.uniform(0.4, 0.6)
        print(f"➡️  Giữ chuột {hold_time:.2f}s, nghỉ {release_time:.2f}s...")
        hold_click(hold_time)
        time.sleep(release_time)
        if time.time() - start > 60:
            print("⏰ Quá 60s vẫn còn ảnh 8. Thoát lặp.")
            break
    print("✅ Ảnh 8 đã biến mất.")

def press_tab_until_5_or_7_detected(max_wait=60, first_run=False):
    if first_run:
        print("⏳ Đợi 10s để vào game...")
        time.sleep(10)  # đợi 10s lần đầu tiên khi mở tool

    print("⏳ Bắt đầu nhấn Tab liên tục để hiện ảnh 5 hoặc 7...")
    start = time.time()
    while time.time() - start < max_wait:
        keyboard.press(Key.tab)
        time.sleep(0.05)
        keyboard.release(Key.tab)
        time.sleep(0.45)
        if check_template(template5, binary=True) or check_template(template7, binary=True):
            print("✅ Đã phát hiện ảnh 5 hoặc 7.")
            return True

    print("❌ Không tìm thấy ảnh 5 hoặc 7 trong thời gian chờ.")
    return False

def restart_loop():
    print("✅ Ảnh 8 đã biến mất.")
    print("⏳ Đợi 5s sau khi mất ảnh 8...")
    time.sleep(5)
    print("🔁 Bắt đầu vòng lặp mới...")

print("🚀 Bắt đầu bot câu cá... Nhấn Ctrl+C để thoát.")

try:
    first_run = True
    while True:
        # Lần đầu mở tool thì đợi 10s, các lần sau không đợi
        if not press_tab_until_5_or_7_detected(first_run=first_run):
            print("❌ Không thể mở kho đồ, thoát bot.")
            exit(1)
        first_run = False  # chỉ đợi 10s lần đầu

        while True:
            if check_template(template5, binary=True) or check_template(template7, binary=True):
                print("🎯 Phát hiện ảnh 5 hoặc 7. Nhấn phím 2.")
                keyboard.press('2')
                time.sleep(0.05)
                keyboard.release('2')
                time.sleep(1)

                if check_template(template8):
                    repeat_hold_click_until_template_gone(template8)
                    restart_loop()
                    # Sau khi restart_loop thì quay lại nhấn tab không đợi 10s
                    if not press_tab_until_5_or_7_detected():
                        print("❌ Không thể mở kho đồ, thoát bot.")
                        exit(1)
                    continue

                if not wait_for_image(template1, 170):
                    print("⏰ Timeout ảnh 1.")
                    restart_loop()
                    if not press_tab_until_5_or_7_detected():
                        print("❌ Không thể mở kho đồ, thoát bot.")
                        exit(1)
                    continue

                hold_time_1 = random.uniform(1.0, 1.5)
                print(f"🖱️ Ảnh 1 xuất hiện → giữ chuột trái {hold_time_1:.2f}s.")
                hold_click(hold_time_1)
                time.sleep(1)

                if not wait_for_image(template2, 230):
                    print("⏰ Timeout ảnh 2.")
                    restart_loop()
                    if not press_tab_until_5_or_7_detected():
                        print("❌ Không thể mở kho đồ, thoát bot.")
                        exit(1)
                    continue

                print("🖱️ Ảnh 2 xuất hiện → Click chuột trái.")
                click()
                time.sleep(1)

                if check_template(template8):
                    repeat_hold_click_until_template_gone(template8)
                    restart_loop()
                    if not press_tab_until_5_or_7_detected():
                        print("❌ Không thể mở kho đồ, thoát bot.")
                        exit(1)
                    continue

                restart_loop()
                if not press_tab_until_5_or_7_detected():
                    print("❌ Không thể mở kho đồ, thoát bot.")
                    exit(1)
            else:
                print("🔍 Đang tìm ảnh 5 hoặc 7...")
                time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Đã dừng bot.")

finally:
    cv2.destroyAllWindows()
