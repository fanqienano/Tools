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

for i in range(30):
	pm.addTask(test, args = (i,))

pm.start()
pm.close()
pm.wait()
print 111

# # print dir(pm)

# def test(args = ()):
# 	print args

# test((11,22))
# test()