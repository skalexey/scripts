import os
from datetime import datetime as _datetime


def backup_path(path, datetime=None, date_format="%Y-%m-%d--%H-%M-%S"):
	def gen_backup_path(cnt):
		cnt_addition = f"_{cnt}" if cnt > 0 else ""
		current_datetime = datetime or _datetime.now()
		return path + "." + current_datetime.strftime(date_format) + cnt_addition + ".bak"
	cnt = 0
	while os.path.exists(backup_path := gen_backup_path(cnt)):
		cnt += 1
	return backup_path
