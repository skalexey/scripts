import hashlib
import io
import os
import re
import sys
import time
from datetime import datetime

import win32gui
from PIL import ImageGrab

CHECK_INTERVAL = 0.3333333333333333333333333333333333333333333333  # seconds

def get_active_window_title():
	hwnd = win32gui.GetForegroundWindow()
	return win32gui.GetWindowText(hwnd).strip() or "UnknownApp"

def get_clipboard_image():
	time_before = time.time()
	img = ImageGrab.grabclipboard()
	time_after = time.time()
	print(f"[+] Time taken to grab clipboard image: {time_after - time_before:.2f} seconds")

	if isinstance(img, ImageGrab.Image.Image):
		return img
	return None


def calculate_md5(img, size=(64, 64)):
	img_small = img.copy().resize(size).convert("RGB")
	return hashlib.md5(img_small.tobytes()).hexdigest()

def get_screenshot_path(base_dir, app_name, timestamp):
	base_name = f"{app_name}_{timestamp}.png"
	full_path = os.path.join(base_dir, base_name)
	counter = 1
	while os.path.exists(full_path):
		full_path = os.path.join(base_dir, f"{app_name}_{timestamp}_{counter}.png")
		counter += 1
	return full_path

def save_screenshot_if_new(img, last_md5, pictures_dir):
	md5_current = calculate_md5(img)
	if md5_current == last_md5:
		return last_md5  # No change

	app_name = re.sub(r'[\\/:*?"<>|]', '_', get_active_window_title()).replace(" ", "_")
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	file_path = get_screenshot_path(pictures_dir, app_name, timestamp)
	img.save(file_path)
	print(f"[+] Saved new screenshot: {file_path}")
	return md5_current

def main():
	if "--install" in sys.argv:
		import win32com.client
		import winshell
		startup_dir = winshell.startup()
		script_path = os.path.abspath(__file__)
		shortcut_path = os.path.join(startup_dir, "clipboard_image_auto_saver.lnk")

		pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
		if not os.path.exists(pythonw_path):
			print(f"[!] pythonw.exe not found next to {sys.executable}")
			return

		shell = win32com.client.Dispatch("WScript.Shell")
		shortcut = shell.CreateShortCut(shortcut_path)
		shortcut.TargetPath = pythonw_path
		shortcut.Arguments = f'"{script_path}"'
		shortcut.WorkingDirectory = os.path.dirname(script_path)
		shortcut.IconLocation = script_path
		shortcut.save()
		print(f"[+] Shortcut created: {shortcut_path}")
		return

	pictures_dir = os.path.join(os.path.expanduser("~"), "OneDrive", "Pictures", "Screenshots")
	os.makedirs(pictures_dir, exist_ok=True)

	last_md5 = None
	print("Monitoring clipboard for image changes... Press Ctrl+C to stop.")
	while True:
		try:
			image = get_clipboard_image()
			if image:
				# time_before = time.time()
				last_md5 = save_screenshot_if_new(image, last_md5, pictures_dir)
				# time_after = time.time()
				# print(f"[+] Time taken to process image: {time_after - time_before:.2f} seconds")
		except Exception as e:
			print(f"[!] Error: {e}")
		time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
	main()
