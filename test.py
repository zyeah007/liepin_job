#!/usr/bin/env python
# coding=utf-8
import time

for i in range(1000):
    print('进度:%.2f%%' % (i * 100 / 1000))
    time.sleep(5)