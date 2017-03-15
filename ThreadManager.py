#!/usr/bin/python
#coding=UTF-8

from multiprocessing import Process
from multiprocessing import JoinableQueue
from threading import Thread
from threading import Event
from threading import Timer
import time
import random
from collections import OrderedDict
import inspect
import ctypes
import signal

from TaskManager import TaskManager

class TimeoutException(Exception):
	pass

class TaskThread(Thread):
	def __init__(self, func, *args, **kwargs):
		super(TaskThread, self).__init__()
		self.func = func
		self.args = args
		self.callback = kwargs.get('callback', self.callback)
		self.excTimeout = kwargs.get('exc_timeout', None)
		self.timeout = kwargs.get('timeout', None)

	def run(self):
		error = None
		if self.excTimeout is not None:
			timeoutThread = Timer(self.excTimeout, self.exceptionHandler, (self.ident,))
			timeoutThread.start()
		try:
			self.func(*self.args)
		except Exception, error:
			pass
		self.callback(self)
		if error is not None:
			raise error

	def exceptionHandler(self, tid):
		self.callback(self)
		ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(TimeoutException))

	def callback(self, t):
		pass

class ThreadManager(TaskManager):

	def startTask(self):
		while len(self.workQueue) < self.num and len(self.waitQueue) > 0:
			item = self.waitQueue.popitem(0)
			daemonic = item[1][2].get('daemonic', False)
			t = TaskThread(item[1][0], *item[1][1], **item[1][2])
			t.name = item[0]
			self.workQueue[t.name] = t
			t.setDaemon(daemonic)
			t.start()