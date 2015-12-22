import gluon.scheduler
scheduler = gluon.scheduler.Scheduler(db, heartbeat=0.5)

def wrapped_task(taskname, *args, **kwargs):
	task = web2py[taskname]
	try:
		result = task(*args, **kwargs)
		if kwargs.get('autocommit',True): db.commit()
		return result
	except:
		logger.exception('failed')

def queue_wrapped_task(self, function, pargs=[], pvars={}, **kwargs):
	logger.debug('queueing %s %s %s %s',function,pargs,pvars,kwargs)
	pargs = [function.__name__]+list(pargs)
	logger.debug('queueing %s %s %s %s',function,pargs,pvars,kwargs)
	return self.raw_queue_task(wrapped_task,pargs,pvars,**kwargs)

scheduler.raw_queue_task = scheduler.queue_task
scheduler.queue_task = queue_wrapped_task.__get__(scheduler, gluon.scheduler.Scheduler)

# fix broken imports
import datetime as dt
gluon.scheduler.datetime = dt
