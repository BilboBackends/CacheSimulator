
import sys
import math


# <CACHE_SIZE> is the size of the simulated cache in bytes
# <ASSOC> is the associativity
# <REPLACEMENT> replacement policy: 0 means LRU, 1 means FIFO
# <WB> Write-back policy: 0 means write-through, 1 means write-back
# <TRACE_FILE> trace file name with full path
# Example:
# "args": ["16", "1024", "2", "8192", "4", "0", "0", "filepath/gcc_trace.txt" ]


#Arrays to hold information from the input file 
mode = []
l1_index = []
l1_tag = []
l2_index = []
l2_tag = []


#making a class of cache for organizational purposes
class Cache:
    def __init__(self, line, data, dirty, tag, assoc, numSets):
        self.line = [[0 for x in range(assoc)] for y in range(numSets)]
        self.data = [[0 for x in range(assoc)] for y in range(numSets)]
        self.dirty = [[0 for x in range(assoc)] for y in range(numSets)]
        self.tag = [0 for x in range(numSets)]

def print_cache_l1(self):
    print("===== L contents =====")
    for set_idx, (line_set, dirty_set) in enumerate(zip(self.line, self.dirty)):
        print(f"Set {set_idx: <4}:", end=" ")
        for line_val, dirty_val in zip(line_set, dirty_set):
            dirty_indicator = "D" if dirty_val else " "
            print(f"{hex(line_val)[2:]: <8}{dirty_indicator}", end=" ")
        print()

def print_cache_l2(self):
    print("===== L2 contents =====")
    for set_idx, (line_set, dirty_set) in enumerate(zip(self.line, self.dirty)):
        print(f"Set {set_idx: <4}:", end=" ")
        for line_val, dirty_val in zip(line_set, dirty_set):
            dirty_indicator = "D" if dirty_val else " "
            print(f"{hex(line_val)[2:]: <8}{dirty_indicator}", end=" ")
        print()

def reformat_l1_tag_to_l2(l1_tag_value, l1_setNumber, l2_setNumber):
    shift_bits = l1_setNumber - l2_setNumber
    if shift_bits > 0:
        return l1_tag_value << shift_bits
    else:
        return l1_tag_value >> abs(shift_bits)
     

#Assigning variables to whatever the user inputted when running the file
blockSize = int(sys.argv[1])
l1_cacheSize = int(sys.argv[2])
l1_assoc = int(sys.argv[3])
l2_cacheSize = int(sys.argv[4])
l2_assoc = int(sys.argv[5])
replacement = sys.argv[6]
inclusion = sys.argv[7]
wb = 1
traceFile = sys.argv[8]
l1_numSets = int(l1_cacheSize / (blockSize * l1_assoc))
l1_setNumber = int(math.log2(l1_numSets))
blockOffset = int(math.log2(blockSize))
if l2_cacheSize != 0:
    l2_numSets = int(l2_cacheSize / (blockSize * l2_assoc))
    l2_setNumber = int(math.log2(l2_numSets))
file = open(traceFile, mode = 'r')

with open(traceFile, "r") as traceFile:
    lines = traceFile.readlines()


#Opening the input file, converting to binary, and taking the index and tag to store in variables
for i in lines:
    split = i.split(" ")
    mode.append(split[0].upper())
    hex_value = split[1] if split[1].startswith("0x") else "0x" + split[1]
    l1_index.append(int(bin(int(hex_value, base=16))[-(l1_setNumber + blockOffset):-blockOffset], 2))
    l1_tag.append(int(bin(int(hex_value, base=16))[:-(blockOffset+l1_setNumber)], 2))
    if l2_cacheSize != 0:
        l2_index.append(int(bin(int(hex_value, base=16))[-(l2_setNumber + blockOffset):-blockOffset], 2))
        l2_tag.append(int(bin(int(hex_value, base=16))[:-(blockOffset+l2_setNumber)], 2))


cacheL1 = Cache(l1_numSets, l1_tag, 0, 0, l1_assoc, l1_numSets)
if l2_cacheSize != 0:
    cacheL2 = Cache(l2_numSets, l2_tag, 0, 0, l2_assoc, l2_numSets)

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
l1_read = 0
l1_read_misses = 0
l1_writes = 0
l1_write_misses = 0
l2_read = 0
l2_read_misses = 0
l2_writes = 0
l2_write_misses = 0
l2_hit = 0
l2_miss = 0

if replacement == "1": #FIFO
    for t, i in enumerate(l1_index):
        for j in range(l1_assoc):
            if cacheL1.line[i][j] == l1_tag[t]:
                hit+=1
                if mode[t] == "R":
                    l1_read+=1
                if mode[t] == "W":
                    l1_writes+=1
                    cacheL1.dirty[i][j] = dirty
                if wb == "0":
                    if mode[t] == 'W':
                        write+=1
                break
        else:
            miss+=1
            # if wb == "0":    
            #     if mode[t] == 'W':
            #         write+=1
            for j in range(l1_assoc):
                if cacheL1.data[i][j] == old:
                    if cacheL1.line[i][j] != 0:
                        if wb == "1":
                            if cacheL1.dirty[i][j] == dirty:
                                write+=1
                            if mode[t] == "R":
                                l1_read+=1
                                l1_read_misses+=1
                                cacheL1.dirty[i][j] = 0
                            if mode[t] == "W":
                                l1_write_misses+=1
                                l1_writes+=1
                                cacheL1.dirty[i][j] = dirty
                    cacheL1.line[i][j] = l1_tag[t]
                    cacheL1.data[i][j] = new
                    break
            else:
                for k in range(l1_assoc):
                    cacheL1.data[i][k] = old
                if wb == "1":
                    if cacheL1.dirty[i][0] == dirty:
                        #l1_writes+=1
                        write+=1
                    if mode[t] == "R":
                        l1_read+=1
                        l1_read_misses+=1
                        cacheL1.dirty[i][0] = 0
                    if mode[t] == "W":
                        l1_write_misses+=1
                        l1_writes+=1
                        cacheL1.dirty[0][j] = dirty
                cacheL1.line[i][0] = l1_tag[t]
                cacheL1.data[i][0] = new

if replacement == "0":  # LRU
    for t, (i, l2_num) in enumerate(zip(l1_index, l2_index if l2_index else [None] * len(l1_index))):
        for j in range(l1_assoc):
            if cacheL1.line[i][j] == l1_tag[t]:
                hit += 1
                value = cacheL1.line[i].pop(j)
                cacheL1.line[i].insert(0, value)
                dirty_value = cacheL1.dirty[i].pop(j)
                cacheL1.dirty[i].insert(0, dirty_value)

                if mode[t] == "R":
                    l1_read += 1
                elif mode[t] == "W":
                    l1_writes += 1
                    cacheL1.dirty[i][0] = dirty

                if wb == "0" and mode[t] == "W":
                    write += 1
                break
        else:
            #l1_read+=1
            miss += 1
            if mode[t] == "R":
                l1_read_misses += 1
            elif mode[t] == "W":
                l1_write_misses += 1

            l1_evicted_value = cacheL1.line[i].pop(-1)
            l1_evicted_dirty = cacheL1.dirty[i].pop(-1)
            cacheL1.line[i].insert(0, l1_tag[t])
            cacheL1.dirty[i].insert(0, dirty if mode[t] == "W" else 0)

            # Simulate L2 cache access
            if l2_cacheSize != 0:
                l2_found = False
                for k in range(l2_assoc):
                    if cacheL2.line[l2_num][k] == l2_tag[t]:
                        l2_hit += 1
                        l1_writes+=1
                        l2_found = True

                        # Move the cache line to the beginning of the list
                        value = cacheL2.line[l2_num].pop(k)
                        cacheL2.line[l2_num].insert(0, value)
                        dirty_value = cacheL2.dirty[l2_num].pop(k)
                        cacheL2.dirty[l2_num].insert(0, dirty_value)
                        

                        if mode[t] == "R":
                            l2_read += 1
                        elif mode[t] == "W":
                            l2_writes += 1
                            cacheL2.dirty[l2_num][0] = dirty
                        break

                if not l2_found:
                    l2_miss += 1
                    #l2_read_misses += 1
                    if mode[t] == "R":
                        l2_read_misses += 1
                        l2_read += 0
                    elif mode[t] == "W":
                        l2_write_misses += 1
                        l2_writes += 0
                        #cacheL2.dirty[l2_num][0] = dirty
                    for k in range(l2_assoc):
                        if cacheL2.line[l2_num][k] == 0:
                            l2_evicted_value = cacheL2.line[l2_num].pop(-1)
                            l2_evicted_dirty = cacheL2.dirty[l2_num].pop(-1)
                            cacheL2.line[l2_num].insert(0, l2_tag[t])
                            cacheL2.dirty[l2_num].insert(0, dirty if mode[t] == "W" else 0)
                            break

                    if l2_evicted_dirty and wb == "1":
                        write += 1

                # Write back L1 evicted block to L2 cache if it's dirty
                if l1_evicted_dirty == 1:
                    l1_evicted_value = reformat_l1_tag_to_l2(l1_evicted_value, l1_setNumber, l2_setNumber)
                    for k in range(l2_assoc):
                        if cacheL2.line[l2_num][k] == l1_evicted_value:
                            cacheL2.dirty[l2_num][k] = 1
                            break
                    else:
                        # Evict the least recently used block from L2 cache
                        l2_evicted_value_l2 = cacheL2.line[l2_num].pop(-1)
                        l2_evicted_dirty_l2 = cacheL2.dirty[l2_num].pop(-1)

                        # Insert the evicted block from L1 cache into L2 cache
                        cacheL2.line[l2_num].insert(0, l1_evicted_value)
                        cacheL2.dirty[l2_num].insert(0, l1_evicted_dirty)

                        # Write back the evicted block from L2 cache to the main memory if it's dirty
                        if l2_evicted_dirty_l2 and wb == "1":
                            write += 1



if replacement == "2":  # Optimal
    for t, i in enumerate(l1_index):
        for j in range(l1_assoc):
            if cacheL1.line[i][j] == l1_tag[t]:
                hit += 1
                if mode[t] == "R":
                    l1_read += 1
                if mode[t] == "W":
                    l1_writes += 1
                    cacheL1.dirty[i][j] = dirty
                if wb == "0":
                    if mode[t] == "W":
                        write += 1
                break
        else:
            miss+=1
            #write += 1
            # Cache miss
            max_future_access = -1
            farthest_block = -1

            for j in range(l1_assoc):
                found = False
                for future_t, (future_tag, future_index) in enumerate(zip(l1_tag[t + 1:], l1_index[t + 1:])):
                    if future_tag == cacheL1.line[i][j] and future_index == i:
                        found = True
                        if future_t > max_future_access:
                            max_future_access = future_t
                            farthest_block = j
                        break

                if not found:
                    farthest_block = j
                    break

            # Evict the farthest_block and update the cache accordingly
            if cacheL1.dirty[i][farthest_block] == 1:
                write+=1
            if mode[t] == "R":
                l1_read_misses += 1
                l1_read += 1
                cacheL1.dirty[i][farthest_block] = 0
            if mode[t] == "W":
                l1_write_misses += 1
                l1_writes += 1
                cacheL1.dirty[i][farthest_block] = 1

            cacheL1.line[i][farthest_block] = l1_tag[t]



                        
l1_hex_cache = [[hex(num) for num in sublist] for sublist in cacheL1.line]
l1_hex_cache = [[hex(num) for num in sublist] for sublist in cacheL2.line]

print_cache_l1(cacheL1)
if l2_cacheSize != 0:
    print_cache_l2(cacheL2)

print(f'l1_Reads: {l1_read}')
# print(f'Reads: {read}')
# print(f'Miss: {miss}')
print(f'l1_Reads Misses: {l1_read_misses}')
print(f'L1 Writes: {l1_writes}')
print(f'L1 Write Misses: {l1_write_misses}')
print(f'Miss Ratio: {(miss/(hit+miss))}')
print(f'Write Backs: {write}')
print(f'total memory traffic: {l1_read_misses + l1_write_misses + write}')
print(f'l2_Reads: {l2_read}')
print(f'l2_Reads Misses: {l2_read_misses}')
print(f'L2 Writes: {l2_writes}')
print(f'L2 Write Misses: {l2_write_misses}')
print(f'L2 Miss Ratio: {(l2_miss/(l2_hit+l2_miss))}')
print(f'Write Backs: {write}')
print(f'total memory traffic: {l2_read_misses + l2_write_misses + write}')
