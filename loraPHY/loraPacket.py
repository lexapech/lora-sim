from dataclasses import dataclass
from typing import Any
from loraPHY.enums import LoraBandwidth, LoraSpreadFactor, LoraCodingRate

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as axes
import random
import scipy
import time
from loraPHY.modemSettings import ModemSettings
from pack_bytes import code4_5678, decode4_5678, pack_bytes
from loraPHY.lora import calculate_lora_bandwidth,calculate_lora_symbol_time

def indep_roll(arr, shifts, axis=1):
    """Apply an independent roll for each dimensions of a single axis.

    Parameters
    ----------
    arr : np.ndarray
        Array of any shape.

    shifts : np.ndarray
        How many shifting to use for each dimension. Shape: `(arr.shape[axis],)`.

    axis : int
        Axis along which elements are shifted. 
    """
    arr = np.swapaxes(arr,axis,-1)
    all_idcs = np.ogrid[[slice(0,n) for n in arr.shape]]

    # Convert to a positive shift
    shifts[shifts < 0] += arr.shape[-1] 
    all_idcs[-1] = all_idcs[-1] - shifts[:, np.newaxis]

    result = arr[tuple(all_idcs)]
    arr = np.swapaxes(result,-1,axis)
    return arr


class LoraPacket:

    def __init__(self, modem_settings: ModemSettings, data=None):
        self.settings = modem_settings
        self.symbol_samples = 1
        if data is not None:
            self.data = list(data)
        
    def modulate(self):
        if self.data is None:
            raise Exception("no data")
        if not self.settings.coding_rate.is_valid():
            raise ValueError(self.settings.coding_rate)
        if not self.settings.bandwidth.is_valid():
            raise ValueError(self.settings.bandwidth)
        if not self.settings.spread_factor.is_valid():
            raise ValueError(self.settings.spread_factor)
        preamble = [0] * self.settings.preamble
        bandwidth = self.get_bandwidth()
        symbols = 2**self.settings.spread_factor.value
        chip_size = bandwidth / symbols
        chirp_rate = chip_size*bandwidth
        symbol_samples = symbols * self.symbol_samples
        coded = code4_5678(self.data,self.settings.coding_rate.value + 4)
        print(coded)
        coded = pack_bytes(coded,\
            self.settings.spread_factor.value,\
            2*(self.settings.coding_rate.value + 4))
        print(coded)
        symbol_count = len(coded)
        symbol_time = calculate_lora_symbol_time(self.settings) * 0.000001
        time = symbol_time* symbol_count
        n_samples = symbol_samples * symbol_count
        print(n_samples)
        t = np.linspace(0, time, n_samples, False) 
        print(time)
        #time_full = symbol_time * (symbol_count+self.settings.preamble+2+2)
        time_full = symbol_time * symbol_count
        #return np.concatenate((self.generate_preamble(self.settings.preamble),self.freq(coded,t))), time_full
        return (self.freq(coded,t)+0.5-symbols/2)*chip_size, time_full

    def demodulate(self,freqs,duration,power_db=0,noise_db=0):
        if not self.settings.coding_rate.is_valid():
            raise ValueError(self.settings.coding_rate)
        if not self.settings.bandwidth.is_valid():
            raise ValueError(self.settings.bandwidth)
        if not self.settings.spread_factor.is_valid():
            raise ValueError(self.settings.spread_factor)

        n_samples = freqs.shape[0]
        


        bandwidth = self.get_bandwidth()
        symbols = 2**self.settings.spread_factor.value
        chip_size = bandwidth / symbols
        chirp_rate = chip_size*bandwidth
        symbol_samples = symbols * self.symbol_samples
        symbol_count = int(duration / (calculate_lora_symbol_time(self.settings)*0.000001))

        t = np.linspace(0, duration, n_samples, False) 


        spectrum = np.full((n_samples,symbols),0)

        #spectrum[:,0] = np.where(np.abs(freqs) <= bandwidth/2,10**(power_db-noise_db/10),0)
        spectrum[:,0] = np.where(np.abs(freqs) <= bandwidth/2,10**((power_db-noise_db)/10),0)
        freqs = np.int_(np.round((freqs / chip_size)  - 0.5 + symbols/2))  

        noise = np.float_(np.random.normal(0, 1, (32, 32)))**2

        noise = np.tile(noise,(int(n_samples/32),int(symbols/32)))
       
        ref = np.int_(np.round(symbols-bandwidth*t)) % (symbols)

        diff2 = indep_roll(spectrum,(freqs + ref)% symbols)

        diff2 = diff2 + noise

        nearest_multiple = int(((n_samples + symbol_samples -1) // symbol_samples) * symbol_samples)
        diff2 = np.split(diff2,nearest_multiple/symbol_samples,axis=0)
        diff2 = np.concatenate(diff2,axis=1)
        diff2 = np.mean(diff2,axis=0)
        diff2 = np.reshape(diff2,(-1,symbols))
        recv = np.argmax(diff2,axis=1)
        data = np.int_(np.round(recv))

        data = [int(x) for x in data]

        decoded = pack_bytes(data,\
            2*(self.settings.coding_rate.value + 4),\
            self.settings.spread_factor.value)
        decoded = decode4_5678(decoded,self.settings.coding_rate.value + 4)
        return decoded, noise

    def freq(self,data,t):
        bandwidth = self.get_bandwidth()
        symbols = 2**self.settings.spread_factor.value
        chip_size = bandwidth / symbols
        
        return np.int_(np.fmod(np.round(bandwidth*t + np.take(data,np.int_(t*chip_size))),symbols))

    def generate_preamble(self,symbol_count):
        bandwidth = self.get_bandwidth()
        symbols = 2**self.settings.spread_factor.value

        symbol_samples = symbols * self.symbol_samples
        symbol_count = symbol_count + 2
        symbol_time = calculate_lora_symbol_time(self.settings) * 0.000001

        t = np.linspace(0, symbol_time* symbol_count, symbol_samples * symbol_count, False) 

        
        preamble = np.int_(np.fmod(np.floor(bandwidth*t),symbols))
        symbol_count = 2
        t = np.linspace(0, symbol_time* symbol_count, symbol_samples * symbol_count, False) 
        sync = np.int_(np.remainder(symbols - np.floor(bandwidth*t),symbols))
        return np.concatenate((preamble,sync))


    def get_bandwidth(self):
        return calculate_lora_bandwidth(self.settings.bandwidth)


