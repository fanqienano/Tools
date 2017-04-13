#!/usr/bin/python
#coding=UTF-8

from threading import Thread
from threading import Timer
from threading import RLock
import time
import random
from collections import OrderedDict
import ctypes

from TaskManager import TaskManager

from TaskException import TimeoutException
from TaskException import CloseException
from TaskException import TaskException

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class TaskThread(Thread):
	'''
	任务进程
	func: 任务方法
	childConn: 子链接
	timeout: join的超时时间，默认None不限时
	exc_timeout: func执行的超时时间
	callback: 回调方法，传入func执行返回值
	args: func的参数
	'''
	def __init__(self, func, finish, timeout = None, exc_timeout = 0, callback = None, args = ()):
		super(TaskThread, self).__init__()
		self.func = func
		self.args = args
		self.callback = callback
		self.finish = finish
		self.excTimeout = exc_timeout
		self.timeout = timeout

	def run(self):
		error = None
		ret = None
		if self.excTimeout > 0:
			timeoutThread = Timer(self.excTimeout, self.exceptionHandler, (self.ident,))
			timeoutThread.start()
		try:
			ret = self.func(*self.args)
		except Exception, error:
			pass
		self.finish(self.name)
		if self.callback:
			self.callback(ret)
		if error is not None:
			raise error

	def exceptionHandler(self, tid):
		self.finish(self.name)
		ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(TimeoutException))

class ThreadManager(TaskManager):
	'''
	进程管理
	num: 同时任务数，默认为5
	'''
	def __init__(self, num = 5):
		self._waitQueue = OrderedDict()
		self._cancel = False
		self._workQueue = {}
		self._isRun = False
		self._lock = RLock()
		self._num = num
		self._isFinish = False

	def start(self):
		'''
		开始服务，可无任务状态开始
		'''
		self._isRun = True
		self._isFinish = False
		self._startTask()

	def resume(self):
		'''
		恢复服务
		'''
		self.start()

	def addTask(self, func, name = None, timeout = None, exc_timeout = 0, callback = None, daemonic = False, args = ()):
		'''
		添加任务
		func: 任务方法
		name: 任务id，默认则随机生成
		timeout: join超时时间
		exc_timeout: 任务执行超时时间
		callback: 回调方法
		daemonic: 是否守护进程
		args: 任务方法所需参数
		'''
		if self._isFinish:
			raise CloseException('')
		if name is None:
			name = ''.join(random.sample(words, 5)) + '_' + str(time.time())
		self._waitQueue[name] = {'func': func, 'timeout': timeout, 'exc_timeout': exc_timeout, 'callback': callback, 'daemonic': daemonic, 'args': args}
		if self._isRun:
			self._startTask()
		return name

	def _startTask(self):
		# self._lock.acquire()
		while len(self._workQueue) < self._num and len(self._waitQueue) > 0:
			itemName, itemData = self._waitQueue.popitem(0)
			t = TaskThread(func = itemData['func'], finish = self._finish, timeout = itemData['timeout'], exc_timeout = itemData['exc_timeout'], callback = itemData['callback'], args = itemData['args'])
			t.name = itemName
			t.setDaemon(itemData['daemonic'])
			self._workQueue[t.name] = t
			t.start()
		# self._lock.release()
