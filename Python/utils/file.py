import os
import shutil
import sys
from datetime import datetime as _datetime

import utils.function
from utils.log.logger import Logger

log = Logger()

def backup_path(path, datetime=None, date_format=None):
	"""
    Generates a unique backup name with date and time and returns it as a path in the same directory as the original file.
	"""
	dt = datetime or _datetime.now()
	_date_format = date_format or "%Y-%m-%d_%H-%M-%S"
	def gen_backup_path(cnt):
		cnt_addition = f"_{cnt}" if cnt > 0 else ""
		return path + "." + dt.strftime(_date_format) + cnt_addition + ".bak"
	backup_path = gen_free_path(gen_func=gen_backup_path)
	return backup_path

def gen_free_path(path=None, gen_func=None):
	"""
	Generates a unique file name by appending a counter or using a custom generation function and returns it as a path in the same directory as the original file.
	"""
	if gen_func is None:
		if path is None:
			raise ValueError("Either 'path' or 'gen_func' must be provided")
		dir = os.path.dirname(path)
		basename = os.path.basename(path)
		name, ext = os.path.splitext(basename)
		def _gen_func(cnt):
			cnt_addition = f"-{cnt}" if cnt > 0 else ""
			ext_addition = f".{ext}" if ext else ""
			return os.path.join(dir, f"{name}{cnt_addition}{ext_addition}")
	else:
		_gen_func = gen_func
	cnt = 0
	while os.path.exists(free_path := gen_func(cnt)):
		cnt += 1
	return free_path

def restore(backed_path, original_path):
	"""
	Restores a backup file to its original location with additional checks for integrity and safety of this operation.
	"""
	if not os.path.exists(backed_path):
		return -1
	# Log the creation of the original file path if it doesn't exist
	if not os.path.exists(os.path.dirname(original_path)):
		os.makedirs(os.path.dirname(original_path))
	try:
		shutil.copy2(backed_path, original_path)
		verify_result = verify_copy(backup_path, original_path)
		if verify_result != 0:
			log.error(utils.function.msg(f"Error verifying restored file '{original_path}': {verify_result}"))
			return verify_result
	except Exception as e:
		log.error(utils.function.msg(f"Error restoring file '{backed_path}' to '{original_path}': {e}"))
		return -2
	return 0

def backup(path, datetime=None, date_format=None):
	"""
	Creates a backup of a file by copying it to a new location with a timestamped unique name.
	Performs additional checks for the integrity and safety of this operation.
	"""
	target_path = backup_path(path, datetime, date_format)
	log.warning(utils.function.msg(f"Backing up to '{target_path}'"))
	try:
		shutil.copy2(path, target_path)
		verify_result = verify_copy(path, target_path)
		if verify_result != 0:
			log.error(utils.function.msg(f"Error verifying backup file '{target_path}': {verify_result}"))
			return verify_result
	except Exception as e:
		log.error(utils.function.msg(f"Error backing up file '{path}' to '{target_path}': {e}"))
		return -1
	return target_path

def verify_copy(source_path, destination_path):
	"""
	Verifies the integrity of a copied file by comparing its size and modification time.
	"""
	if not os.path.exists(destination_path):
		return 1
	source_stat = os.stat(source_path)
	dest_stat = os.stat(destination_path)
	if source_stat.st_size != dest_stat.st_size:
		return 2
	if source_stat.st_mtime != dest_stat.st_mtime:
		return 3
	return 0

def is_open(fpath):
	"""
	Checks if a file at the given path is open by attempting to rename it.
	"""
	if not os.path.exists(fpath):
		return False
	try:
		os.rename(fpath, f'{fpath}.bckp')
		os.rename(f'{fpath}.bckp', fpath)
	except OSError:
		return True
	except Exception as e:
		return True
	return False

