# src/utils.py
import datetime

def timestamp():
    return datetime.datetime.utcnow().isoformat() + "Z"
