#!/usr/bin/python
#coding=UTF-8

import time
import random
from collections import OrderedDict

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class TaskManager(object):
	def __init__(self, *args, **kwargs):
		self.waitQueue = OrderedDict()
		self.cancel = False
		self.num = 5
		if 'num' in kwargs:
			self.num = kwargs['num']
		self.workQueue = {}
		self.isRun = False

	def callback(self, t):
		try:
			del self.workQueue[t.name]
		except KeyError:
			pass
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
				self.callback(t)
		else:
			while True:
				try:
					t = self.workQueue[name]
					t.join(t.timeout)
					self.callback(t)
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
		kwargs['callback'] = kwargs.get('callback', self.callback)
		if name is None:
			name = ''.join(random.sample(words, 5)) + '_' + str(time.time())
		self.waitQueue[name] = (func, args, kwargs)
		if self.isRun:
			self.startTask()
		return name

	def startTask(self):
		pass

	# def startTask(self):
	# 	while len(self.workQueue) <= self.num and len(self.waitQueue) > 0:
	# 		item = self.waitQueue.popitem(0)
	# 		daemonic = item[1][2].get('daemonic', False)
	# 		t = TaskThread(item[1][0], *item[1][1], **item[1][2])
	# 		self.workQueue[t.name] = t
	# 		t.name = item[0]
	# 		t.setDaemon(daemonic)
	# 		t.start()