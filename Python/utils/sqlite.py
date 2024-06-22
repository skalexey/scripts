import json
import os
import shutil
import sqlite3
import threading
from datetime import datetime

import utils.lang
from utils.log.logger import *

log = Logger("sqlite_utils")

def backup_database(db_path, addition=None, datetime_format='%Y-%m-%d--%H-%M-%S'):
	"""
	Function to create a backup of the SQLite database file.
	"""
	addition_str = f".{addition}" if addition else ""
	backup_path = db_path + addition_str + "." + datetime.now().strftime(datetime_format) + '.backup'
	backup_path = os.path.abspath(backup_path)
	if os.path.exists(db_path):
		shutil.copy(db_path, backup_path)
		log.attention(f"Backup created: {backup_path}")
	else:
		raise Exception(f"Error: '{db_path}' does not exist.")

def condition_keys(input_string):
	# Split the string by the "AND" keyword
	parts = input_string.split("AND")
	
	# Extract the values from each part
	values = []
	for part in parts:
		if part:
			value = part.split(" ")[0]
			values.append(value)
	return values

def process_param(param):
	# Convert datetime objects to string
	return param.isoformat() if isinstance(param, datetime) else param

# Given kwargs will ovevwrite the values in where
def construct_where(where, params, **kwargs):
	_where, _params = where, params
	if isinstance(where, str):
		if kwargs: # Convert where to a dictionary to be able to update it with kwargs
			keys = condition_keys(where)
			_where = dict(zip(keys, params or []))
	elif isinstance(where, dict):
		if params is None:
			raise Exception("Params must not be provided if where is a dictionary")
	if kwargs:
		_where = _where.update(kwargs) if _where else kwargs
		_params = list(_where.values())
	if isinstance(_where, dict):
		_where = ' AND '.join(f"{key} = ?" for key in _where.keys())
	return _where, _params or []

def infer_sqlite_type(value):
	if isinstance(value, int):
		return 'INTEGER'
	elif isinstance(value, float):
		return 'REAL'
	elif isinstance(value, str):
		return 'TEXT'
	elif isinstance(value, bytes):
		return 'BLOB'
	elif isinstance(value, datetime):
		return 'TEXT'
	else:
		raise ValueError(f"Unsupported data type: {type(value)}")

def insert_query(table_name, data, **kwargs):
	"""
	Function to generate SQLite insertion query based on a JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- kwargs: Optional key-value pairs to be inserted into the table. Given kwargs will ovevwrite the same values in data.
	"""
	keyvalues = data.copy()
	keyvalues.update(kwargs)
	placeholders = ', '.join('?' for _ in keyvalues.keys())
	query = f'INSERT INTO {table_name} ({", ".join(keyvalues.keys())}) VALUES ({placeholders})'

	return query, list(keyvalues.values())

def insert(table_name, data, db_name=None, connection=None, cursor=None, **kwargs):
	# Connect to SQLite database
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)
	assert conn is not None, "Connection must be provided"
	# Insert JSON data into the table
	query, values = insert_query(table_name, data, **kwargs)
	cur.execute(query, values)

	# Commit changes and close connection
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

	return cur.lastrowid

def update_query(table_name, data, where=None, params=None):
	"""
	Function to generate SQLite update query based on a JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	"""
	_set = ', '.join(f"{key} = ?" for key in data.keys())
	_where, _params = construct_where(where, params)
	query = f"UPDATE {table_name} SET {_set} WHERE {_where}"
	_params = list(data.values()) + (_params or [])
	return query, _params

def update(table_name, data, where=None, params=None, db_name=None, connection=None, cursor=None):
	"""
	Function to update a row in the SQLite database based on a JSON object.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- data: JSON object (dictionary)
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	"""
	update_query, _params = update_query(table_name, data, where, params)
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)
	cur.execute(update_query, _params)
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

	return cur.rowcount

def create_if_not_exists_from_dict_query(table_name, struct, addition=None, primary_keys=None):
	"""
	Function to generate SQLite table creation query based on a JSON object.
	- struct: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- primary_keys: Set of primary key fields (optional)
	"""
	columns = []
	for key, value in struct.items():
		col_type = infer_sqlite_type(value)
		default_value = f" DEFAULT '{value}'" if isinstance(value, str) else f" DEFAULT {value}"
		columns.append(f'{key} {col_type}{default_value}')
	columns_str = ', '.join(columns)
	primary_key_str = ', PRIMARY KEY (' + ', '.join(primary_keys) + ')' if primary_keys else ''
	addition_str = f", {addition}" if addition else ''
	create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str}{primary_key_str}{addition_str})'
	return create_table_query

def create_or_alter_table_from_dict(db_name, table_name, struct, addition=None, primary_keys=None, composite_indexes=None, connection=None, cursor=None):
	"""
	Function to create or alter a SQLite table based on a given JSON object.
	- db_name: SQLite database file name used for backup
	- struct: JSON object (dictionary) with keys of column names and values of default values with types for the corresponding columns
	- table_name: Name of the SQLite table
	- primary_keys: Set of primary key fields (columns)
	- composite_indexes: Array of arrays where each inner array specifies fields for a composite index (optional)
	"""
	# Connect to SQLite database
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)

	# Get current table schema
	cur.execute(f"PRAGMA table_info({table_name})")
	existing_columns = cur.fetchall()
	existing_column_names, existing_primary_keys = [], []
	for col in existing_columns:
		existing_column_names.append(col[1])
		if col[5] == 1:
			existing_primary_keys.append(col[1])

	# Determine columns to add and drop
	keys = set(struct.keys())
	existing_column_set = set(existing_column_names)
	existing_primary_key_set = set(existing_primary_keys)

	columns_to_add = keys - existing_column_set
	columns_to_drop = existing_column_set - keys

	if existing_columns:
		if columns_to_add or columns_to_drop:
			# Backup the database first
			backup_database(db_name)
			# Add new columns with default values and inferred types
			for column_name in columns_to_add:
				default_value = struct[column_name]
				col_type = infer_sqlite_type(default_value)
				default_value_str = f" DEFAULT '{default_value}'" if isinstance(default_value, str) else f" DEFAULT {default_value}"
				log.attention(f"Altering table '{table_name}': Added column '{column_name}'")
				cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {col_type}{default_value_str}")

			# Drop columns
			for column_name in columns_to_drop:
				log.attention(f"Altering table '{table_name}': Dropped column '{column_name}'")
				cur.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

		if existing_primary_key_set != set(primary_keys or {}):
			# Handle primary keys
			# Construct a new table with primary keys if they are specified
			cur.execute(f"BEGIN TRANSACTION")
			cur.execute(f"CREATE TEMPORARY TABLE {table_name}_backup({', '.join(existing_column_names)})")
			cur.execute(f"INSERT INTO {table_name}_backup SELECT * FROM {table_name}")
			cur.execute(f"DROP TABLE {table_name}")
			create_table_query = create_if_not_exists_from_dict_query(table_name, struct, addition, primary_keys)
			cur.execute(create_table_query)
			cur.execute(f"INSERT INTO {table_name} SELECT * FROM {table_name}_backup")
			cur.execute(f"DROP TABLE {table_name}_backup")
			cur.execute(f"COMMIT")

	create_table_query = create_if_not_exists_from_dict_query(table_name, struct, addition, primary_keys)
	cur.execute(create_table_query)

	# Handle composite indexes
	if composite_indexes:
		index_prefix = f"idx_{table_name}_"
		composite_indexes_dict = {f"{index_prefix}{'_'.join(index_fields)}": index_fields for index_fields in composite_indexes}
		composite_indexes_set = set(composite_indexes_dict.keys())
		cur.execute(f"PRAGMA index_list({table_name})")
		indexes = cur.fetchall()
		existing_indexes_set = set(index[1] for index in indexes)
		indexes_to_add = composite_indexes_set - existing_indexes_set
		indexes_to_drop = existing_indexes_set - composite_indexes_set
		for index_name in indexes_to_add:
			index_fields = composite_indexes_dict[index_name]
			log.attention(f"create_or_alter_table_from_dict(): Creating index '{index_name}' on table '{table_name}'")
			cur.execute(f"CREATE UNIQUE INDEX {index_name} ON {table_name} ({', '.join(index_fields)})")
		for index_name in indexes_to_drop:
			log.attention(f"create_or_alter_table_from_dict(): Dropping index '{index_name}' from table '{table_name}'")
			cur.execute(f"DROP INDEX {index_name}")

	# Commit changes and close connection
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

def get_or_alloc_conn_cur(db_name, connection, cursor):
	assert connection is not None or cursor is not None or db_name is not None, "Either connection or cursor or db_name must be provided"
	conn = connection or (sqlite3.connect(db_name) if cursor is None else None)
	cur = cursor or conn.cursor()
	return conn, cur

def query_rows(table_name, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None, **kwargs):
	"""
	Function to query rows from the SQLite database.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	- statement: SQL statement (SELECT or DELETE)
	- kwargs (optional): Alternative key-value pairs for the WHERE clause. If provided, its values are in priority in the case of any intersection with where and corresponding params
	"""
	assert statement in ['SELECT', 'DELETE'], f"Invalid statement: {statement}"
	
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)

	what_addition = f" {', '.join(columns) if columns else '*'}" if statement == 'SELECT' else ''
	query = f"{statement}{what_addition} FROM {table_name}"
	
	_where, _params = construct_where(where, params, **kwargs)

	if statement == 'DELETE':
		if not _where:
			raise Exception("Either where or kwargs must be provided for DELETE statement")

	if _where:
		query += f" WHERE {_where}"

	cur.execute(query, _params)

	if statement == 'SELECT':
		result = cur.fetchall()
	else:
		result = cur.rowcount  # Number of rows affected

	if connection is None and cursor is None:
		conn.close()

	return result, cur, conn

def query_row(table_name, rowid, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None):
	"""
	Function to query a single row from the SQLite database.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- id: Primary key value
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	"""
	rows, cur, conn = query_rows(table_name, f"rowid = ?", [id], columns, db_name, connection, cursor)
	return rows[0] if rows else None

def query_data(table_name, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None, **kwargs):
	"""
	Function to query data in the form of a list of dictionaries from the SQLite database.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	- statement: SQL statement (SELECT or DELETE)
	- kwargs (optional): Alternative key-value pairs for the WHERE clause. If provided, its values are in priority in the case of any intersection with where and corresponding params
	"""
	rows, cur, conn = query_rows(table_name, where, params, columns, statement, db_name, connection, cursor, **kwargs)
	column_names = [desc[0] for desc in cur.description]
	data = [dict(zip(column_names, row)) for row in rows]
	return data, cur, conn

def query_dict(table_name, rowid=None, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None, **kwargs):
	"""
	Function to query a single entry from the SQLite database in the form of a dictionary.
	- table_name: Name of the SQLite table
	- rowid: rowid value
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- db_name: Optional SQLite database file name
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	"""
	assert rowid or where, "Either id or where must be provided"
	result = query_data(table_name, where or f"rowid = ?", [rowid] if rowid else params, columns, statement, db_name, connection, cursor)
	data = result[0]
	assert len(data) <= 1, "Multiple rows returned for a single row query"
	result = list(result)
	result[0] = data[0] if data else None
	return tuple(result)

class CursorWrapper:
	def __init__(self, cursor, lock, *args, **kwargs):
		self._cursor = cursor
		self._lock = lock
		self._lock.acquire()
		super().__init__(*args, **kwargs)

	def __del__(self):
		self._lock.release()
		utils.lang.clear_resources(self)

	def __getattr__(self, name):
		# Redirect attribute access to the underlying cursor
		return getattr(self._cursor, name)

class Connection:
	def __init__(self, db_fname, *args, **kwargs):
		self._lock = threading.RLock()
		self.db_fname = db_fname
		self.connection = sqlite3.connect(db_fname, check_same_thread=False)
		super().__init__(*args, **kwargs)
	
	def cursor(self):
		return CursorWrapper(self.connection.cursor(), self._lock)
	
	def backup(self, addition=None, datetime_format='%Y-%m-%d--%H-%M-%S'):
		backup_database(self.db_fname, addition, datetime_format)

	def query(self, table_name, where=None, params=None, statement="SELECT", **kwargs):
		return query_rows(table_name, where, params, statement, cursor=self.cursor(), **kwargs)[0]
	
	def delete(self, table_name, where=None, params=None, **kwargs):
		return query_rows(table_name, where, params, statement="DELETE", cursor=self.cursor(), **kwargs)[0]

	def query_row(self, table_name, id, columns=None, statement="SELECT"):
		return query_row(table_name, id, columns, statement, cursor=self.cursor())[0]

	def insert(self, data, table_name, **kwargs):
		return insert(data, table_name, self.db_fname, connection=self.connection, cursor=self.cursor(), **kwargs)

	def update(self, data, table_name, where=None, params=None):
		return update(table_name, where, params, cursor=self.cursor())[0]


class DictInterface(Connection):
	def __init__(self, db_fname):
		super().__init__(db_fname)

	def create_or_alter_table(self, table_name, data, addition=None, primary_keys=None, composite_indexes=None):
		create_or_alter_table_from_dict(self.db_fname, table_name, data, addition, primary_keys, composite_indexes, connection=self.connection, cursor=self.cursor())

	def query(self, table_name, where=None, params=None, columns=None, statement="SELECT", **kwargs):
		return query_data(table_name, where, params, columns, statement, cursor=self.cursor(), **kwargs)[0]

	def query_dict(self, table_name, rowid=None, where=None, params=None, statement="SELECT", **kwargs):
		return query_dict(table_name, rowid, where, params, statement=statement, cursor=self.cursor(), **kwargs)[0]
