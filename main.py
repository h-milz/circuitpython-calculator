import math as m
import random 
import os 
import time

(sysname, nodename, release, version, machine) = os.uname()
print ("Adafruit CircuitPython {},\n{}".format(version, machine))

# run all benchmarks circa 10s to reduce the influence of the timing overhead. 

# Integer Benchmark
# calculate 1000! n times. 

n = 80
print ("Integer: elapsed time = ", end="")

start = time.monotonic()

for i in range (n):
    res = 1
    for j in range (2, 1001):
        res *= j
    # print (".", end="")


end = time.monotonic()
# print ("")
elapsed = end - start
print ("{:.2f} s".format(elapsed))


# Float Benchmark
# do some floating point math n times. 

x = m.sqrt(m.pi) # this is our "random" value
n = 100000
print ("Float:   elapsed time = ", end="")
start = time.monotonic()

for i in range (n):
    a = m.sin(x)
    b = m.cos(x)
    c = m.sqrt(x)
    # print (".", end="")


end = time.monotonic()
# print("")
elapsed = end - start
print ("{:.2f} s".format(elapsed))


# List Benchmark
# we create a list of 1000 pseudorandom values and have it copied and sorted n times 

table1 = []    # create empty list 
n = 1200   # number of loops
print ("List:    elapsed time = ", end="")

random.seed(12345) # constant seed so that random values are deterministic. 

tablen = 1000
for i in range (tablen):
    table1.append(random.randint(0, 1000000))

start = time.monotonic()

for j in range(n):
    table2 = table1[0:tablen-1]  # true copy
    table2.sort()
    # print (".", end="")

end = time.monotonic()
# print("")

elapsed = end - start
print ("{:.2f} s".format(elapsed))


