#!/usr/bin/python
#coding=UTF-8

import socket
import json
import time
import random
from threading import Thread
import codecs

from DataUtils import Protocol

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

def object2dict(obj):
	d = {}
	d['__class__'] = obj.__class__.__name__
	d['__module__'] = obj.__module__
	d.update(obj.__dict__)
	return d

def list2dict(objList):
	ol = []
	for o in objList:
		ol.append(object2dict(o))
	return ol

def dict2object(d):
	if'__class__' in d:
		class_name = d.pop('__class__')
		module_name = d.pop('__module__')
		module = __import__(module_name)
		class_ = getattr(module, class_name)
		args = dict((key.encode('utf-8'), value) for key, value in d.items())
		inst = class_(**args)
	else:
		inst = d
	return inst

class Sender(object):
	def __init__(self, host, port, **kwargs):
		# super(Sender, self).__init__()
		self.amount = kwargs.get('amount', 512)
		self.host = host
		self.port = port

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))

	# def setData(self, dataObj, dataType):
	# 	self.dataObj = dataObj
	# 	self.dataType = dataType

	def getPId(self):
		return ''.join(random.sample(words, 5)) + '_' + str(int(time.time() * 1000))

	def makeMessage(self, data, dataType):
		pId = self.getPId()
		messageList = list()
		size = len(data)
		if self.amount > 0:
			sNum = (size / self.amount) + 1
		else:
			sNum = 1
		for i in xrange(0, sNum):
			s = i * self.amount
			e = (i + 1) * self.amount
			p = Protocol(pId = pId, sId = i + 1, sNum = sNum, size = size, data = data[s:e], dataType = dataType)
			messageList.append(str(p))
		return pId, messageList

	def close(self):
		pass

class LongSender(Sender):

	def __init__(self, *args, **kwargs):
		super(LongSender, self).__init__(*args, **kwargs)
		self.amount = 0

	def close(self):
		self.socket.close()

	def send(self, dataObj, dataType):
		result = ''
		pId, messageList = self.makeMessage(dataObj, dataType)
		for msg in messageList:
			# while True:
			self.socket.send(msg)
			try:
				while True:
					ret = self.socket.recv(1024)
					if ret == '':
						break
					result = result + ret
			except:
				pass
		return result

class ShortSender(Sender):

	def __init__(self, *args, **kwargs):
		super(ShortSender, self).__init__(*args, **kwargs)
		self.amount = 0

	def send(self, dataObj, dataType):
		result = ''
		pId, messageList = self.makeMessage(dataObj, dataType)
		for msg in messageList:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.connect((self.host, self.port))
			self.socket.send(msg)
			try:
				while True:
					ret = self.socket.recv(1024)
					if ret == '':
						break
					result = result + ret
			except:
				pass
			self.socket.close()
		return result

# class Client(object):
# 	# def __init__(self, host = 'localhost', port = 8000, socketType = 'long', **kwargs):
# 	# 	self.socketType = socketType
# 	# 	self.num = kwargs.get('num', 100)
# 	# 	self.timeout = kwargs.get('timeout', 30)
# 	# 	socket.setdefaulttimeout(self.timeout)
# 	# 	if self.socketType == 'long':
# 	# 		self._class = LongSender
# 	# 	else:
# 	# 		self._class = ShortSender
# 	# 	self.sender = _class(host, port)

# 	def send(self, host, port, dataObj, dataType, socketType = 'long', block = True, **kwargs):
# 		self.num = kwargs.get('num', 100)
# 		socket.setdefaulttimeout(kwargs.get('timeout', 30))
# 		if socketType == 'long':
# 			_class = LongSender
# 		else:
# 			_class = ShortSender
# 		_class(host, port).setData(dataObj, dataType)
# 		sender.start()

# if __name__ == '__main__':
# 	data = open('/home/fanwu/Desktop/daily-2017-04-24_bilibili_item_10.163.5.169-172.19.0.191-20170414-daily_e7257936dc73a1fb3d7a1015ce201e49daily-2017-04-24.json', 'r').readlines()
# 	data = '[' + ','.join(data) + ']'
# 	for i in range(10):
# 		Sender('localhost', 8001, data, 'json').start()
# 		print i
	# for i in range(10):
		# t = Thread(target = Sender('localhost', 8001, data, 'json').start)
		# t.start()
