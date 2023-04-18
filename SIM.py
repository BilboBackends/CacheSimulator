
import sys
import math


# <CACHE_SIZE> is the size of the simulated cache in bytes
# <ASSOC> is the associativity
# <REPLACEMENT> replacement policy: 0 means LRU, 1 means FIFO
# <WB> Write-back policy: 0 means write-through, 1 means write-back
# <TRACE_FILE> trace file name with full path
# Example:
#"args": ["16", "1024", "1", "8192", "4", "0", "0", "go_trace.txt" ]


#Arrays to hold information from the input file 
mode = []
l1_index = []
l1_tag = []
l2_index = []
l2_tag = []


#making a class of cache for organizational purposes
class Cache:
    def __init__(self, assoc, numSets):
        self.line = [[0 for x in range(assoc)] for y in range(numSets)]
        self.data = [[0 for x in range(assoc)] for y in range(numSets)]
        self.dirty = [[0 for x in range(assoc)] for y in range(numSets)]
        self.tag = [0 for x in range(numSets)]

def print_cache_l1(self):
    print("===== L1 contents =====")
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

def extract_fields(hex_value, set_number, block_offset):
    value = int(hex_value, 16)
    index_mask = (1 << set_number) - 1

    index = (value >> block_offset) & index_mask
    tag = value >> (block_offset + set_number)

    return index, tag

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


cacheL1 = Cache(l1_assoc, l1_numSets)
if l2_cacheSize != 0:
    cacheL2 = Cache(l2_assoc, l2_numSets)

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


if replacement == "1":  # FIFO
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
            l2_hit = False
            evict_index = None
            for j in range(l1_assoc):
                if cacheL1.data[i][j] == old:
                    if cacheL1.dirty[i][j] == dirty:
                        l1_write_back+=1
                    evict_index = j
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
            if evict_index is None:
                for k in range(l1_assoc):
                    cacheL1.data[i][k] = old
                if cacheL1.dirty[i][0] == dirty:
                    write += 1
                    l1_write_back+=1
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
                for j in range(l2_assoc):
                    if cacheL2.line[l2_index[t]][j] == l2_tag[t]:
                        l2_hit = True
                        break

                if not l2_hit:
                    evict_index = None
                    for j in range(l2_assoc):
                        if cacheL2.data[l2_index[t]][j] == old:
                            evict_index = j
                            cacheL2.line[l2_index[t]][j] = l2_tag[t]
                            cacheL2.data[l2_index[t]][j] = new
                            break
                    if evict_index is None:
                        for k in range(l2_assoc):
                            cacheL2.data[l2_index[t]][k] = old
                        cacheL2.line[l2_index[t]][0] = l2_tag[t]
                        cacheL2.data[l2_index[t]][0] = new


# if replacement == "1": #FIFO
#     for t, i in enumerate(l1_index):
#         for j in range(l1_assoc):
#             if cacheL1.line[i][j] == l1_tag[t]:
#                 hit += 1
#                 if mode[t] == "R":
#                     l1_read += 1
#                 if mode[t] == "W":
#                     l1_writes += 1
#                     cacheL1.dirty[i][j] = dirty
#                 break
#         else:
#             miss += 1
#             for j in range(l1_assoc):
#                 if cacheL1.data[i][j] == old:
#                     if cacheL1.line[i][j] == 0:
#                         if mode[t] == "R":
#                             l1_read += 1
#                             l1_read_misses += 1
#                             cacheL1.dirty[i][j] = 0
#                         if mode[t] == "W":
#                             l1_write_misses += 1
#                             l1_writes += 1
#                             cacheL1.dirty[i][j] = dirty
#                         cacheL1.line[i][j] = l1_tag[t]
#                         cacheL1.data[i][j] = new
#                         break
#             else:
#                 for k in range(l1_assoc):
#                     cacheL1.data[i][k] = old
#                 if cacheL1.dirty[i][0] == dirty:
#                     write += 1
#                 if mode[t] == "R":
#                     l1_read += 1
#                     l1_read_misses += 1
#                     cacheL1.dirty[i][0] = 0
#                 if mode[t] == "W":
#                     l1_write_misses += 1
#                     l1_writes += 1
#                     cacheL1.dirty[i][0] = dirty
#                 cacheL1.line[i][0] = l1_tag[t]
#                 cacheL1.data[i][0] = new

#             if l2_cacheSize != 0:
#                 l2_miss = True
#                 for j in range(l2_assoc):
#                     if cacheL2.line[l2_index[t]][j] == l2_tag[t]:
#                         l2_hit = True
#                         l2_miss = False
#                         break

#                 if l2_miss:
#                     for j in range(l2_assoc):
#                         if cacheL2.data[l2_index[t]][j] == old:
#                             if cacheL2.line[l2_index[t]][j] == 0:
#                                 cacheL2.line[l2_index[t]][j] = l2_tag[t]
#                                 cacheL2.data[l2_index[t]][j] = new
#                                 break
#                     else:
#                         for k in range(l2_assoc):
#                             cacheL2.data[l2_index[t]][k] = old
#                         cacheL2.line[l2_index[t]][0] = l2_tag[t]
#                         cacheL2.data[l2_index[t]][0] = new

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
    for t, (i, l2_num) in enumerate(zip(l1_index, l2_index if l2_index else [None] * len(l1_index))): #iterate through both l1 and l2 index, but ignore l2 if there is none
        l1_hit = False
        for j in range(l1_assoc): #looping throught the actual cache line
            if cacheL1.line[i][j] == l1_tag[t]: #if theres a hit
                l1_hit = True
                hit += 1
                value = cacheL1.line[i].pop(j) #pop off the block we just hit
                cacheL1.line[i].insert(0, value) #insert the block we just hit back to the front
                dirty_value = cacheL1.dirty[i].pop(j) #pop off the dirty/clean bit we just hit
                cacheL1.dirty[i].insert(0, dirty_value) #insert it to the front

                if mode[t] == "R":
                    l1_read += 1
                elif mode[t] == "W":
                    l1_writes += 1
                    cacheL1.dirty[i][0] = dirty #if mode is write we always set bit to dirty
                break

        if not l1_hit:
            miss += 1
            if mode[t] == "R":
                l1_read += 1
                l1_read_misses += 1
            elif mode[t] == "W":
                l1_write_misses += 1
                l1_writes += 1

            l1_evicted_value = cacheL1.line[i].pop(-1) #if not hit we pop off the lru block
            l1_evicted_dirty = cacheL1.dirty[i].pop(-1) #pop off lru dirty bit
            if l1_evicted_dirty == dirty: #if the block is dirty/has been tampered with since pull from main memory we must write it back to memory, or l2 cache if it exists
                l1_write_back += 1
            cacheL1.line[i].insert(0, l1_tag[t]) #insert the new block we just read to the front
            cacheL1.dirty[i].insert(0, dirty if mode[t] == "W" else 0) #insert the corresponding dirty bit, if its write put dirty if its read we can make it not dirty (0)

            # If L2 cache exists, check for a hit here if L1 cache has a miss
            if l2_cacheSize != 0:
                l2_hit = False
                
                #this for loop checks for a hit in the l2 cache if l1 miss
                for j in range(l2_assoc):  #weve already looped through the l2 index so we can just loop through the line the index is located
                    if cacheL2.line[l2_num][j] == l2_tag[t]: #if we have a hit
                        l2_hit = True
                        l2_hit_count += 1
                        value = cacheL2.line[l2_num].pop(j) #pop the hit item off
                        cacheL2.line[l2_num].insert(0, value) #insert that hit item back to the front
                        dirty_value = cacheL2.dirty[l2_num].pop(j) #pop off the corresponding dirty bit
                        cacheL2.dirty[l2_num].insert(0, dirty_value) #insert it to the front

                        if mode[t] == "R":
                            l2_read += 1
                        elif mode[t] == "W":
                            l2_writes += 1
                            cacheL2.dirty[l2_num][0] = dirty #if its a write operation make the bit dirty that we just inserted to the front
                        break

                
                #if it wasnt found in the l2 or l1 cache
                if not l2_hit:
                    l2_miss_count += 1
                    if mode[t] == "R":
                        l2_read_misses += 1
                    elif mode[t] == "W":
                        l2_writes += 1
                        l2_write_misses+=1

                    

                    l2_evicted_value = cacheL2.line[l2_num].pop(-1)
                    l2_evicted_dirty = cacheL2.dirty[l2_num].pop(-1)
                    if l2_evicted_dirty == dirty:
                        l2_write_back += 1
                    cacheL2.line[l2_num].insert(0, l2_tag[t])
                    cacheL2.dirty[l2_num].insert(0, dirty if mode[t] == "W" else 0)

                    


                #now whether there was an l2 hit or miss, a block will be evicted from l1 cache and placed into l2 cache, this part checks if its already in l2 cache
                l2_evicted_l1_tag = reformat_l1_tag_to_l2(l1_evicted_value, l1_setNumber, l2_setNumber) #reformatting the evicted l1 tag to be compatible with l2
                if l2_evicted_l1_tag != 0:
                    for j in range(l2_assoc):  #weve already looped through the l2 index so we can just loop through the line the index is located
                        if cacheL2.line[l2_num][j] == l2_evicted_l1_tag: #if we have a hit
                            l2_hit = True
                            value = cacheL2.line[l2_num].pop(j) #pop the hit item off
                            cacheL2.line[l2_num].insert(0, value) #insert that hit item back to the front
                            dirty_value = cacheL2.dirty[l2_num].pop(j) #pop off the corresponding dirty bit
                            cacheL2.dirty[l2_num].insert(0, dirty_value) #insert it to the front

                            if mode[t] == "R":
                                l2_read += 1
                            elif mode[t] == "W":
                                l2_writes += 1
                                cacheL2.dirty[l2_num][0] = dirty #if its a write operation make the bit dirty that we just inserted to the front
                            break
                    
                    #if the block wasnt in the l2 cache we need to evict a block and insert the new block from the l1 cache into l2
                    else:
                        l2_evicted_value = cacheL2.line[l2_num].pop(-1)
                        l2_evicted_dirty = cacheL2.dirty[l2_num].pop(-1)
                        if l2_evicted_dirty == dirty:
                            l2_write_back += 1
                        cacheL2.line[l2_num].insert(0, l2_evicted_l1_tag)
                        cacheL2.dirty[l2_num].insert(0, l1_evicted_dirty)






if replacement == "2":  # Optimal
    for t, (i, l2_num) in enumerate(zip(l1_index, l2_index if l2_index else [None] * len(l1_index))):
        # L1 cache handling
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
            miss += 1
            # Cache miss in L1
            max_future_access_l1 = -1
            farthest_block_l1 = -1

            for j in range(l1_assoc):
                found = False
                for future_t, (future_tag, future_index) in enumerate(zip(l1_tag[t + 1:], l1_index[t + 1:])):
                    if future_tag == cacheL1.line[i][j] and future_index == i:
                        found = True
                        if future_t > max_future_access_l1:
                            max_future_access_l1 = future_t
                            farthest_block_l1 = j
                        break

                if not found:
                    farthest_block_l1 = j
                    break

            if cacheL1.dirty[i][farthest_block_l1] == 1:
                write += 1
                l1_write_back += 1
            if mode[t] == "R":
                l1_read_misses += 1
                l1_read += 1
                cacheL1.dirty[i][farthest_block_l1] = 0
            if mode[t] == "W":
                l1_write_misses += 1
                l1_writes += 1
                cacheL1.dirty[i][farthest_block_l1] = 1

            cacheL1.line[i][farthest_block_l1] = l1_tag[t]

            # L2 cache handling if exists
            if l2_cacheSize != 0:
                for j in range(l2_assoc):
                    if cacheL2.line[l2_num][j] == l2_tag[t]:
                        l2_hit_count += 1
                        if mode[t] == "R":
                            l2_read += 1
                        if mode[t] == "W":
                            l2_writes += 1
                            cacheL2.dirty[l2_num][j] = dirty
                        break
                else:
                    l2_miss_count += 1
                    # Cache miss in L2
                    max_future_access_l2 = -1
                    farthest_block_l2 = -1

                    for j in range(l2_assoc):
                        found = False
                        for future_t, (future_tag, future_index) in enumerate(zip(l2_tag[t + 1:], l2_index[t + 1:])):
                            if future_tag == cacheL2.line[l2_num][j] and future_index == l2_num:
                                found = True
                                if future_t > max_future_access_l2:
                                    max_future_access_l2 = future_t
                                    farthest_block_l2 = j
                                break

                        if not found:
                            farthest_block_l2 = j
                            break

                    if cacheL2.dirty[l2_num][farthest_block_l2] == 1:
                        l2_write_back += 1
                    if mode[t] == "R":
                        l2_read_misses += 1
                        l2_read += 1
                        cacheL2.dirty[l2_num][farthest_block_l2] = 0
                    if mode[t] == "W":
                        l2_writes += 1
                        l2_write_misses += 1
                        cacheL2.dirty[l2_num][farthest_block_l2] = 1

                    cacheL2.line[l2_num][farthest_block_l2] = l2_tag[t]

                    # Move evicted block from L1 to L2
                    l2_evicted_l1_tag = reformat_l1_tag_to_l2(cacheL1.line[i][farthest_block_l1], l1_setNumber, l2_setNumber)
                    if l2_evicted_l1_tag != 0:
                        max_future_access_l2_evicted = -1
                        farthest_block_l2_evicted = -1

                        for j in range(l2_assoc):
                            found = False
                            for future_t, (future_tag, future_index) in enumerate(zip(l2_tag[t + 1:], l2_index[t + 1:])):
                                if future_tag == cacheL2.line[l2_num][j] and future_index == l2_num:
                                    found = True
                                    if future_t > max_future_access_l2_evicted:
                                        max_future_access_l2_evicted = future_t
                                        farthest_block_l2_evicted = j
                                    break

                            if not found:
                                farthest_block_l2_evicted = j
                                break

                        if cacheL2.dirty[l2_num][farthest_block_l2_evicted] == 1:
                            l2_write_back += 1
                        cacheL2.line[l2_num][farthest_block_l2_evicted] = l2_evicted_l1_tag
                        cacheL2.dirty[l2_num][farthest_block_l2_evicted] = cacheL1.dirty[i][farthest_block_l1]



# if replacement == "2":  # Optimal
#     for t, i in enumerate(l1_index):
#         for j in range(l1_assoc):
#             if cacheL1.line[i][j] == l1_tag[t]:
#                 hit += 1
#                 if mode[t] == "R":
#                     l1_read += 1
#                 if mode[t] == "W":
#                     l1_writes += 1
#                     cacheL1.dirty[i][j] = dirty
#                 if wb == "0":
#                     if mode[t] == "W":
#                         write += 1
#                 break
#         else:
#             miss+=1
#             #write += 1
#             # Cache miss
#             max_future_access = -1
#             farthest_block = -1

#             for j in range(l1_assoc):
#                 found = False
#                 for future_t, (future_tag, future_index) in enumerate(zip(l1_tag[t + 1:], l1_index[t + 1:])):
#                     if future_tag == cacheL1.line[i][j] and future_index == i:
#                         found = True
#                         if future_t > max_future_access:
#                             max_future_access = future_t
#                             farthest_block = j
#                         break

#                 if not found:
#                     farthest_block = j
#                     break

#             # Evict the farthest_block and update the cache accordingly
#             if cacheL1.dirty[i][farthest_block] == 1:
#                 write+=1
#                 l1_write_back+=1
#             if mode[t] == "R":
#                 l1_read_misses += 1
#                 l1_read += 1
#                 cacheL1.dirty[i][farthest_block] = 0
#             if mode[t] == "W":
#                 l1_write_misses += 1
#                 l1_writes += 1
#                 cacheL1.dirty[i][farthest_block] = 1

#             cacheL1.line[i][farthest_block] = l1_tag[t]



                        
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
