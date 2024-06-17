import json
import os
import shutil
import sqlite3
import threading

import utils.lang
from utils.log.logger import *

log = Logger("sqlite_utils")

def backup_database(db_fname, addition=None, datetime_format='%Y-%m-%d--%H-%M-%S'):
	"""
	Function to create a backup of the SQLite database file.
	"""
	addition_str = f".{name_addition}" if name_addition else ""
	name_with_date_and_time = db_fname + addition_str + "." + datetime.now().strftime(datetime_format) + '.backup'
	if os.path.exists(db_fname):
		shutil.copy(db_fname, backup_file)
		log.attention(f"Backup created: {backup_file}")
	else:
		log.error(f"Error: '{db_fname}' does not exist.")
		return False
	return True

def construct_where(where, params):
	if isinstance(where, str):
		return where, params
	if isinstance(where, dict):
		assert params is None, "Params must not be provided if where is a dictionary"
		_where = ' AND '.join(f"{key} = ?" for key in where.keys())
		_params = list(where.values())
		return _where, _params

def create_if_not_exists_from_dict_query(data, table_name, primary_keys=None):
	"""
	Function to generate SQLite table creation query based on a JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- primary_keys: Set of primary key fields (optional)
	"""
	columns = ', '.join(f'{key} TEXT' for key in data.keys())
	if primary_keys:
		primary_key_str = ', '.join(primary_keys)
		create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({primary_key_str}, {columns}, PRIMARY KEY ({primary_key_str}))'
	else:
		create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})'

	return create_table_query

def insert_query(data, table_name):
	"""
	Function to generate SQLite insertion query based on a JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	"""
	placeholders = ', '.join('?' for _ in data.keys())
	insert_query = f'INSERT INTO {table_name} ({", ".join(data.keys())}) VALUES ({placeholders})'

	return insert_query

def insert(data, table_name, db_name=None, connection=None, cursor=None):
	# Connect to SQLite database
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)
	assert conn is not None, "Connection must be provided"
	# Insert JSON data into the table
	insert_query = insert_query(data, table_name)
	cur.execute(insert_query, list(data.values()))

	# Commit changes and close connection
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

	return cur.lastrowid

def update_query(data, table_name, where=None, params=None):
	"""
	Function to generate SQLite update query based on a JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	"""
	_set = ', '.join(f"{key} = ?" for key in data.keys())
	_where, _params = construct_where(where, params)
	update_query = f"UPDATE {table_name} SET {_set} WHERE {_where}"
	_params = list(data.values()) + (_params or [])
	return update_query, _params

def update(db_name, table_name, data, where=None, params=None, connection=None, cursor=None):
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
	update_query, _params = update_query(data, table_name, where, params)
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)
	cur.execute(update_query, _params)
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

	return cur.rowcount

def create_or_alter_table_from_dict(data, table_name, primary_keys=None, composite_indexes=None, db_name=None, connection=None, cursor=None):
	"""
	Function to create or alter a SQLite table based on a given JSON object.
	- data: JSON object (dictionary)
	- table_name: Name of the SQLite table
	- db_name: SQLite database file name
	- primary_keys: Set of primary key fields (columns)
	- composite_indexes: Array of arrays where each inner array specifies fields for a composite index (optional)
	"""
	# Backup the database first
	backup_database(db_name)

	# Connect to SQLite database
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)

	# Get current table schema
	cur.execute(f"PRAGMA table_info({table_name})")
	existing_columns = cur.fetchall()
	existing_column_names = [col[1] for col in existing_columns]

	# Determine columns to add and drop
	keys = set(data.keys())
	existing_column_set = set(existing_column_names)

	columns_to_add = keys - existing_column_set
	columns_to_drop = existing_column_set - keys

	# Add new columns
	for column_name in columns_to_add:
		log.attention(f"Altering table '{table_name}': Added column '{column_name}'")
		cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT")

	# Drop columns
	for column_name in columns_to_drop:
		log.attention(f"Altering table '{table_name}': Dropped column '{column_name}'")
		cur.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

	# Handle primary keys
	if primary_keys:
		# Construct a new table with primary keys if they are specified
		create_table_query = create_if_not_exists_from_dict_query(data, table_name, primary_keys)
		cur.execute(f"BEGIN TRANSACTION")
		cur.execute(f"CREATE TEMPORARY TABLE {table_name}_backup({', '.join(existing_column_names)})")
		cur.execute(f"INSERT INTO {table_name}_backup SELECT * FROM {table_name}")
		cur.execute(f"DROP TABLE {table_name}")
		cur.execute(create_table_query)
		cur.execute(f"INSERT INTO {table_name} SELECT * FROM {table_name}_backup")
		cur.execute(f"DROP TABLE {table_name}_backup")
		cur.execute(f"COMMIT")

	# Handle composite indexes
	if composite_indexes:
		for index_fields in composite_indexes:
			index_name = '_'.join(index_fields)
			cur.execute(f"PRAGMA index_list({table_name})")
			indexes = cur.fetchall()
			index_exists = any(index[1] == f"idx_{index_name}" for index in indexes)
			if not index_exists:
				log.attention(f"create_or_alter_table_from_dict(): Creating index 'idx_{index_name}' on table '{table_name}' ({', '.join(index_fields)})")
				cur.execute(f"CREATE UNIQUE INDEX idx_{index_name} ON {table_name} ({', '.join(index_fields)})")

	# Commit changes and close connection
	conn.commit()
	if connection is None and cursor is None:
		conn.close()

def get_or_alloc_conn_cur(db_name, connection, cursor):
	assert connection is not None or cursor is not None or db_name is not None, "Either connection or cursor or db_name must be provided"
	conn = connection or (sqlite3.connect(db_name) if cursor is None else None)
	cur = cursor or conn.cursor()
	return conn, cur

def query_rows(table_name, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None):
	"""
	Function to query rows from the SQLite database.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	"""
	assert statement in ['SELECT', 'DELETE'], f"Invalid statement: {statement}"
	
	conn, cur = get_or_alloc_conn_cur(db_name, connection, cursor)

	query = f"{statement} {', '.join(columns) or '*'} FROM {table_name}"
	
	_where, _params = construct_where(where, params)

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

def query_data(table_name, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None):
	"""
	Function to query data in the form of a list of dictionaries from the SQLite database.
	- db_name: SQLite database file name
	- table_name: Name of the SQLite table
	- where: Optional SQL WHERE clause or a dictionary of column-value pairs
	- params: Optional parameters for the WHERE clause
	- connection: Optional SQLite connection object
	- cursor: Optional SQLite cursor object
	"""
	rows, cur, conn = query_rows(table_name, where, params, columns, statement, db_name, connection, cursor)
	column_names = [desc[0] for desc in cur.description]
	data = [dict(zip(column_names, row)) for row in rows]
	return data

def query_dict(table_name, rowid=None, where=None, params=None, columns=None, statement="SELECT", db_name=None, connection=None, cursor=None):
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
	data = query_data(table_name, where or f"rowid = ?", [rowid or params], columns, statement, db_name, connection, cursor)
	assert len(data) <= 1, "Multiple rows returned for a single row query"
	return data[0] if data else None

class CursorWrapper:
	def __init__(self, cursor, lock):
		self._cursor = cursor
		self._lock = lock
		self._lock.acquire()

	def __del__(self):
		self._lock.release()
		utils.lang.clear_resources(self)

	def __getattr__(self, name):
		# Redirect attribute access to the underlying cursor
		return getattr(self._cursor, name)

class Connection:
	def __init__(self, db_fname):
		self._lock = threading.RLock()
		self.db_fname = db_fname
		self.connection = sqlite3.connect(db_fname)
	
	def cursor(self):
		return CursorWrapper(self.connection.cursor(), self._lock)
	
	def backup(self, addition=None, datetime_format='%Y-%m-%d--%H-%M-%S'):
		backup_database(self.db_fname, addition, datetime_format)

	def query(self, table_name, where=None, params=None, statement="SELECT"):
		return query_rows(self.db_fname, table_name, where, params, statement, cursor=self.cursor())[0]
	
	def delete(self, table_name, where=None, params=None):
		return query_rows(self.db_fname, table_name, where, params, "DELETE", cursor=self.cursor())[0]

	def query_row(self, table_name, id, columns=None, statement="SELECT"):
		return query_row(self.db_fname, table_name, id, columns, statement, cursor=self.cursor())[0]

	def insert(self, data, table_name):
		return insert(data, table_name, self.db_fname, connection=self.connection, cursor=self.cursor())

	def update(self, data, table_name, where=None, params=None):
		return update(self.db_fname, table_name, where, params, cursor=self.cursor())[0]


class DictInterface(Connection):
	def __init__(self, db_fname):
		super().__init__(db_fname)

	def create_or_alter_table(self, data, table_name, primary_keys=None, composite_indexes=None):
		create_or_alter_table_from_dict(self.db_fname, data, table_name, primary_keys, composite_indexes, connection=self.connection, cursor=self.cursor())

	def query(self, table_name, where=None, params=None, statement="SELECT"):
		return query_data(self.db_fname, table_name, where, params, statement, cursor=self.cursor())[0]

	def query_dict(self, table_name, rowid=None, where=None, params=None, statement="SELECT"):
		return query_dict(self.db_fname, table_name, rowid, where, params, statement, cursor=self.cursor())[0]
