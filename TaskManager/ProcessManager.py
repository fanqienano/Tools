#!/usr/bin/python
#coding=UTF-8

from multiprocessing import Process
from multiprocessing import Pipe
import threading
import time
import random
from collections import OrderedDict
import signal

from TaskManager import TaskManager
from TaskManager import processLock

from TaskException import TimeoutException
from TaskException import CloseException
from TaskException import TaskException

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

class TaskProcess(Process):
	'''
	任务进程
	func: 任务方法
	childConn: 子链接
	timeout: join的超时时间，默认None不限时
	exc_timeout: func执行的超时时间
	callback: 回调方法，传入func执行返回值
	args: func的参数
	'''
	def __init__(self, func, childConn, timeout = None, exc_timeout = 0, callback = None, args = ()):
		super(TaskProcess, self).__init__()
		self.func = func
		self.args = args
		self.timeout = timeout
		self.excTimeout = exc_timeout
		self.childConn = childConn
		self.callback = callback

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
		if self.callback:
			self.callback(ret)
		if error is not None:
			raise error

	def exceptionHandler(self, signum, frame):
		raise TimeoutException

	def finish(self, msg):
		self.childConn.send(msg)

class ProcessManager(TaskManager):
	'''
	进程管理
	num: 同时任务数，默认为5
	'''
	def __init__(self, num = 5):
		self._parentConn, self._childConn = Pipe()
		self._waitQueue = OrderedDict()
		self._cancel = False
		self._num = num
		self._workQueue = {}
		self._isRun = False
		self._isFinish = False

	def _startRecv(self):
		t = threading.Thread(target = self.__finishRecv__, args = ())
		t.start()

	def __finishRecv__(self):
		while not self._isFinish or len(self._waitQueue) + len(self._workQueue) > 0:
			msg = self._parentConn.recv()
			self._finish(msg['name'])

	def start(self):
		'''
		开始服务，可无任务状态开始
		'''
		self._isRun = True
		self._isFinish = False
		self._startRecv()
		self._startTask()

	def resume(self):
		'''
		恢复服务
		'''
		self._isRun = True
		self._startTask()

	def terminate(self, name = None):
		'''
		终止任务
		name: 目标任务id
		'''
		if name is None:
			self._waitQueue.clear()
			for t in self._workQueue.values():
				try:
					t.terminate()
					t.join()
				except:
					pass
			return True
		else:
			try:
				self._workQueue[name].terminate()
				self._workQueue[name].join()
				self._finish(name)
				return True
			except:
				return False

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
			raise CloseException()
		if name is None:
			name = ''.join(random.sample(words, 5)) + '_' + str(time.time())
		t = TaskProcess(func = func, childConn = self._childConn, timeout = timeout, exc_timeout = exc_timeout, callback = callback, args = args)
		t.name = name
		t.daemon = daemonic
		self._waitQueue[name] = t
		if self._isRun:
			self._startTask()
		return t

	@processLock
	def _startTask(self):
		super(ProcessManager, self)._startTask()
