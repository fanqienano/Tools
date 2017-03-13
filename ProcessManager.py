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
		self.isFork = kwargs.get('fork', False)
		self.timeout = kwargs.get('timeout', 0)

	def start(self):
		if self.isFork:
			super(TaskProcess, self).start()

	def run(self):
		signal.signal(signal.SIGALRM, self.exceptionHandler)
		signal.alarm(self.timeout)
		self.func(*self.args)
		self.callback(self)

	def exceptionHandler(self, signum, frame):
		raise AssertionError

	def callback(self, t):
		pass

class ProcessManager(TaskManager):
	def __init__(self, *args, **kwargs):
		self.waitQueue = OrderedDict()
		self.cancel = False
		self.num = 5
		if 'num' in kwargs:
			self.num = kwargs['num']
		self.threadQueue = {}
		self.isRun = False
