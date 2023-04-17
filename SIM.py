
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


def find_block_to_evict_l2(cache, set_idx):
    for j in range(l2_assoc):
        if cache.line[set_idx][j] == 0:
            return j
    return l2_assoc - 1

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
l1_write_back = 0
l2_read = 0
l2_read_misses = 0
l2_writes = 0
l2_write_misses = 0
l2_write_back = 0
l2_hit = 0
l2_miss = 0
l2_hit_count = 0
l2_miss_count = 0

if replacement == "1": #FIFO
    for t, i in enumerate(l1_index):
        for j in range(l1_assoc):
            if cacheL1.line[i][j] == l1_tag[t]:
                hit += 1
                if mode[t] == "R":
                    l1_read += 1
                if mode[t] == "W":
                    l1_writes += 1
                    cacheL1.dirty[i][j] = dirty
                break
        else:
            miss += 1
            for j in range(l1_assoc):
                if cacheL1.data[i][j] == old:
                    if cacheL1.line[i][j] == 0:
                        if mode[t] == "R":
                            l1_read += 1
                            l1_read_misses += 1
                            cacheL1.dirty[i][j] = 0
                        if mode[t] == "W":
                            l1_write_misses += 1
                            l1_writes += 1
                            cacheL1.dirty[i][j] = dirty
                        cacheL1.line[i][j] = l1_tag[t]
                        cacheL1.data[i][j] = new
                        break
            else:
                for k in range(l1_assoc):
                    cacheL1.data[i][k] = old
                if cacheL1.dirty[i][0] == dirty:
                    write += 1
                if mode[t] == "R":
                    l1_read += 1
                    l1_read_misses += 1
                    cacheL1.dirty[i][0] = 0
                if mode[t] == "W":
                    l1_write_misses += 1
                    l1_writes += 1
                    cacheL1.dirty[i][0] = dirty
                cacheL1.line[i][0] = l1_tag[t]
                cacheL1.data[i][0] = new

            if l2_cacheSize != 0:
                l2_miss = True
                for j in range(l2_assoc):
                    if cacheL2.line[l2_index[t]][j] == l2_tag[t]:
                        l2_hit = True
                        l2_miss = False
                        break

                if l2_miss:
                    for j in range(l2_assoc):
                        if cacheL2.data[l2_index[t]][j] == old:
                            if cacheL2.line[l2_index[t]][j] == 0:
                                cacheL2.line[l2_index[t]][j] = l2_tag[t]
                                cacheL2.data[l2_index[t]][j] = new
                                break
                    else:
                        for k in range(l2_assoc):
                            cacheL2.data[l2_index[t]][k] = old
                        cacheL2.line[l2_index[t]][0] = l2_tag[t]
                        cacheL2.data[l2_index[t]][0] = new

# if replacement == "1": #FIFO
#     for t, i in enumerate(l1_index):  #t is the counter of the for loop, i is the actual index for l1
#         for j in range(l1_assoc):     # j is just a number from 0 to the length of the row size in l1 cache and the associativity is the row size
#             if cacheL1.line[i][j] == l1_tag[t]: #go to the index of the cache and loop through the entire line to see if the tag is already there
#                 hit+=1      # if it is then you hit the data
#                 if mode[t] == "R": #if the mode is just read we dont need to do anything in fifo, it stays where it is
#                     l1_read+=1
#                 if mode[t] == "W":     #if the mode is write then we are going to mark the block as dirty
#                     l1_writes+=1
#                     cacheL1.dirty[i][j] = dirty
#                 break
#         else:
#             miss+=1 #if the data isnt in the indexed row we must have missed
#             for j in range(l1_assoc):   #loop through the line again
#                 if cacheL1.data[i][j] == old: #i is still the index of the block, so were still manipulating the same line, and if the flag is old go down if statement
#                     if cacheL1.line[i][j] == 0: # Check if the block is empty, if it is we can just fill it, only happens in the beginning
#                         if mode[t] == "R":
#                             l1_read+=1
#                             l1_read_misses+=1
#                         if mode[t] == "W":
#                             l1_write_misses+=1
#                             l1_writes+=1
#                             cacheL1.dirty[i][j] = dirty
#                     else:
#                         if cacheL1.dirty[i][j] == dirty: # If the cache line thats getting evicted is dirty we write to the memory
#                             write+=1
#                         if mode[t] == "R": # if we're just reading it then we make sure the bit set to not dirty since its new
#                             l1_read+=1
#                             l1_read_misses+=1
#                             cacheL1.dirty[i][j] = 0
#                         if mode[t] == "W":
#                             l1_write_misses+=1
#                             l1_writes+=1
#                             cacheL1.dirty[i][j] = dirty
#                     cacheL1.line[i][j] = l1_tag[t]
#                     cacheL1.data[i][j] = new
#                     break
#             else:
#                 for k in range(l1_assoc):
#                     cacheL1.data[i][k] = old
#                 if cacheL1.dirty[i][0] == dirty:
#                     write+=1
#                 if mode[t] == "R":
#                     l1_read+=1
#                     l1_read_misses+=1
#                     cacheL1.dirty[i][0] = 0
#                 if mode[t] == "W":
#                     l1_write_misses+=1
#                     l1_writes+=1
#                     cacheL1.dirty[i][0] = dirty
#                 cacheL1.line[i][0] = l1_tag[t]
#                 cacheL1.data[i][0] = new


# This works right now!!!!!!
# if replacement == "0":  # LRU
#     for t, (i, l2_num) in enumerate(zip(l1_index, l2_index if l2_index else [None] * len(l1_index))): #looping through both the l1 and l2 index, but ignore l2 index if no l2 cache
#         for j in range(l1_assoc): #Looping through the amount of blocks in a single line (assocciativity)
#             if cacheL1.line[i][j] == l1_tag[t]: #If we find the tag already in the line were just moving it to the front
#                 hit += 1
#                 value = cacheL1.line[i].pop(j) #pop off that value we found
#                 cacheL1.line[i].insert(0, value) #insert it back to the front since its now least recently used
#                 dirty_value = cacheL1.dirty[i].pop(j) #pop off the dirty/not dirty bit from the same location
#                 cacheL1.dirty[i].insert(0, dirty_value) #insert it to the front to match the cache line location

#                 if mode[t] == "R": #if its read we dont need to do anything
#                     l1_read += 1
#                 elif mode[t] == "W": #if its write we mark the cache block as dirty that we just moved to the front
#                     l1_writes += 1
#                     cacheL1.dirty[i][0] = dirty
#                 break #we can break out of the loop since it was found
#         else: #if block wasnt found
#             #l1_read+=1
#             miss += 1
#             if mode[t] == "R":
#                 l1_read += 1
#                 l1_read_misses += 1
#             elif mode[t] == "W":
#                 l1_write_misses += 1
#                 l1_writes += 1

#             l1_evicted_value = cacheL1.line[i].pop(-1) #pop off the oldest block which is at the end of the cache line
#             l1_evicted_dirty = cacheL1.dirty[i].pop(-1) #same with the dirty value
#             if l1_evicted_dirty == dirty:
#                 l1_write_back+=1
#             cacheL1.line[i].insert(0, l1_tag[t]) #insert the new tag we just read to the front of the block
#             cacheL1.dirty[i].insert(0, dirty if mode[t] == "W" else 0) #insert the dirty bit to the front of the block, if its write it must be dirty




if replacement == "0":  # LRU
    for t, (i, l2_num) in enumerate(zip(l1_index, l2_index if l2_index else [None] * len(l1_index))):
        l1_hit = False
        for j in range(l1_assoc):
            if cacheL1.line[i][j] == l1_tag[t]:
                l1_hit = True
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
                break

        if not l1_hit:
            miss += 1
            if mode[t] == "R":
                l1_read += 1
                l1_read_misses += 1
            elif mode[t] == "W":
                l1_write_misses += 1
                l1_writes += 1

            l1_evicted_value = cacheL1.line[i].pop(-1)
            l1_evicted_dirty = cacheL1.dirty[i].pop(-1)
            if l1_evicted_dirty == dirty:
                l1_write_back += 1
            cacheL1.line[i].insert(0, l1_tag[t])
            cacheL1.dirty[i].insert(0, dirty if mode[t] == "W" else 0)

            # If L2 cache exists, check for a hit there
            if l2_cacheSize != 0:
                l2_hit = False
                for j in range(l2_assoc):
                    if cacheL2.line[l2_num][j] == l2_tag[t]:
                        l2_hit = True
                        l2_hit_count += 1
                        value = cacheL2.line[l2_num].pop(j)
                        cacheL2.line[l2_num].insert(0, value)
                        dirty_value = cacheL2.dirty[l2_num].pop(j)
                        cacheL2.dirty[l2_num].insert(0, dirty_value)

                        if mode[t] == "R":
                            l2_read += 1
                        elif mode[t] == "W":
                            l2_writes += 1
                            cacheL2.dirty[l2_num][0] = dirty
                        break

                if not l2_hit:
                    l2_miss_count += 1
                    if mode[t] == "R":
                        l2_read += 1
                        l2_read_misses += 1
                    elif mode[t] == "W":
                        l2_writes += 1
                    

                    l2_evicted_value = cacheL2.line[l2_num].pop(-1)
                    l2_evicted_dirty = cacheL2.dirty[l2_num].pop(-1)
                    if l2_evicted_dirty == dirty:
                        l2_write_back += 1
                    cacheL2.line[l2_num].insert(0, l2_tag[t])
                    cacheL2.dirty[l2_num].insert(0, dirty if mode[t] == "W" else 0)

                    

                    # If the evicted block from L1 cache is in the L2 cache, update the L2 cache
                    l2_evicted_l1_tag = reformat_l1_tag_to_l2(l1_evicted_value, l1_setNumber, l2_setNumber)
                    l2_evicted_block_idx = find_block_to_evict_l2(cacheL2, l2_num)
                    cacheL2.line[l2_num][l2_evicted_block_idx] = l2_evicted_l1_tag
                    cacheL2.dirty[l2_num][l2_evicted_block_idx] = l1_evicted_dirty

                    evicted_l1_block_present = False

                    for j in range(l2_assoc):
                        if cacheL2.line[l2_num][j] == l2_evicted_l1_tag:
                            evicted_l1_block_present = True
                            cacheL2.line[l2_num].pop(j)
                            cacheL2.line[l2_num].insert(0, l2_evicted_l1_tag)

                            # Also update the dirty status
                            dirty_status = cacheL2.dirty[l2_num][j]
                            cacheL2.dirty[l2_num].pop(j)
                            cacheL2.dirty[l2_num].insert(0, dirty_status)
                            break

                    if not evicted_l1_block_present:
                        l2_write_misses += 1
















            # # Simulate L2 cache access
            # if l2_cacheSize != 0:
            #     l2_found = False
            #     for k in range(l2_assoc):
            #         if cacheL2.line[l2_num][k] == l2_tag[t]:
            #             l2_hit += 1
            #             l1_writes+=1
            #             l2_found = True

            #             # Move the cache line to the beginning of the list
            #             value = cacheL2.line[l2_num].pop(k)
            #             cacheL2.line[l2_num].insert(0, value)
            #             dirty_value = cacheL2.dirty[l2_num].pop(k)
            #             cacheL2.dirty[l2_num].insert(0, dirty_value)
                        

            #             if mode[t] == "R":
            #                 l2_read += 1
            #             elif mode[t] == "W":
            #                 l2_writes += 1
            #                 cacheL2.dirty[l2_num][0] = dirty
            #             break

            #     if not l2_found:
            #         l2_miss += 1
            #         #l2_read_misses += 1
            #         if mode[t] == "R":
            #             l2_read_misses += 1
            #             l2_read += 0
            #         elif mode[t] == "W":
            #             l2_write_misses += 1
            #             l2_writes += 0
            #             #cacheL2.dirty[l2_num][0] = dirty
            #         for k in range(l2_assoc):
            #             if cacheL2.line[l2_num][k] == 0:
            #                 l2_evicted_value = cacheL2.line[l2_num].pop(-1)
            #                 l2_evicted_dirty = cacheL2.dirty[l2_num].pop(-1)
            #                 cacheL2.line[l2_num].insert(0, l2_tag[t])
            #                 cacheL2.dirty[l2_num].insert(0, dirty if mode[t] == "W" else 0)
            #                 break

            #         if l2_evicted_dirty and wb == "1":
            #             write += 1

            #     # Write back L1 evicted block to L2 cache if it's dirty
            #     if l1_evicted_dirty == 1:
            #         l1_evicted_value = reformat_l1_tag_to_l2(l1_evicted_value, l1_setNumber, l2_setNumber)
            #         for k in range(l2_assoc):
            #             if cacheL2.line[l2_num][k] == l1_evicted_value:
            #                 cacheL2.dirty[l2_num][k] = 1
            #                 break
            #         else:
            #             # Evict the least recently used block from L2 cache
            #             l2_evicted_value_l2 = cacheL2.line[l2_num].pop(-1)
            #             l2_evicted_dirty_l2 = cacheL2.dirty[l2_num].pop(-1)

            #             # Insert the evicted block from L1 cache into L2 cache
            #             cacheL2.line[l2_num].insert(0, l1_evicted_value)
            #             cacheL2.dirty[l2_num].insert(0, l1_evicted_dirty)

            #             # Write back the evicted block from L2 cache to the main memory if it's dirty
            #             if l2_evicted_dirty_l2 and wb == "1":
            #                 write += 1



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
if l2_cacheSize!=0:
    l1_hex_cache = [[hex(num) for num in sublist] for sublist in cacheL2.line]

print_cache_l1(cacheL1)
if l2_cacheSize != 0:
    print_cache_l2(cacheL2)

print(f'a. number of L1 reads:        {l1_read}')
print(f'b. number of L1 read misses:  {l1_read_misses}')
print(f'c. number of L1 writes:       {l1_writes}')
print(f'd. number of L1 write misses: {l1_write_misses}')
print(f'e. L1 miss rate:              {miss/(hit+miss):.6f}')
print(f'f. number of L1 writebacks:   {l1_write_back}')
print(f'g. number of L2 reads:        {l2_hit_count + l2_miss_count}')
print(f'h. number of L2 read misses:  {l2_read_misses}')
print(f'i. number of L2 writes:       {l2_writes}')
print(f'j. number of L2 write misses: {l2_write_misses}')
print(f'k. L2 miss rate:              {(l2_miss_count / (l2_hit_count + l2_miss_count)) if l2_cacheSize != 0 else 0:.6f}')
print(f'l. number of L2 writebacks:   {l2_write_back}')
print(f'm. total memory traffic:      {l1_read_misses + l1_write_misses + l1_write_back if l2_cacheSize == 0 else l2_read_misses + l2_write_misses + l2_write_back}')
