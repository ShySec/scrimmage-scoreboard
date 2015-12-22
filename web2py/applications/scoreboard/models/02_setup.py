request.now = request.utcnow
from gluon.storage import Storage
from datetime import datetime, timedelta

import gluon.custom_import
gluon.custom_import.track_changes(True)

# Assign application logger to a global var
import logging
logger = logging.getLogger()
log_name = 'applications/scoreboard/private/scoreboard.log'
log_format = "%(asctime)s %(process)05d:%(levelname)5s %(funcName)s():%(lineno)d %(message)s"
logging.basicConfig(level=logging.DEBUG,filename=log_name,format=log_format)
if len(logger.handlers) < 2:
	import logging.handlers
	handler = logging.handlers.TimedRotatingFileHandler(log_name,'d')
	handler.setFormatter(logging.Formatter(log_format))
	handler.setLevel(logging.DEBUG)
	logger.addHandler(handler)

def requireSSL():
	if request.is_https: return
	redirect(URL(scheme='https'))

def stripSSL():
	if not request.is_https: return
	redirect(URL(scheme='http'))
