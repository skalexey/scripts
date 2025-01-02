"""
A small library that provides network transport-level abstractions (Connection, Server) and concrete implementations (TCP, UDP). Enables the creation of connection-agnostic systems that are not tied to a specific transport network protocol. Also includes an abstract PacketServer class.
"""

import importlib


def __getattr__(name):
	library = importlib.import_module(f"{__name__}.library")
	if name == '__wrapped__':
		return None
	return getattr(library, name)
