#!/usr/bin/python
#coding=UTF-8

import socket
from threading import Thread
import re
import json
import time

from DataUtils import pProtocol
from DataUtils import pProtocolHead
from DataUtils import Protocol
from DataUtils import analysis
from DataUtils import HeadSize
from DataUtils import makeHead
from DataUtils import encryption
from DataUtils import decryption

class Listener(Thread):
	def __init__(self, connection, address, callback, handleDict):
		super(Listener, self).__init__()
		self.connection = connection
		self.address = address
		self.bufferSize = 4096
		self.callback = callback
		self.handleDict = handleDict

	def run(self):
		pass

	def runPart(self):
		content = ''
		pId = None
		size = 0
		bufferSize = HeadSize
		retP = None
		ret = ''
		handle = None
		while True:
			buf = self.connection.recv(bufferSize)
			if len(buf) > 0:
				if pId is None and size == 0:
					buf = decryption(buf)
					m = pProtocolHead.match(buf)
					if m is not None:
						pId = m.group(1)
						size = int(m.group(2))
						path = m.group(3).strip()
						bufferSize = self.bufferSize
						if path in self.handleDict:
							handle = self.handleDict[path]
						else:
							raise AssertionError
				else:
					content = content + buf
					if len(content) == size:
						content = decryption(content)
						retP, ret = analysis(content)
						if ret == 'ok' and retP is not None and retP.pId == pId:
							break
						else:
							content = ''
							pId = None
							size = 0
							bufferSize = HeadSize
							retP = None
							ret = ''
		if ret == 'ok' and retP is not None and handle is not None:
			result = handle(retP.data)
			result = str(self.makeResult(retP.pId, result))
			result = encryption(result)
			head = makeHead(retP.pId, result, 'return')
			message = encryption(head) + result
			self.connection.send(message)
			self.callback(self, retP)
			return 'ok'

	def makeResult(self, pId, result, dataType = 'text'):
		size = len(result)
		p = Protocol(pId = pId, sId = 1, sNum = 1, size = size, data = result, dataType = dataType)
		return str(p)

class LongListener(Listener):

	def __init__(self, *args, **kwargs):
		super(LongListener, self).__init__(*args, **kwargs)
		self.timeLeft = 60
		self.finished = False
		self.timer = Thread(target = self.countdown)
		self.timer.start()

	def countdown(self):
		while not self.finished:
			self.timeLeft = self.timeLeft - 1
			if self.timeLeft <= 0:
				self.close()
			time.sleep(1)

	def close(self):
		print 'close connection'
		self.finished = True

	def run(self):
		while not self.finished:
			ret = self.runPart()
			if ret is not None:
				self.timeLeft = 60
		self.connection.close()

class ShortListener(Listener):

	def run(self):
		self.runPart()
		self.connection.close()

class Server(object):
	def __init__(self, host = 'localhost', port = 8000, socketType = 'short', **kwargs):
		self.socketType = socketType
		self.num = kwargs.get('num', 100)
		self.timeout = kwargs.get('timeout', 60)
		self.bufferSize = kwargs.get('bufferSize', 1024)
		self._close = False
		self.addressDict = dict()
		self._handleDict = dict()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((host, port))
		print host, port
		self.socket.listen(self.num)

	def setHandle(self, handleDict):
		self._handleDict = handleDict

	def close(self):
		self._close = True

	def setTimeout(self, timeout = 10):
		self.timeout = timeout

	def setNum(self, num = 10):
		self.num = num

	def closeServer(self, address):
		if address in self.addressDict:
			del self.addressDict[address]

	def callback(self, obj, prot):
		if prot.dataType == 'json':
			f = open('%s.txt'%prot.pId, 'w')
			f.write(json.dumps(json.loads(prot.data), indent = 4))
			f.close()

	def run(self):
		while not self._close:
			connection, address = self.socket.accept()
			connection.settimeout(self.timeout)
			if self.socketType == 'short':
				_class = ShortListener
			else:
				_class = LongListener
			print address
			_class(connection = connection, address = address, callback = self.callback, handleDict = self._handleDict).start()


			# self.listen(connection)

			# try:
			# 	buf = connection.recv(self.buffer)
			# 	print buf
			# 	if buf == '1':
			# 		connection.send('welcome to server!')
			# 	else:
			# 		connection.send('please go out!')
			# except socket.timeout:
			# 	print 'time out'
			# except:
			# 	print 
		# connection.close()


# import socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind(('localhost', 8001))
# sock.listen(5)
# while True:
#     connection,address = sock.accept()
#     try:
#         connection.settimeout(5)
#         buf = connection.recv(1024)
#         if buf == '1':
#             connection.send('welcome to server!')
#         else:
#             connection.send('please go out!')
#     except socket.timeout:
#         print 'time out'
#     connection.close()