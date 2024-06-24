import os
from datetime import datetime as _datetime

import utils.function
from utils.log.logger import *

log = Logger()

def backup_path(path, datetime=None, date_format=None):
	_datetime = datetime or _datetime.now()
	_date_format = date_format or "%Y-%m-%d_%H-%M-%S"
	def gen_backup_path(cnt):
		cnt_addition = f"_{cnt}" if cnt > 0 else ""
		return path + "." + _datetime.strftime(_date_format) + cnt_addition + ".bak"
	cnt = 0
	while os.path.exists(backup_path := gen_backup_path(cnt)):
		cnt += 1
	return backup_path

def backup(path, datetime=None, date_format=None):
	target_path = backup_path(path, datetime, date_format)
	log.warning(utils.function.msg(f"Backing up to '{target_path}'"))
	try:
		os.rename(path, target_path)
	except Exception as e:
		log.error(utils.function.msg(f"Error backing up file '{path}' to '{target_path}': {e}"))
		return None
	return target_path
