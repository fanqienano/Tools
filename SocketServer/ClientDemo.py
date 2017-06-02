#!/usr/bin/python
#coding=UTF-8

from Client import LongSender, ShortSender

if __name__ == '__main__':
	# client = LongSender('localhost', 8000)
	client = ShortSender('localhost', 8000)
	ret = client.send('test', '111222333', 'text')
	print ret
	ret = client.send('test', '444555666', 'text')
	print ret
