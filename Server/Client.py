#!/usr/bin/python
#coding=UTF-8

import time

if __name__ == '__main__':
	import socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(('localhost', 8001))
	import time
	time.sleep(2)
	for i in range(1000):
		sock.send(str(i))
		time.sleep(1)
	# print sock.recv(1024)
	sock.close()