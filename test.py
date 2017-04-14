#!/usr/bin/python
#coding=UTF-8

import time

from TaskManager import ThreadManager

pm = ThreadManager()
print pm

def test(t):
	print t
	time.sleep(3)
	print 'over'

tasks = []
for i in range(30):
	t = pm.addTask(test, args = (i,))
	tasks.append(t)

pm.start()
pm.close()
time.sleep(10)
pm.pause()
print 222333
for i in tasks:
	print i.status, '@@@@@@@@@@@@@@'
pm.resume()
pm.wait()
print 111

# # print dir(pm)

# def test(args = ()):
# 	print args

# test((11,22))
# test()