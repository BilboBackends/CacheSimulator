import sys
import math


# <CACHE_SIZE> is the size of the simulated cache in bytes
# <ASSOC> is the associativity
# <REPLACEMENT> replacement policy: 0 means LRU, 1 means FIFO
# <WB> Write-back policy: 0 means write-through, 1 means write-back
# <TRACE_FILE> trace file name with full path
# Example:
# ./SIM 32768 8 1 1 /home/TRACES/MCF.t


#Arrays to hold information from the input file 
mode = []
index = []
tag = []


#making a class of cache for organizational purposes
class Cache:
    def __init__(self, line, data, dirty, tag):
        self.line = [[0 for x in range(assoc)] for y in range(numSets)]
        self.data = [[0 for x in range(assoc)] for y in range(numSets)]
        self.dirty = [[0 for x in range(assoc)] for y in range(numSets)]
        self.tag = [0 for x in range(numSets)]
        

#Assigning variables to whatever the user inputted when running the file
cacheSize = int(sys.argv[1])
assoc = int(sys.argv[2])
replacement = sys.argv[3]
wb = sys.argv[4]
traceFile = sys.argv[5]
blockSize = 64
numSets = int(cacheSize / (blockSize * assoc))
setNumber = int(math.log2(numSets))
blockOffset = int(math.log2(blockSize))
file = open(traceFile, mode = 'r')

with open(traceFile, "r") as traceFile:
    lines = traceFile.readlines()


#Opening the input file, converting to binary, and taking the index and tag to store in variables
for i in lines:
    split = i.split(" ")
    mode.append(split[0])
    index.append(int(bin(int(split[1], base=16))[-(setNumber + blockOffset):-blockOffset], 2))
    tag.append(int(bin(int(split[1], base=16))[:-(blockOffset+setNumber)], 2))

cache = Cache(numSets, tag, 0, 0)

j = 0
k = 0
hit = 0
miss = 0
write = 0
read = 0
flag = 0
old = 0
new = 1
dirty = 1

if replacement == "1": #FIFO
    for t, i in enumerate(index):
        for j in range(assoc):
            if cache.line[i][j] == tag[t]:
                hit+=1
                if mode[t] == "W":
                    cache.dirty[i][j] = dirty
                if wb == "0":
                    if mode[t] == 'W':
                        write+=1
                break
        else:
            read += 1
            miss+=1
            if wb == "0":    
                if mode[t] == 'W':
                    write+=1
            for j in range(assoc):
                if cache.data[i][j] == old:
                    if cache.line[i][j] != 0:
                        if wb == "1":
                            if cache.dirty[i][j] == dirty:
                                write+=1
                            if mode[t] == "R":
                                cache.dirty[i][j] = 0
                            if mode[t] == "W":
                                cache.dirty[i][j] = dirty
                    cache.line[i][j] = tag[t]
                    cache.data[i][j] = new
                    break
            else:
                for k in range(assoc):
                    cache.data[i][k] = old
                if wb == "1":
                    if cache.dirty[i][0] == dirty:
                        write+=1
                    if mode[t] == "R":
                        cache.dirty[i][0] = 0
                    if mode[t] == "W":
                        cache.dirty[0][j] = dirty
                cache.line[i][0] = tag[t]
                cache.data[i][0] = new


if replacement == "0": #LRU
    for t, i in enumerate(index):
        for j in range(assoc):
            if cache.line[i][j] == tag[t]:
                hit+=1
                value = cache.line[i].pop(j)
                cache.line[i].insert(0, value)
                if mode[t] == "R":
                    dirtyValue = cache.dirty[i].pop(j)
                    cache.dirty[i].insert(0, dirtyValue)
                if mode[t] == "W":
                    dirtyValue = cache.dirty[i].pop(j)
                    cache.dirty[i].insert(0, dirty)
                if wb == "0":
                    if mode[t] == "W":
                     write+=1
                break
        else:
            miss+=1
            read+=1
            if wb == "0":    
                if mode[t] == 'W':
                    write+=1
            value = cache.line[i].pop(-1)
            cache.line[i].insert(0, tag[t])
            dirtyValue = cache.dirty[i].pop(-1)
            if dirtyValue == 1:
                if wb == "1":
                    write+=1
            if mode[t] == "R":
                cache.dirty[i].insert(0, 0)
            if mode[t] == "W":
                cache.dirty[i].insert(0, 1)



                        
    
print(f'Miss Ratio: {(miss/(hit+miss))}')
print(f'Writes: {write}')
print(f'Reads: {read}')