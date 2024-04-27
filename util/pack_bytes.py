import ctypes
import os
import time
#random_bytes = os.urandom(100)

parity=[
    [0x0,0x3,0x5,0x6,0x9,0xa,0xc,0xf,0x11,0x12,0x14,0x17,0x18,0x1b,0x1d,0x1e],
    [0x0,0x5,0x9,0xc,0x12,0x17,0x1b,0x1e,0x22,0x27,0x2b,0x2e,0x30,0x35,0x39,0x3c],
    [0x00,0x07,0x19,0x1e,0x2a,0x2d,0x33,0x34,0x4b,0x4c,0x52,0x55,0x61,0x66,0x78,0x7f],
    [0,0x87,0x99,0x1e,0xAA,0x2d,0x33,0xb4,0x4b,0xcc,0xd2,0x55,0xe1,0x66,0x78,0xff]
]

hamming_corr=[0,0,0,1,0,2,4,8]
def code45(arr):
    res=[]
    for b in arr:
        b = ((b&0x0F)<<1) | ((b&0xF0)<<2)
        r = b
        b = (b>>1) ^ (b>>2) ^ (b>>3) ^ (b>>4)
        r |= b&0x21
        res.append(r)
        #print(bin(r))
    return res

def code4_5678(arr, rate):
    if rate < 5 or rate > 8:
        raise ValueError
    res=[]
    for b in arr:
        r = parity[rate-5][b&0x0F] | (parity[rate-5][(b>>4)&0x0F]<<rate)
        res.append(r)
    return res

def decode4_5678(arr, rate):
    if rate < 5 or rate > 8:
        raise ValueError
    res=[]
    errors=0
    if rate in [5,6]:
        for b in arr:
            r = (b >> (rate-4)) & 0x0F
            r |= (b >> 2*(rate-4)) & 0xF0
            c = parity[rate-5][r&0x0F] | (parity[rate-5][(r>>4)&0x0F]<<rate)
            if c != b:
                errors+=1
            res.append(r)
    else:
        for b in arr:
            r = ((b & 0x4) >> 2) | ((b & 0x70) >> 3)
            r |= ((((b>>rate) & 0x4) >> 2) | (((b>>rate) & 0x70) >> 3))<<4
            
            c = parity[rate-5][r&0x0F] | (parity[rate-5][(r>>4)&0x0F]<<rate)
            d = b ^ c
            if rate == 7:
                d1 = d&0x3 | ((d&0x8)>>1)
                d2 = ((d&0x180)>>7) | ((d&0x200)>>8)
                r ^= hamming_corr[d1]
                r ^= hamming_corr[d2]<<4
            else:
                d1 = d&0x3 | ((d&0x8)>>1)
                
                d2 = ((d&0x300)>>8) | ((d&0x800)>>9)
                r ^= hamming_corr[d1]
                r ^= hamming_corr[d2]<<4
                if d1>0:                  
                    b ^= 1 << (d1-1)
                if d2>0:                  
                    b ^= 1 << (d2-1+8)
                p1 = b ^ (b>>1) ^ (b>>2) ^ (b>>3)^ (b>>4)^ (b>>5)^ (b>>6)
                p2 = (b>>8) ^ (b>>9) ^ (b>>10) ^ (b>>11) ^ (b>>12) ^ (b>>13) ^ (b>>14)

                if (p1 & 1) != ((b&0x80)>>7) or (p2 & 1) != ((b&0x8000)>>15 ):
                    errors+=1
            res.append(r)
    return res, errors

def code46_2(arr):
    res=[]
    for b in arr:
        r = parity46[b&0x0F] | (parity46[(b>>4)&0x0F]<<6)
        res.append(r)
    return res

def uncode45(arr):
    res=[]
    for b in arr:
        r = (b >> 1) & 0x0F
        r |= (b >> 2) & 0xF0
        res.append(r)
    return res

def uncode46(arr):
    res=[]
    for b in arr:
        r = (b >> 2) & 0x0F
        r |= (b >> 4) & 0xF0
        res.append(r)
    return res

def code46(arr):
    for b in arr:
        b = ((b&0x0F)<<2) | ((b&0xF0)<<4)
        r = b
        p1 = (b>>2) ^ (b>>3) 
        p2 = (b>>3) ^ (b>>4)
        r |= p1&0x41 | p2&0x82
        print(hex(r))



def pack_bytes(arr, out_bits=8, in_bits=8):
    fifo_size = 4 * max(in_bits,out_bits)
    free = fifo_size
    avail=0
    arr_idx=0
    fifo=0
    res=[]
    while True:
        while free >=in_bits and arr_idx < len(arr):
            fifo |= (arr[arr_idx]&((1<<in_bits)-1)) << (free - in_bits)
            free -= in_bits
            avail+=in_bits
            
            arr_idx+=1  
        if avail >= out_bits:
            #print("avil",avail)
            #print("free",free)
            #print(hex(fifo))
            res.append(fifo >> (fifo_size - out_bits))
            avail-=out_bits
            #print("shift")
            #avail+=out_bits
            fifo <<= out_bits
            fifo &= (1<<fifo_size) - 1
            free += out_bits
        else:
            if avail == 0:
                break
            else:
                avail=out_bits
    return res


#print([hex(x) for x in pack_bytes([1,2,3,4,5,6],8,4)])

#print([hex(x) for x in random_bytes])
#start = time.time()
#c = code4_5678(random_bytes,6)
#c[0]^=4
#v,e = decode4_5678(c,6)
#print(time.time() - start)
#print([hex(x) for x in v],e)

#code46(list(range(16)))