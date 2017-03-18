#!/usr/bin/python
#coding=UTF-8

from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import Lock
import threading
import time
import random
from collections import OrderedDict
import signal

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class TaskProcess(Process):
	def __init__(self, func, childConn, *args, **kwargs):
		super(TaskProcess, self).__init__()
		self.func = func
		self.args = args
		self.timeout = kwargs.get('timeout', None)
		self.excTimeout = kwargs.get('exc_timeout', 0)
		self.childConn = childConn
		self.callback = kwargs.get('callback', self.callback)

	def run(self):
		error = None
		ret = None
		try:
			signal.signal(signal.SIGALRM, self.exceptionHandler)
			signal.alarm(self.excTimeout)
			ret = self.func(*self.args)
			signal.alarm(0)
		except Exception, error:
			pass
		self.finish({'name': self.name})
		self.callback(ret)
		if error is not None:
			raise error

	def exceptionHandler(self, signum, frame):
		raise AssertionError

	def callback(self, *args, **kwargs):
		pass

	def finish(self, msg):
		self.childConn.send(msg)

# class ProcessManager(TaskManager):

class ProcessManager(object):
	def __init__(self, *args, **kwargs):
		self.parentConn, self.childConn = Pipe()
		self.waitQueue = OrderedDict()
		self.cancel = False
		self.num = 5
		if 'num' in kwargs:
			self.num = kwargs['num']
		self.workQueue = {}
		self.isRun = False
		self.isFinish = False
		self.lock = Lock()

	def startRecv(self):
		t = threading.Thread(target = self.__finishRecv__, args = ())
		# t.setDaemon(False)
		t.start()

	def __finishRecv__(self):
		while not self.isFinish or len(self.waitQueue) + len(self.workQueue) > 0:
			msg = self.parentConn.recv()
			self.finish(msg['name'])

	def finish(self, name):
		try:
			del self.workQueue[name]
		except KeyError:
			pass
		if self.isRun:
			self.startTask()

	def start(self):
		'''
		Start all tasks.
		'''
		self.isRun = True
		self.startRecv()
		self.startTask()

	def close(self):
		self.isFinish = True

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

	def terminate(self, **kwargs):
		name = kwargs.get('name', None)
		if name is None:
			self.waitQueue.clear()
			for t in self.workQueue.values():
				try:
					t.terminate()
					t.join()
				except:
					pass
			return True
		else:
			try:
				self.workQueue[name].terminate()
				self.workQueue[name].join()
				self.finish(name)
				return True
			except:
				return False

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
			t = TaskProcess(item[1][0], self.childConn, *item[1][1], **item[1][2])
			t.name = item[0]
			t.daemon = daemonic
			self.workQueue[t.name] = t
			t.start()
			print len(self.waitQueue), len(self.workQueue)
		self.lock.release()