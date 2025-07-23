import os
import cv2
import numpy as np
import time
from pynput.keyboard import Controller
import mss  # Dùng để chụp màn hình cụ thể

keyboard = Controller()

# Đọc ảnh mẫu (template)
template1 = cv2.imread("f:/nova/image/5.png", 0)
template2 = cv2.imread("f:/nova/image/7.png", 0)
threshold = 0.85  # Độ khớp

def get_monitor_screen(monitor_index=1):
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index >= len(monitors):
            print(f"❌ Không có màn hình số {monitor_index}")
            return None
        monitor = monitors[monitor_index]
        img = np.array(sct.grab(monitor))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return gray

def check_image_on_screen(template, monitor_index=1):
    screen = get_monitor_screen(monitor_index)
    if screen is None:
        return False

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    return len(loc[0]) > 0

# --- Chạy vòng lặp ---
while True:
    time.sleep(1)  # delay để không spam
    if check_image_on_screen(template1, monitor_index=1) or check_image_on_screen(template2, monitor_index=1):
        print("🎯 Phát hiện ảnh! Nhấn phím 2.")
        keyboard.press('2')
        keyboard.release('2')
        time.sleep(1)
    else:
        print("🔍 Không phát hiện...")
