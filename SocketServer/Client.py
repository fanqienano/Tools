#!/usr/bin/python
#coding=UTF-8

import socket
import json
import time
import random
from threading import Thread
import codecs
socket.setdefaulttimeout(30)

from DataUtils import Protocol
from DataUtils import pProtocolHead
from DataUtils import analysis
from DataUtils import HeadSize
from DataUtils import makeHead
from DataUtils import encryption
from DataUtils import decryption

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
		# self.amount = kwargs.get('amount', 512)
		self.host = host
		self.port = port
		self.headBufferSize = HeadSize
		self.bufferSize = 1024

	def getPId(self):
		return ''.join(random.sample(words, 5)) + '_' + str(int(time.time() * 1000))

	def makeMessage(self, data, dataType):
		pId = self.getPId()
		size = len(data)
		p = Protocol(pId = pId, sId = 1, sNum = 1, size = size, data = data, dataType = dataType)
		msg = str(p)
		return pId, msg

	# def makeMessageList(self, data, dataType):
	# 	pId = self.getPId()
	# 	messageList = list()
	# 	size = len(data)
	# 	if self.amount > 0:
	# 		sNum = (size / self.amount) + 1
	# 	else:
	# 		sNum = 1
	# 	for i in xrange(0, sNum):
	# 		s = i * self.amount
	# 		if self.amount > 0:
	# 			e = (i + 1) * self.amount
	# 		else:
	# 			e = size
	# 		p = Protocol(pId = pId, sId = i + 1, sNum = sNum, size = size, data = data[s:e], dataType = dataType)
	# 		messageList.append(str(p))
	# 	return pId, messageList

	def send(self, path, data, dataType):
		result = ''
		retP = None
		bufferSize = self.headBufferSize
		size = 0
		pId, msg = self.makeMessage(data, dataType)
		msg = encryption(msg)
		head = makeHead(pId, msg, path)
		message = encryption(head) + msg
		self.socket.send(message)
		try:
			while True:
				ret = self.socket.recv(bufferSize)
				if len(ret) > 0:
					if len(result) == 0 and size == 0:
						ret = decryption(ret)
						m = pProtocolHead.match(ret)
						if m is not None:
							if pId == m.group(1):
								size = int(m.group(2))
								bufferSize = self.bufferSize
					else:
						result = result + ret
						if len(result) == size:
							result = decryption(result)
							retP, msg = analysis(result)
							if retP is not None and retP.pId == pId and msg == 'ok':
								break
							else:
								result = ''
								retP = None
								bufferSize = self.headBufferSize
								size = 0
		except:
			pass
		return retP.data

	def close(self):
		pass

class LongSender(Sender):

	def __init__(self, *args, **kwargs):
		super(LongSender, self).__init__(*args, **kwargs)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))

	def close(self):
		self.socket.close()

class ShortSender(Sender):

	def __init__(self, *args, **kwargs):
		super(ShortSender, self).__init__(*args, **kwargs)
		self.amount = 0

	def send(self, *args, **kwargs):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		result = super(ShortSender, self).send(*args, **kwargs)
		self.socket.close()
		return result
