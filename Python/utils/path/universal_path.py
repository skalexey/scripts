import os
import pathlib
import re
import sys

from utils.log.logger import Logger

log = Logger()


def is_wsl_path(path):
	return path.startswith("/mnt/")

def is_windows_path(path):
	return path[1] == ":" or "\\" in path

def is_unix_path(path):
	return "/" in path

# Is path like /c/Users/...
def is_cyg_path(path):
	# if the first folder name is a sigle letter
	return re.match(r'^/[a-zA-Z]/', path) != None

def wslpath_to_windows(path):
	"""
	Converts a WSL Unix-style path to a Windows-style path.
	Example: '/mnt/c/Users/skoro' -> 'C:\\Users\\skoro'
	"""
	if path.startswith('/mnt/'):
		# Handle /mnt/c/... paths
		drive_letter = path[5].upper() + ':'
		windows_path = drive_letter + path[6:].replace('/', '\\')
		return windows_path
	else:
		# Assume it's a relative path
		return path.replace('/', '\\')

def windows_to_wslpath(path):
	"""
	Converts a Windows-style path to a WSL Unix-style path.
	Example: 'C:\\Users\\skoro' -> '/mnt/c/Users/skoro'
	"""
	if re.match(r'^[a-zA-Z]:\\', path):
		# Handle drive letter paths
		drive_letter = path[0].lower()
		path_replaced = path[2:].replace("\\", "/")
		wsl_path = f"/mnt/{drive_letter}{path_replaced}"
		return wsl_path
	else:
		# Assume it's a relative path
		return path.replace('\\', '/')

def cygpath_to_windows(path):
	"""
	Converts a Cygwin-like Unix-style path to a Windows-style path.
	Example:
	'/cygdrive/c/Users/skoro' -> 'C:\\Users\\skoro'
	'/c/Users/skoro' -> 'C:\\Users\\skoro'
	'/x/some/path' -> 'X:\\some\\path'
	"""
	import re

	# Match /x/... where x is a single letter
	if re.match(r'^/[a-zA-Z]/', path):
		drive_letter = path[1].upper() + ':'  # Extract and capitalize the drive letter
		windows_path = drive_letter + path[2:].replace('/', '\\')  # Replace '/' with '\'
		return windows_path
	elif path.startswith('/cygdrive/'):
		# Handle legacy /cygdrive/c/... paths
		drive_letter = path[10].upper() + ':'
		windows_path = drive_letter + path[11:].replace('/', '\\')
		return windows_path
	else:
		# Assume it's a relative path
		return path.replace('/', '\\')

def windows_to_cygpath(path):
	"""
	Converts a Windows-style path to a Cygwin-like Unix-style path.
	Example: 'C:\\Users\\skoro' -> '/c/Users/skoro' (if you want simpler format)
	"""
	if re.match(r'^[a-zA-Z]:\\', path):
		# Handle drive letter paths
		drive_letter = path[0].lower()
		path_replaced = path[2:].replace("\\", "/")
		# Return '/c/...' format (simpler)
		cygwin_path = f'/{drive_letter}{path_replaced}'
		return cygwin_path
	else:
		# Assume it's a relative path
		return path.replace('\\', '/')

def is_absolute_path(path):
	return os.path.isabs(path)

def system_path(path):
	import platform

	# Convert to a Path object
	path_processed = os.path.expanduser(path)  # Expands '~' to the user's home directory
	# Handle Windows-specific logic
	if is_absolute_path(path):
		if platform.system() == "Windows":
			if is_wsl_path(str(path_processed)):
				# Handle WSL path conversion
				return wslpath_to_windows(str(path_processed))
				# return subprocess.check_output(["wsl", "wslpath", "-w", path_processed]).decode().strip()
			elif is_cyg_path(str(path_processed)):
				# Handle Cygwin path conversion
				# return subprocess.check_output(["cygpath", "-w", path_processed]).decode().strip()
				return cygpath_to_windows(str(path_processed))
			else:
				# If absolute path, resolve it
				return path_processed
	return str(pathlib.Path(path_processed))


class UniversalPath(type(pathlib.Path())):  # Dynamically inherit the correct Path class for the system
	def __new__(cls, path, *args, **kwargs):
		# Preprocess the input path using your custom `system_path` logic
		syspath = system_path(path)
		# Call the parent class's __new__ with the preprocessed path
		return super().__new__(cls, syspath, *args, **kwargs)


if __name__ == "__main__":
	if len(sys.argv) > 2:  # TODO: check if __main__ works in place of this args check
		arr = []
		for i, a in enumerate(sys.argv):
			if (i > 1):
				arr.append(a)
		locals()[sys.argv[1]](*arr)
	elif len(sys.argv) == 2:
		locals()[sys.argv[1]]()
