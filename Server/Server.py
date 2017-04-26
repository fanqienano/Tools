#!/usr/bin/python
#coding=UTF-8

import socket
from threading import Thread
import re
import json
import time

from DataUtils import pProtocol
from DataUtils import Protocol

class Listener(Thread):
	def __init__(self, connection, address, analysis, callback, bufferSize = 1024):
		super(Listener, self).__init__()
		self.connection = connection
		self.address = address
		self.bufferSize = bufferSize
		self.dataDict = dict()
		self.callback = callback
		self.analysis = analysis

	def run(self):
		pass

class LongListener(Listener):
	# def __init__(self, *args, **kwargs):
	# 	super(LongListener, self).__init__(*args, **kwargs)

	def close(self):
		self.connection.close()

	def run(self):
		while True:
			content = ''
			while True:
				buf = self.connection.recv(self.bufferSize)
				if buf == '':
					break
				content = content + buf
			if content != '':
				p, ret = self.analysis(content)
				self.connection.send(ret)
				if p is not None:
					self.callback(self, p)
			else:
				time.sleep(1)
		# self.connection.close()

class ShortListener(Listener):
	# def __init__(self, *args, **kwargs):
	# 	super(LongListener, self).__init__(*args, **kwargs)

	def run(self):
		content = ''
		while True:
			buf = self.connection.recv(self.bufferSize)
			if buf == '':
				break
			content = content + buf
		p, ret = self.analysis(content)
		self.connection.send(ret)
		if p is not None:
			self.callback(self, p)
		self.connection.close()

class Server(object):
	def __init__(self, host = 'localhost', port = 8000, socketType = 'long', **kwargs):
		self.socketType = socketType
		self.num = kwargs.get('num', 100)
		self.timeout = kwargs.get('timeout', 60)
		self.bufferSize = kwargs.get('bufferSize', 1024)
		self._close = False
		self.addressDict = dict()
		self.dataDict = dict()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((host, port))
		print host, port
		self.socket.listen(self.num)

	def analysis(self, data):
		m = pProtocol.search(data)
		if m is not None:
			pId = m.group(1)
			dataType = m.group(2)
			sId = int(m.group(3))
			sNum = int(m.group(4))
			size = int(m.group(5))
			data = m.group(6)
			p = Protocol(pId = pId, sId = sId, sNum = sNum, size = size, data = data, dataType = dataType)
			if pId not in self.dataDict:
				self.dataDict[pId] = dict()
			self.dataDict[pId][sId] = p
			if len(self.dataDict[pId]) == sNum:
				retP = Protocol(pId = pId, sId = sId, sNum = sNum, size = size, dataType = dataType)
				items = sorted(self.dataDict[pId].items(), key = lambda x: x[0])
				for i, d in items:
					retP.data = retP.data + d.data
				if size == len(retP.data):
					try:
						del self.dataDict[pId]
					except:
						pass
					return retP, 'ok'
			return None, 'ok'
		else:
			return None, 'error'

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
			if self.socketType == 'long':
				_class = LongListener
			else:
				_class = ShortListener
			_class(connection = connection, address = address, analysis = self.analysis, callback = self.callback).start()


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

if __name__ == '__main__':
	Server().run()


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