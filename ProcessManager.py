#!/usr/bin/python
#coding=UTF-8

from multiprocessing import Process
from multiprocessing import JoinableQueue
import time
import random
from collections import OrderedDict
import inspect
import ctypes
import signal

from TaskManager import TaskManager

class TaskProcess(Process):
	def __init__(self, func, *args, **kwargs):
		super(TaskProcess, self).__init__()
		self.func = func
		self.args = args
		self.callback = kwargs.get('callback', self.callback)
		self.timeout = kwargs.get('timeout', 0)

	def run(self):
		error = None
		try:
			signal.signal(signal.SIGALRM, self.exceptionHandler)
			signal.alarm(self.timeout)
			self.func(*self.args)
			signal.alarm(0)
		except Exception, error:
			pass
		self.callback(self)
		if error is not None:
			raise error

	def exceptionHandler(self, signum, frame):
		raise AssertionError

	def callback(self, t):
		pass

class ProcessManager(TaskManager):

	def startTask(self):
		while len(self.workQueue) < self.num and len(self.waitQueue) > 0:
			item = self.waitQueue.popitem(0)
			print len(self.waitQueue), len(self.workQueue), item
			daemonic = item[1][2].get('daemonic', False)
			t = TaskProcess(item[1][0], *item[1][1], **item[1][2])
			self.workQueue[t.name] = t
			t.name = item[0]
			t.daemon = daemonic
			t.start()