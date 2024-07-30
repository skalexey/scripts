import utils  # Lazy import
from utils.subscription import Subscription

on_exit = Subscription()
on_exit.subscribe(lambda: utils.log.log.log("Exiting..."), on_exit)
