#coding=utf-8
#
# Author: Bruce Zhu
#

import time
import sys

class ProgressBar:
    def __init__(self, count = 0, total = 0, width = 50):
        self.count = count
        self.total = total
        self.width = width

    def move(self):
        self.count += 1

    def log(self, s):
        sys.stdout.write(' ' * (self.width + 9) + '\r')
        sys.stdout.flush()
        progress = int(self.width * self.count / self.total)
        sys.stdout.write('{0:3}/{1:3}: '.format(self.count, self.total))
        sys.stdout.write('#' * progress + '-' * (self.width - progress) + '\r')
        if progress == self.width:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def sleep(self, t):
        self.total = t
        for i in range(t):
            try:
                self.move()
                self.log(str(i + 1))
                time.sleep(1)
            except:
                print("Progress bar error!")
        self.total = 0

if __name__=="__main__":
    progressBar = ProgressBar()
    progressBar.sleep(10)
    print(1)