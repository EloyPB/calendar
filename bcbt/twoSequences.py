from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import pylab as py

simultaneous = False

## Setup parameters and state variables
N    = 6                       # number of neurons
if simultaneous:
    T=100                      # total time to simulate (msec)
else:
    T=300 
dt   = 0.125                   # simulation time step (msec)
time = np.arange(0, T+dt, dt)  # time array


## LIF properties
Vm      = np.zeros([N,len(time)])  # potential (V) trace over time
tau_m   = 15                       # time constant (msec)
tau_ref = 4                        # refractory period (msec)
tau_psc = 5                        # post synaptic current filter time constant
Vth     = 1                        # spike threshold (V)


## Currents
I    = np.zeros((N,len(time)))
Iext = np.zeros(N) # externally applied stimulus


## Synapse weight matrix
synapses = np.zeros((N,N))

# within first circuit
synapses[0,1] = 1.2
synapses[1,2] = 1.2

r = 0.4
synapses[0,2] = r
synapses[2,0] = r
synapses[2,1] = r
synapses[1,0] = r

# # within second circuit
synapses[3,4] = 1.2
synapses[4,5] = 1.2
    
synapses[3,5] = r
synapses[5,3] = r
synapses[5,4] = r
synapses[4,3] = r

synapses = synapses.T


## Synapse current model
def Isyn(t):
    '''t is an array of times since each neuron's last spike event'''
    t[np.nonzero(t < 0)] = 0
    return t*np.exp(-t/tau_psc)


last_spike = np.zeros(N) - 100*tau_ref

## Simulate network
raster = np.zeros([N,len(time)])*np.nan

for i, t in enumerate(time[1:],1):
    active = np.nonzero(t > last_spike + tau_ref)
    Vm[active,i] = Vm[active,i-1] + (-Vm[active,i-1] + I[active,i-1]) / tau_m * dt

    spiked = np.nonzero(Vm[:,i] > Vth) 
    last_spike[spiked] = t
    raster[spiked,i] = spiked[0]+1
    
    Iext = np.zeros(N)
    if not simultaneous:
        if t > 10 and t < 20:
            Iext[2] = 2.2
        elif t > 60 and t < 80:
            Iext[0] = 1.8
            Iext[3] = 1.8
        elif t > 180 and t < 190:
            Iext[5] = 2.2
        elif t > 230 and t < 250:
            Iext[0] = 1.8
            Iext[3] = 1.8
    else:
        if t > 10 and t < 20:
            Iext[2] = 2.2
            Iext[5] = 2.2
        elif t > 60 and t < 80:
            Iext[0] = 1.8
            Iext[3] = 1.8

    
    I[:,i] = Iext + synapses.dot(Isyn(t - last_spike))

## plot membrane potential trace
plt.figure(figsize=(6,3))
py.plot(time, np.transpose(raster), 'b|', mew=2)
py.ylabel('Neuron')
py.xlabel('Time (msec)')
py.ylim([0.75,N+0.25])
py.xlim([0,T])
cn = ['A1','B', 'C', 'A2', 'D', 'E']
plt.yticks(  np.arange(1,N+1) , cn )
plt.tight_layout()

plt.savefig("simultaneous"+str(simultaneous)+".png", dpi=500)

# f, ax = plt.subplots(N, 2)
# 
# for n in range(N):
#     ax[n,0].plot(time, I[n,:])
#     ax[n,0].set_xlabel('Time (msec)')
#     ax[n,0].set_xlim([0,T])
#     ax[n,0].set_title("I")
#      
#     ax[n,1].plot(time, Vm[n,:])
#     ax[n,1].set_xlabel('Time (msec)')
#     ax[n,1].set_xlim([0,T])
#     ax[n,1].set_title("Vm")

py.show()

