"""
Global subscriptions for different purposes.
"""

from utils.log import log
from utils.subscription import Event

on_exit = Event()
def on_exit_handler():
	log("Exiting...")
on_exit.subscribe(on_exit_handler, on_exit) # Called manually or by the main thread monitor
