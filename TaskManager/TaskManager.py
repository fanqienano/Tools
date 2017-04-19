#!/usr/bin/python
#coding=UTF-8

from collections import OrderedDict
from threading import RLock
from multiprocessing import Lock
import time
import random

tLock = RLock()

pLock = Lock()

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

def threadLock(func):
	def _Lock(*args, **kwargs):
		tLock.acquire()
		try:
			ret = func(*args, **kwargs)
		except Exception, e:
			ret = None
			tLock.release()
			raise e
		tLock.release()
		return ret
	return _Lock

def processLock(func):
	def _Lock(*args, **kwargs):
		pLock.acquire()
		try:
			ret = func(*args, **kwargs)
		except Exception, e:
			ret = None
			pLock.release()
			raise e
		pLock.release()
		return ret
	return _Lock

class TaskManager(object):

	def __init__(self, num = 5):
		self._waitQueue = OrderedDict()
		self._workQueue = {}
		self._num = num
		self._cancel = False
		self._isRun = False
		self._isFinish = False

	def setNum(self, num):
		'''
		设置同时任务数
		num: 同时任务数
		'''
		self._num = num

	def _startRecv(self):
		pass

	def __finishRecv__(self):
		pass

	def _finish(self, name):
		try:
			del self._workQueue[name]
		except KeyError:
			pass
		if self._isRun:
			self._startTask()

	def start(self):
		'''
		开始服务，可无任务状态开始
		'''
		pass

	def close(self):
		'''
		关闭服务
		'''
		self._isFinish = True

	def resume(self):
		'''
		恢复服务
		'''
		pass

	def pause(self):
		'''
		暂停任务
		'''
		self.__isRun = False

	def wait(self, name = None):
		'''
		阻塞等待服务结束
		name: 目标任务id
		'''
		if name is None:
			while len(self._workQueue) > 0:
				for t in self._workQueue.values():
					t.join(t.timeout)
					self._finish(t.name)
					break
		else:
			while True:
				try:
					t = self._workQueue[name]
					t.join(t.timeout)
					self._finish(t.name)
					break
				except KeyError:
					if name in self._waitQueue.keys() + self._workQueue.keys():
						continue
					else:
						break

	def terminate(self, name = None):
		'''
		终止任务
		name: 目标任务id
		'''
		pass

	def dismiss(self, name = None):
		'''
		取消所有未执行的任务
		name: 目标任务id
		'''
		if name is None:
			self._waitQueue.clear()
			return True
		else:
			try:
				del self._waitQueue[name]
				return True
			except KeyError:
				return False
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
		pass

	def _startTask(self):
		while len(self._workQueue) < self._num and len(self._waitQueue) > 0:
			name, task = self._waitQueue.popitem(0)
			self._workQueue[name] = task
			task.start()

	def getStatus(self, name):
		'''
		获取任务状态
		0: 未执行
		1: 正在执行
		2: 不在服务中
		'''
		if name in self._waitQueue.keys():
			return 0
		if name in self._workQueue.keys():
			return 1
		return 2

	def getName(self):
		return ''.join(random.sample(words, 5)) + '_' + str(time.time())