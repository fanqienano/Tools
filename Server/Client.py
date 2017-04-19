#!/usr/bin/python
#coding=UTF-8

# import time

# if __name__ == '__main__':
# 	import socket
# 	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	sock.connect(('localhost', 8001))
# 	import time
# 	time.sleep(2)
# 	for i in range(1000):
# 		sock.send(str(i))
# 		time.sleep(1)
# 	# print sock.recv(1024)
# 	sock.close()

import socket
import json
import time
import random
from threading import Thread
# from decimal import Decimal

from DataUtils import Protocol

words = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

# Message = 'head:aaa:0001/0010:3:{'aaa': 1}:end'

class Sender(Thread):
	"""docstring for Sender"""
	def __init__(self, host, port, dataObj, dataType):
		super(Sender, self).__init__()
		self.amount = 512
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = host
		self.port = port
		self.dataObj = dataObj
		self.dataType = dataType

	def getPId(self):
		return ''.join(random.sample(words, 5)) + '_' + str(int(time.time() * 1000))

	def makeMessage(self, obj, dataType):
		messageList = list()
		data = json.dumps(object2dict(obj))
		size = len(data)
		sNum = (size / self.amount) + 1
		for i in xrange(0, sNum):
			s = i * self.amount
			e = (i + 1) * self.amount
			p = Protocol(pId = self.getPId(), sId = i + 1, sNum = sNum, size = size, data = data[s:e], dataType = dataType)
			messageList.append(str(p))
		return messageList

	def run(self):
		messageList = self.makeMessage(self.dataObj, self.dataType)
		self.socket.connect((self.host, self.port))
		for msg in messageList:
			self.socket.send
		self.socket.close()

def object2dict(obj):
	#convert object to a dict
	d = {}
	d['__class__'] = obj.__class__.__name__
	d['__module__'] = obj.__module__
	d.update(obj.__dict__)
	return d

def list2dict(objList):
	#convert object list to a dict
	ol = []
	for o in objList:
		ol.append(object2dict(o))
	return ol

def dict2object(d):
	#convert dict to object
	if'__class__' in d:
		class_name = d.pop('__class__')
		module_name = d.pop('__module__')
		module = __import__(module_name)
		class_ = getattr(module, class_name)
		# class_ = getattr(module, class_name)
		args = dict((key.encode('utf-8'), value) for key, value in d.items())  #get args
		inst = class_(**args)  #create new instance
	else:
		inst = d
	return inst
