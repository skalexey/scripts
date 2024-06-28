import collections
import json
import os
import re
import shutil

import utils  # Lazy import
import utils.file
import utils.function
from utils.log.logger import Logger

log = Logger()

def is_primitive(value):
	return isinstance(value, (int, str, bool, float, type(None)))

def is_dictionary(value):
	return isinstance(value, (dict, collections.OrderedDict))

def is_list(value):
	return isinstance(value, (list, tuple))

def is_collection(value):
	return is_dictionary(value) or is_list(value)

def is_serializable(value):
	return is_primitive(value) or is_collection(value)

# Load with pre-check to avoid capturing raised exceptions
# TODO: optimize-out pattern check for release environment
def load(string):
	if __debug__:
		pattern = r'^\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*$'
		if not re.match(pattern, string):
			return None
	try:
		return json.loads(string)
	except json.JSONDecodeError:
		return None

def stringify(obj, default=None, throw=True, overwrite=False, fpath=None, backup=False, precache=True):
	_default = default if default is not None else utils.serialize.NotSerializable
	if is_serializable(obj):
		if is_primitive(obj):
			return obj
		if fpath:
			try:
				log.info(utils.function.msg(f"Storing json to '{fpath}'"))
				dirpath = os.path.dirname(fpath)
				if dirpath and not os.path.exists(dirpath):
					log.info(utils.function.msg(f"Creating directory '{dirpath}'"))
					os.makedirs(dirpath)
				# Backup the current file content to avoid losing it in case of an error
				if precache:
					if os.path.exists(fpath):
						with open(fpath, 'r') as f:
							previous_content = f.read()
				if backup:
					bak_fpath = utils.file.backup(fpath, date_format="%Y-%m-%d_%H-%M-%S_stringify")
					if isinstance(bak_fpath, int):
						raise Exception(utils.function.msg(f"Error backing up file '{fpath}': {bak_fpath}"))
				with open(fpath, 'w') as f:
					json.dump(obj, f, indent='\t')
				log.debug(utils.function.msg(f"Stored successfully to '{fpath}'"))
				if backup:
					os.remove(bak_fpath)
				return True
			except Exception as e:
				# Restore the previous content
				if precache:
					with open(fpath, 'w') as f:
						f.write(previous_content)
				elif backup:
					# Copy the file
					restore_result = utils.file.restore(bak_fpath, fpath)
					if restore_result != 0:
						log.error(utils.function.msg(f"Error restoring file '{bak_fpath}' to '{fpath}': {restore_result}"))
				# Process the error
				if throw:
					raise Exception(utils.function.msg(f"Error writing to file '{fpath}': {e}"))
				else:
					return _default
		return json.dumps(obj, indent='\t')
	if throw:
		raise Exception(utils.function.msg(f"Not supported type '{type(obj)}' encountered"))
	else:
		return _default
