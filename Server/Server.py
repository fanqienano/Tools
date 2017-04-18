#!/usr/bin/python
#coding=UTF-8

import socket
from threading import Thread
import re
import json

# class protocol(object):
# 	"""docstring for ClassName"""
# 	def __init__(self, arg):
# 		super(ClassName, self).__init__()
# 		self.arg = arg

pProtocol = re.compile(r'^head:(\S+?):(\d+?):(.+?):end$')

class Protocol(object):
	def __init__(self, pId = '', size = 0, data = '', finish = False):
		self.pId = pId
		self.size = size
		self.data = data
		self.finish = finish

class Listener(Thread):
	def __init__(self, connection, address, bufferSize = 1024):
		super(Listener, self).__init__()
		self.connection = connection
		self.address = address
		self.bufferSize = bufferSize
		self.dataDict = dict()

	'''head:3:{'aaa': 1}:end'''
	def analysis(self, data):
		m = pProtocol.search(data)
		if m is not None:
			pId = m.group(1)
			size = int(m.group(2))
			data = m.group(3)
			p = Protocol(pId = pId, size = size, data = data)
			if pId not in self.dataDict:
				self.dataDict[pId] = p
			else:
				self.dataDict[pId] = Protocol(pId = pId, size = size, data = self.dataDict[pId].data + data)
				if size == len(self.dataDict[pId].data):
					self.dataDict[pId].finish = True
					ret = self.dataDict[pId]
					del self.dataDict[pId]
					ret.data = json.loads(ret.data)
					return ret
		return None

	def run(self):
		while True:
			buf = self.connection.recv(self.bufferSize)
			p = self.analysis(buf)
			if p is not None:
				print p.data
		self.connection.close()

class Server(object):
	def __init__(self, connectionType = 'long'):
		self.connectionType = connectionType
		self.num = 10
		self.timeout = 10
		self.bufferSize = 1024
		self.close = False
		self.addressDict = dict()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind(('localhost', 8001))
		self.socket.listen(self.num)

	def close(self):
		self.close = True

	def setTimeout(self, timeout = 10):
		self.timeout = timeout

	def setNum(self, num = 10):
		self.num = num

	def closeServer(self, address):
		if address in self.addressDict:
			del self.addressDict[address]

	def run(self):
		while not self.close:
			connection, address = self.socket.accept()
			connection.settimeout(self.timeout)
			if address not in self.addressDict:
				self.addressDict[address] = Listener(connection, address)
				self.addressDict[address].start()
			print self.addressDict
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