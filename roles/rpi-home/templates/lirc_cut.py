#coding: UTF-8
import sys

argvs = sys.argv
argc = len(argvs)

if (argc < 2):
    print 'Error: argument not enough'
    quit()

f = open(argvs[1])
line = f.readline()
line = f.readline()

count = 0

while line:
    print line.split(' ')[1].strip(),
    line = f.readline()
    count += 1
    if (count > 20):
        count = 0
        print

f.close
