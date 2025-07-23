import os
import sys
import hashlib
import json
import time
import datetime
import uuid
import platform
import requests
import socket
import config  # file config.py của bạn
import subprocess
import contextlib
import io

def get_cpu_id():
    """
    Lấy CPU ID trên Windows bằng lệnh wmic.
    Nếu không phải Windows hoặc lỗi thì trả về mã mặc định.
    """
    if platform.system() != "Windows":
        return "BFEBFBFF000306C3"  # mã giả định nếu không phải Windows
    
    try:
        output = subprocess.check_output("wmic cpu get ProcessorId", shell=True, text=True)
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            cpu_id = lines[1].strip()
            if cpu_id:
                return cpu_id
    except Exception as e:
        print(f"⚠️ Lỗi lấy CPU ID: {e}")
    return "BFEBFBFF000306C3"  # fallback

def get_mac_address():
    """
    Lấy địa chỉ MAC hợp lệ đầu tiên
    """
    mac = None
    for interface in socket.if_nameindex():
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                           for ele in range(0,8*6,8)][::-1])
            if mac and mac != "00:00:00:00:00:00":
                break
        except:
            continue
    if not mac:
        mac = "FCAA14DA4010"
    return mac.replace(":", "").upper()

def hash_sha256(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def send_discord_webhook(cpu_id, mac, cpu_hash, mac_hash):
    # Gửi thông tin format đẹp, có dấu . ở đầu cuối mỗi dòng để dễ phân biệt
    content = (
        "----------------------------------------\n"
        "📥 **Yêu cầu duyệt mã băm mới**\n"
        f"CPU ID:\n{cpu_id}.\n"
        f"MAC Address:\n{mac}.\n"
        f"Hash CPU:\n{cpu_hash}.\n"
        f"Hash MAC:\n{mac_hash}.\n"
        "Từ tool auto câu cá Python\n"
        "----------------------------------------"
    )
    data = {"content": content}
    try:
        r = requests.post(config.WEBHOOK_URL, json=data)
        if r.status_code in (200, 204):
            print("")  # Không hiện gì
        else:
            print(f"⚠️ Lỗi gửi webhook: {r.status_code} {r.text}")
    except Exception as e:
        print(f"⚠️ Lỗi gửi webhook: {e}")

def check_hash_approved(cpu_hash, mac_hash):
    try:
        r = requests.get(config.KEY_JSON_URL, timeout=10)
        r.raise_for_status()
        keys = r.json()  # JSON dạng list
    except Exception as e:
        print(f"❌ Lỗi tải danh sách key: {e}")
        return False

    # Chắc chắn keys là list
    if not isinstance(keys, list):
        print("❌ Dữ liệu key không hợp lệ (không phải list).")
        return False

    # So sánh hash CPU hoặc MAC trong keys
    for k in keys:
        code_hash = k.get("code", "").lower()
        if cpu_hash.lower() == code_hash or mac_hash.lower() == code_hash:
            return True
    return False

def main_check():
    print("🔍 Kiểm tra hash CPU và MAC, gửi thông tin thiết bị qua Discord...")

    cpu_id = get_cpu_id()
    mac = get_mac_address()
    cpu_hash = hash_sha256(cpu_id)
    mac_hash = hash_sha256(mac)

    send_discord_webhook(cpu_id, mac, cpu_hash, mac_hash)

    if not check_hash_approved(cpu_hash, mac_hash):
        print("❌ Bạn chưa được duyệt sử dụng tool, vui lòng liên hệ Admin.")
        print("👉 Discord hỗ trợ: https://discord.gg/y4CSXVsQuD")
        print("👉 Tiktok: https://www.tiktok.com/@thowmm2005")
        print("\n... Vui lòng đóng tool thủ công khi bạn sẵn sàng ...\n")
        # Không tự exit để người dùng chủ động đóng
        while True:
            time.sleep(60)  # giữ chương trình chạy chờ người dùng thoát
    else:
        print("✅ Bạn đã được duyệt sử dụng tool. Tiếp tục chạy chức năng...")

if __name__ == "__main__":
    # Chặn thông báo khi import pygame (giảm thông báo khi init mixer)
    import pygame
    f = io.StringIO()
    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()

    main_check()

    # Sau khi check ok, import và chạy phần tool câu cá của bạn (test6.py)
    import test6  # chắc chắn có file test6.py trong cùng thư mục
