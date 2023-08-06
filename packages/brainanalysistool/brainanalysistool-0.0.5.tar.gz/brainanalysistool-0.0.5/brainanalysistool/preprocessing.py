import matplotlib.pyplot as plt
from scipy import signal
import numpy as np

###### 
# input:
# sig shape:channels*(trials)*time
# output:
# sig shape:same as input
def fir_filt_bp(sig, fs=1000, band=[0.1,100]):
    lb = band[0]
    hb = band[1]
    bands = [0,lb-lb/20,lb,hb,hb+hb/20,fs/2]
    desired = [0,0,1,1,0,0]
    fir = signal.firls(149, bands, desired, fs=fs)
    # fig,ax = plt.subplots()    
    # freq, response = signal.freqz(fir)
    # ax.semilogy(0.5*fs*freq/np.pi, np.abs(response))
    # plt.show()
    filted_sig = signal.filtfilt(fir,1,sig)
    return filted_sig

def butter_filt(sig, fs, band, mod='bandpass'):
    if mod == 'bandpass':
        b, a = signal.butter(4, [2*band[0]/fs,2*band[1]/fs], 'bandpass')
    elif mod == 'lowpass':
        b, a = signal.butter(4, 2*band/fs, 'lowpass')
    elif mod == 'highpass':
        b, a = signal.butter(4, 2*band/fs, 'highpass')
    elif mod == 'bandstop':
        b, a = signal.butter(4, [2*band[0]/fs,2*band[1]/fs], 'bandstop')
    filted_sig = signal.filtfilt(b, a, sig)
    return filted_sig

def re_reference(sig,ref_chan):
    # raw_sig removed powerline (chans*totaltime)
    sig = sig-sig[ref_chan]
    return sig

def powerline_interference_filt(sig, fs, pl_freq=50):
    sig = butter_filt(sig,fs,[pl_freq-0.5,pl_freq+0.5],'bandstop')
    sig = butter_filt(sig,fs,[2*pl_freq-0.5,2*pl_freq+0.5],'bandstop')
    sig = butter_filt(sig,fs,[3*pl_freq-0.5,3*pl_freq+0.5],'bandstop')
    sig = butter_filt(sig,fs,[4*pl_freq-0.5,4*pl_freq+0.5],'bandstop')
    return sig

def default_preprocess(sig,fs,band=[1,100],normed=False):
    sig = butter_filt(sig,fs,band,'bandpass')
    
    sig[np.isnan(sig)]=0
    if normed:
        sig = (sig-np.mean(sig))/np.std(sig)
    return sig

def sig_slice(sig, fs, start, end, time_array):
    #######
    # input:
    # sig.shape = (channels,long_time)
    # output:
    # sig.shape = (channels,trials,trial_time)
    period = end-start
    time_points = np.linspace(start/fs,(end-1)/fs,period)
    
    channel_trial_data_ = np.zeros((sig.shape[0],time_array.shape[0],period))
    channel_trial_data = np.zeros((sig.shape[0],time_array.shape[0],period))
    for id in range(sig.shape[0]):
        for trial,evoke in enumerate(time_array[:,0]):
            channel_trial_data_[id][trial] = sig[id][evoke+start:evoke+end]
            channel_trial_data[id][trial] = sig[id][evoke:evoke+period]
    return channel_trial_data_,channel_trial_data,time_points

def gen_time_array(time_stamp,start_time):
    evoke_time_array = time_stamp[:,0]
    stim_end_array = time_stamp[:,1]
    end_time_array = time_stamp[:,2]
    evoke_time = np.zeros((time_stamp.shape[0],1),int)
    stim_end = np.zeros((time_stamp.shape[0],1),int)
    end_time = np.zeros((time_stamp.shape[0],1),int)
    # print(evoke_time.shape[0])
    for i in range(evoke_time_array.shape[0]):
        evoke_time[i] = (evoke_time_array[i][0,-2]*60+evoke_time_array[i][0,-1])*1000 - start_time
        stim_end[i] = (stim_end_array[i][0,-2]*60+stim_end_array[i][0,-1])*1000 - start_time
        end_time[i] = (end_time_array[i][0,-2]*60+end_time_array[i][0,-1])*1000 - start_time

    time_array = np.concatenate((evoke_time,stim_end,end_time),1)
    return time_array

def minus_baseline_ave(ct_sig,stim_start_pnt):
    ct_sig = ct_sig[:,:]-np.mean(ct_sig[:,:,:stim_start_pnt],-1).reshape(ct_sig.shape[0],ct_sig.shape[1],1)
    return ct_sig


if __name__ == '__main__':
    fir_filt_bp()