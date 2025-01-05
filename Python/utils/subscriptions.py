"""
Global subscriptions for different purposes.
"""

from utils.log import log
from utils.subscription import Event

on_exit = Event()
on_exit.subscribe(lambda: log("Exiting..."), on_exit) # Called manually or by the main thread monitor
