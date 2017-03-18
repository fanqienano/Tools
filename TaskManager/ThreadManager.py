#!/usr/bin/python
#coding=UTF-8

from threading import Thread
from threading import Timer
from threading import RLock
import time
import random
from collections import OrderedDict
import ctypes

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class TimeoutException(Exception):
	pass

class TaskThread(Thread):
	def __init__(self, func, finish, *args, **kwargs):
		super(TaskThread, self).__init__()
		self.func = func
		self.args = args
		self.callback = kwargs.get('callback', self.callback)
		self.finish = finish
		self.excTimeout = kwargs.get('exc_timeout', None)
		self.timeout = kwargs.get('timeout', None)

	def run(self):
		error = None
		ret = None
		if self.excTimeout is not None:
			timeoutThread = Timer(self.excTimeout, self.exceptionHandler, (self.ident,))
			timeoutThread.start()
		try:
			ret = self.func(*self.args)
		except Exception, error:
			pass
		self.finish(self.name)
		self.callback(ret)
		if error is not None:
			raise error

	def callback(self, *args, **kwargs):
		pass

	def exceptionHandler(self, tid):
		self.finish(self.name)
		ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(TimeoutException))

class ThreadManager(object):

	def __init__(self, *args, **kwargs):
		self.waitQueue = OrderedDict()
		self.cancel = False
		self.num = 5
		if 'num' in kwargs:
			self.num = kwargs['num']
		self.workQueue = {}
		self.isRun = False
		self.lock = RLock()

	def finish(self, name):
		try:
			del self.workQueue[name]
		except KeyError:
			pass
		print name
		if self.isRun:
			self.startTask()

	def start(self):
		'''
		Start all tasks.
		'''
		self.isRun = True
		self.startTask()

	def hold(self):
		'''
		No new tasks are pending.
		'''
		self.isRun = False

	def wait(self, **kwargs):
		'''
		Waiting for all tasks.
		name: Waiting for the name of the task.
		'''
		name = kwargs.get('name', None)
		if name is None:
			while len(self.workQueue) > 0:
				t = self.workQueue.values()[0]
				t.join(t.timeout)
				self.finish(t.name)
		else:
			while True:
				try:
					t = self.workQueue[name]
					t.join(t.timeout)
					self.finish(t.name)
					break
				except KeyError:
					if name in self.waitQueue.keys() + self.workQueue.keys():
						continue
					else:
						break

	def dismiss(self, **kwargs):
		'''
		Dismiss all the not starting tasks.
		name: Dismiss for the name of the task.
		return Dismiss result.
		'''
		name = kwargs.get('name', None)
		if name is None:
			self.waitQueue.clear()
			return True
		else:
			try:
				del self.waitQueue[name]
				return True
			except KeyError:
				return False
			return False

	def addTask(self, func, args = (), **kwargs):
		'''
		add one task to queue.
		kwargs: callback; timeout; exc_timeout; daemonic;
		return task name.
		'''
		name = kwargs.get('name', None)
		# kwargs['finish'] = self.finish
		if name is None:
			name = ''.join(random.sample(words, 5)) + '_' + str(time.time())
		self.waitQueue[name] = (func, args, kwargs)
		if self.isRun:
			self.startTask()
		return name

	def startTask(self):
		self.lock.acquire()
		while len(self.workQueue) < self.num and len(self.waitQueue) > 0:
			item = self.waitQueue.popitem(0)
			daemonic = item[1][2].get('daemonic', False)
			t = TaskThread(item[1][0], self.finish, *item[1][1], **item[1][2])
			t.name = item[0]
			t.setDaemon(daemonic)
			self.workQueue[t.name] = t
			t.start()
		self.lock.release()