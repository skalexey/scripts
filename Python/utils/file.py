import os
import shutil
from datetime import datetime as _datetime

import utils.function
from utils.log.logger import *

log = Logger()

def backup_path(path, datetime=None, date_format=None):
	dt = datetime or _datetime.now()
	_date_format = date_format or "%Y-%m-%d_%H-%M-%S"
	def gen_backup_path(cnt):
		cnt_addition = f"_{cnt}" if cnt > 0 else ""
		return path + "." + dt.strftime(_date_format) + cnt_addition + ".bak"
	cnt = 0
	while os.path.exists(backup_path := gen_backup_path(cnt)):
		cnt += 1
	return backup_path

def restore(backed_path, original_path):
	if not os.path.exists(backed_path):
		return -1
	# Log the creation of the original file path if it doesn't exist
	if not os.path.exists(os.path.dirname(original_path)):
		os.makedirs(os.path.dirname(original_path))
	try:
		shutil.copy2(backed_path, original_path)
		verify_result = verify_copy(backup_path, path)
		if verify_result != 0:
			log.error(utils.function.msg(f"Error verifying restored file '{original_path}': {verify_result}"))
			return verify_result
	except Exception as e:
		log.error(utils.function.msg(f"Error restoring file '{backed_path}' to '{original_path}': {e}"))
		return -2
	return 0

def backup(path, datetime=None, date_format=None):
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
	if not os.path.exists(destination_path):
		return 1
	source_stat = os.stat(source_path)
	dest_stat = os.stat(destination_path)
	if source_stat.st_size != dest_stat.st_size:
		return 2
	if source_stat.st_mtime != dest_stat.st_mtime:
		return 3
	return 0
