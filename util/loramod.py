import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as axes
import random
import scipy
import time

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


# Sample rate 1000 hz / second
n = 10000
max_time = 0.01
sample_freq = n/max_time
t = np.linspace(0, max_time, n, False)  
# Generate a sawtooth signal with frequency of 5 Hz
bandwidth = 500000
spreading_factor=7

symbols = 2**spreading_factor

chip_size = bandwidth / symbols
chirp_rate = chip_size*bandwidth



print("chip",)

symbol_samples = int(sample_freq/chip_size)

spectrum = np.full((n,symbols),0)



data = [random.randint(0, 2**spreading_factor - 1) for x in range(0,2**spreading_factor)]
#data = np.array([3*x for x in range(0,symbols)])
def shift(t):
    return np.take(data,np.int_(t*chip_size))

    # return data[int(np.floor(t*chip_size))]

def freq(t):
    return np.int_(np.fmod(np.floor(bandwidth*t) + np.take(data,np.int_(t*chip_size)),symbols))

#vec_freq = np.vectorize(freq)

spectrum[:,0] = np.ones(n)*200.0

noise = np.float_(np.random.normal(0, 10, (n, symbols)))
start_time = time.time()
freqs = freq(t)

spectrum = indep_roll(spectrum,freqs)

print(spectrum)
spectrum = spectrum + noise*5


#wave = (np.fmod(chirp_rate*t + vec_shift(t), bandwidth) - 0.5*bandwidth)
print(symbol_samples)
nearest_multiple = int(((n + symbol_samples -1) // symbol_samples) * symbol_samples)



#ref_spectrum = np.full((n,symbols),0)
#ref_spectrum[:,0] = np.ones(n)*20.0
ref = np.int_(symbols-bandwidth*t) % (symbols)
#ref_spectrum = indep_roll(ref_spectrum,ref)

t = np.pad(t,(0,nearest_multiple-n),mode="linear_ramp",end_values=max_time*nearest_multiple/n)
#ref = np.int_(bandwidth*t) % (symbols) - symbols/2


#diff = np.fmod(wave-ref + symbols ,symbols)
#diff = wave*ref
#diff2=scipy.signal.fftconvolve(spectrum, ref_spectrum, mode='full',axes=1)

diff2 = indep_roll(spectrum,ref)*20.0


end_time = time.time()
execution_time = end_time - start_time
print('Execution Time: ',execution_time)

print(np.shape(diff2))

#diff2=diff2[:,:symbols-1]+diff2[:,symbols:]

diff2 = np.pad(diff2,((0,nearest_multiple-n),(0,0)),mode="edge")


print(nearest_multiple/symbol_samples)

diff2 = np.split(diff2,nearest_multiple/symbol_samples,axis=0)
diff2 = np.concatenate(diff2,axis=1)
diff2 = np.mean(diff2,axis=0)
diff2 = np.reshape(diff2,(-1,symbols))
recv = np.argmax(diff2,axis=1)



#wave = np.pad(wave,(0,nearest_multiple-n),mode="edge")

#wave_matrix = np.reshape(wave,(-1,symbol_samples))


#recv = np.mean(wave_matrix,axis=1)
#zero = recv[0]

print(data[:int(nearest_multiple/symbol_samples)])
print(np.int_(np.round(recv)))
plt.figure(figsize=(20,5))
#plt.plot(t, wave)
#plt.plot(t, ref)
#plt.plot(diff2)
plt.imshow(np.transpose(spectrum), cmap='hot', interpolation='nearest',aspect='auto')
#plt.imshow(np.transpose(diff2), cmap='hot', interpolation='nearest',aspect='auto')
plt.title("Sawtooth Waveform")
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.ylim(0,128)
#plt.grid(True, which='both')
plt.axhline(0, color='k')
plt.show()