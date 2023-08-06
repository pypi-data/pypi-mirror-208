import matplotlib.pyplot as plt
import numpy as np
from .preprocessing import butter_filt
from .WaveAnalysisFun import *
from scipy import signal





def plot_vector_field(x, y, vec, pixel_spacing_x, pixel_spacing_y, norm=True, fig=None,ax=None, show_flag=True):
    #######
    # INPUT
    # ph - complex-valued scalar field representing vector directions
    # norm - whether to represent the norm of the vec 
    # OUTPUT
    # vector field plot
    #######

    x = x-pixel_spacing_x/2
    y = y-pixel_spacing_y/2
    if norm:
        u = np.real(vec)
        v = np.imag(vec)
    else:
        u = np.real(np.exp(1j*np.angle(vec)))
        v = np.imag(np.exp(1j*np.angle(vec)))

    if ax == None:
        if fig==None:
            fig = plt.figure()
        ax = fig.add_subplot(111)
    ax.quiver(x, y, u, -v, color = 'k',scale=4,scale_units='xy',width=0.005)
    
    if show_flag:
        plt.show()
    return fig,ax


# # 绘制每个通道图像
def show_all_channelwave(sig, grishape, fig=None, show_flag=True):
    #######
    # input:
    # sig.shape = (channels,time) 
    #######
    if fig==None:
        fig = plt.figure()
    for id in range(sig.shape[0]):
        ax = fig.add_subplot(grishape[0],grishape[1],id+1)
        ax.plot(sig[id])
        ax.set_ylabel('V/uV')
    if show_flag:
        plt.show()
    return fig

def show_channelwave(sig, fs, chan, fig=None, ax=None,show_flag=True):
    #######
    # input:
    # sig.shape = (channels,time) 
    #######
    if ax==None:
        if fig==None:
            fig,ax = plt.subplots()
        else:
            ax = fig.add_subplot(111)
    time_points = np.arange(0,len(sig),1)/fs
    ax.plot(time_points,sig)
    ax.set_xlabel('time(s)')
    ax.set_ylabel('V/uV')
    ax.set_title(f'Chan {chan+1}')
    if show_flag:
        plt.show()
    return fig


# wave of each channel 
def channel_wave(trial_sig, fs, time_points, lowband=[3,6], highband=[30,50],period=None, fig=None, fig1=None, show_flag=True):
    #######
    # input:
    # trial_sig:shape=(trial,time) type=np.array
    #######
    if fig == None:
        fig = plt.figure()
    if fig1 == None:
        fig1 = plt.figure()
    if period == None:  
        period=[0,trial_sig.shape[1]]
    ax0 = fig.add_subplot(111)
    ax1 = fig1.add_subplot(211)
    ax2 = fig1.add_subplot(212)

    low_t_sig = butter_filt(trial_sig,fs,lowband,'bandpass')
    high_t_sig = butter_filt(trial_sig,fs,highband,'bandpass')

    # 每个试次图像
    for trial in range(trial_sig.shape[0]):          # gai++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ax0.plot(time_points,trial_sig[trial],color='0.1')
        ax1.plot(time_points[int(period[0]):int(period[1])],low_t_sig[trial][int(period[0]):int(period[1])],color='0.1')
        ax2.plot(time_points[int(period[0]):int(period[1])],high_t_sig[trial][int(period[0]):int(period[1])],color='0.1')
        # ax3.plot(time_points,channel_trial_wave2_[id][trial],color='0.1')
    # 试次间均值
    ax0.plot(time_points,np.mean(trial_sig,0),color='red')
    ax1.plot(time_points[int(period[0]):int(period[1])],np.mean(low_t_sig[:,int(period[0]):int(period[1])],0),color='red')
    ax2.plot(time_points[int(period[0]):int(period[1])],np.mean(high_t_sig[:,int(period[0]):int(period[1])],0),color='red')
    # ax3.plot(time_points,np.mean(channel_trial_wave2_[id],0),color='red')
    # 标准差
    ax0.plot(time_points,np.mean(trial_sig,0)+np.std(trial_sig,0),color='red',linestyle='--')
    ax0.plot(time_points,np.mean(trial_sig,0)-np.std(trial_sig,0),color='red',linestyle='--')
    ax0.set_title('channel trial-mean LFP')
    fig1.suptitle('channel trial-mean LFP at different frequences')
    ax1.set_title('low-frequency')
    ax2.set_title('high-frequency')
    if show_flag:
        plt.show()
    return fig,fig1

def chan_trail_ave_sig(trial_sig, time_points, chan, period=None, fig=None, ax=None, normed=False, show_flag=True):
    # period : time point
    if ax==None:
        if fig==None:
            fig,ax = plt.subplots()
        else:
            ax = fig.add_subplot(111)
    if period==None:
        for trial in range(trial_sig.shape[0]):
            ax.plot(time_points,trial_sig[trial],color='0.1',linewidth =0.1)
        ax.plot(time_points,np.mean(trial_sig,0),color='red')
        ax.plot(time_points,np.mean(trial_sig,0)+np.std(trial_sig,0),color='red',linestyle='--',linewidth =0.5)
        ax.plot(time_points,np.mean(trial_sig,0)-np.std(trial_sig,0),color='red',linestyle='--',linewidth =0.5)
        

    else:
        period = [int(period[0]),int(period[1])]
        for trial in range(trial_sig.shape[0]):
            ax.plot(time_points[period[0]:period[1]],trial_sig[trial,period[0]:period[1]],color='0.1',linewidth =0.1)
        ax.plot(time_points[period[0]:period[1]],np.mean(trial_sig[:,period[0]:period[1]],0),color='red')
        ax.plot(time_points[period[0]:period[1]],np.mean(trial_sig[:,period[0]:period[1]],0)+np.std(trial_sig[:,period[0]:period[1]],0),color='red',linestyle='--',linewidth =0.5)
        ax.plot(time_points[period[0]:period[1]],np.mean(trial_sig[:,period[0]:period[1]],0)-np.std(trial_sig[:,period[0]:period[1]],0),color='red',linestyle='--',linewidth =0.5)
    ax.set_xlabel('time(s)')
    
    if normed:
        ax.set_ylabel('Normed')
    else:
        ax.set_ylabel('V/uV')
    ax.set_title(f'Chan {chan+1}')
    if show_flag:
        plt.show()
    return fig,ax

# # ITPC
# # ITPC循环单通道（一次显示一个channellist中的通道）
def ITPC_channel(trial_sig, fs, time_points, period, chan, band=[1,70], fig=None,ax=None, show_flag=True):
    #######
    # input:
    # trial_sig:shape=(trial,time) type=np.array
    #######
    frequencies = np.logspace(np.log10(band[0]),np.log10(band[1]))
    itpc = np.zeros((len(frequencies),period))
    for idx,f in enumerate(frequencies):
        itpc[idx] = ITPC(trial_sig,fs,f)
    
    if ax==None:
        if fig==None:
            fig,ax = plt.subplots()
        else:
            ax = fig.add_subplot(111)
    levels = [0,0.2,0.4,0.6,0.8,1]
    ax_ = ax.pcolormesh(time_points,frequencies,itpc,cmap='jet',vmin=0)
    # plt.contourf(time_points,frequencies,itpc_mean,100,cmap='jet',vmax=1,vmin=0, extend='min')
    ax.set_yscale('symlog')
    fig.colorbar(ax_,ax=ax,ticks=levels,label='ITPC')
    # plt.yticks([1,3,5,10,30,50])
    ax.set_title(f'ITPC channel {chan+1}')
    ax.set_ylabel('freq(Hz)')
    ax.set_xlabel('time(s)')
    if show_flag:
        plt.show()
    return fig,ax

# # ITPC_location
def ITPC_location(x,y,ct_sig,interval,fs,freq_band,channel_list,bad_chan_list,gridshape,fig=None,show_flag=True):
    ###########
    # INPUT:
    # ct_sig:(channels,trials,time)


    itpc_location = []
    for id in channel_list:
        if id in bad_chan_list:
            itpc_location.append(float('inf'))
            continue
        frequencies = np.linspace(freq_band[0],freq_band[1],40)
        itpc = np.zeros(len(frequencies),)

        for idx,f in enumerate(frequencies):
            itpc[idx] = np.mean(ITPC(ct_sig[id,:,int(interval[0]):int(interval[1])],fs,f))
        
        itpc_location.append(np.mean(itpc))
    itpc_location = np.array(itpc_location).reshape(gridshape[0],gridshape[1])
    if fig==None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax_ = ax.matshow(x_grid,y_grid,itpc_location,cmap='jet')
    ax_ = ax.pcolor(x,y,itpc_location ,cmap='jet')
    # plt.gca().invert_yaxis()
    ax.set_title(f'{freq_band[0]}-{freq_band[1]}Hz ITPC of each location')
    fig.colorbar(ax_,ax=ax,label='ITPC')
    ax.set_xlabel('AP(ms)')
    ax.set_ylabel('ML(ms)')
    ax.invert_xaxis()
    if show_flag:
        plt.show()
    return fig


# # Average filtered LFP traveling wave-like behavior
def plot_traveling_wave_behavior(ct_sig, fs, t_period, show_axis_loc, start, travel_axis_list, band, fig=None,cmap='PRGn',show_flag=True):
    # INPUT:
    # ct_sig:shape(channels,trials,time)

    if fig == None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    t = np.array(np.array(t_period)*fs,int)-start
    t_pnts = np.arange(t_period[0],t_period[1],1/fs)
    tw_mat = np.zeros((len(travel_axis_list),ct_sig.shape[2]))
    # y = np.arange(-1,-len(travel_axis_list)-1,-1)
    for i,id in enumerate(travel_axis_list):
        tw_mat[i] = np.mean(ct_sig[id],0)

    ax_ = ax.pcolor(t_pnts,show_axis_loc,tw_mat[:,t[0]:t[1]], cmap=cmap)
    ax.set_title(f'Normalized {band[0]}-{band[1]}Hz Wave')
    ax.set_xlabel('time(s)')
    ax.set_ylabel('AP(ms)')
    # ax.invert_yaxis()
    fig.colorbar(ax_,ax = ax, label='Voltage (μV)')
    if show_flag:
        plt.show()
    return fig


# Phase-amplitude coupling MI
def Phase_amplitude_coupling(trial_sig_low, trial_sig_high, chan,n_bin = 20, fig=None, show_flag=True):
    # INPUT:
    # trial_sig:shape(trials,time)
    # low: baseband
    # high: carrier
    if fig==None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    analytic_sig_low = signal.hilbert(trial_sig_low)
    analytic_sig_high = signal.hilbert(trial_sig_high)

    mid_interval = np.arange(-np.pi,np.pi,2*np.pi/n_bin)+np.pi/n_bin

    Phase = np.angle(analytic_sig_low)
    Amp = np.abs(analytic_sig_high)
    MI, MeanAmp = PAC_MI(Phase,Amp,n_bin)

    ax.bar(mid_interval,MeanAmp)
    ax.set_title(f'channel {chan+1}  MI = {MI:.4f}')
    ax.set_ylabel('Amp')
    ax.set_xlabel('Phase')

    if show_flag:
        plt.show()
    return fig

    
def MI_maxAmpPhase_location(x,y,ct_sig_low, ct_sig_high, channel_list, bad_channel_list, gridshape, n_bin=20, fig=None, fig1=None, show_flag=True):
    # Phase Coupling MI

    if fig==None:
        fig = plt.figure()
    if fig1==None:
        fig1 = plt.figure()
    
    analytic_low = signal.hilbert(ct_sig_low)
    analytic_high = signal.hilbert(ct_sig_high)

    MI_Gr = np.zeros((len(channel_list),))
    MeanAmp_ct = np.zeros((len(channel_list),n_bin))
    for loc,id in enumerate(channel_list):
        if id in bad_channel_list:
            MI_Gr[loc] = float('inf')
            continue
        Phase = np.angle(analytic_low[id])
        Amp = np.abs(analytic_high[id])
        MI_Gr[loc], MeanAmp_ct[id] = PAC_MI(Phase,Amp,n_bin)


    MI_Gr = MI_Gr.reshape(gridshape[0],gridshape[1])


    ax = fig.add_subplot(111)
    ax_ = ax.pcolor(x,y,MI_Gr ,cmap='rainbow')
    ax.set_title('Phase Coupling MI')
    ax.set_xlabel('AP(ms)')
    ax.set_ylabel('ML(ms)')
    ax.invert_xaxis()
    fig.colorbar(ax_,ax = ax,label='MI')
    
    mid_interval = np.arange(-np.pi,np.pi,2*np.pi/n_bin)+np.pi/n_bin
    PA_Gr = np.zeros(len(channel_list))
    for loc,id in enumerate(channel_list):
        if id in bad_channel_list:
            PA_Gr[loc] = float('inf')
            continue
        # print(np.array(np.where(MeanAmp_ct[id] == np.max(MeanAmp_ct[id]))))
        bin_num = int(np.array(np.where(MeanAmp_ct[id] == np.max(MeanAmp_ct[id]))))
        PA_Gr[loc] = mid_interval[bin_num]

    PA_Gr = PA_Gr.reshape((gridshape[0],gridshape[1]))

    PA_ax = fig1.add_subplot(111)
    PA_ax_ = PA_ax.pcolor(x,y,PA_Gr, vmin=-np.pi, vmax=np.pi, cmap='gist_rainbow')
    PA_ax.set_title('low-freq oscillation Phase with Maximum high-freq oscillation Amplitude')
    PA_ax.invert_xaxis()
    fig1.colorbar(PA_ax_,ax = PA_ax,ticks=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi],label='Phase of low-frequency oscillation')
    PA_ax.set_xlabel('AP(ms)')
    PA_ax.set_ylabel('ML(ms)')
    
    if show_flag:
        plt.show()
    return fig,fig1

# # Spacial wave length and speed
def waveLen_waveSpeed(ct_sig_low, ct_sig_high, fs, stim_start, channel_list, pixel_spacing_x, pixel_spacing_y, Thresh, gridshape, n_mode, tt, fig1=None, fig2=None, show_flag=True):  
    
    # INPUT:
    # tt: 取信号比较明显的时刻作为计算时间相位的时间点
    
    SVD_tc_data = ct_sig_low.swapaxes(0,1)
    SVD_tc_data1 = ct_sig_high.swapaxes(0,1)
    
    period = SVD_tc_data.shape[2]

    most_resp_mode = np.zeros((SVD_tc_data.shape[0],),dtype=int)

    most_resp_mode1 = np.zeros((SVD_tc_data.shape[0],),dtype=int)

    
    low_waveLength_trials = np.zeros((SVD_tc_data.shape[0],gridshape[0],gridshape[1],SVD_tc_data.shape[2]))
    low_waveVelocity_trials = np.zeros((SVD_tc_data.shape[0],gridshape[0],gridshape[1],SVD_tc_data.shape[2]))
    high_waveLength_trials = np.zeros((SVD_tc_data.shape[0],gridshape[0],gridshape[1],SVD_tc_data.shape[2]))
    high_waveVelocity_trials = np.zeros((SVD_tc_data.shape[0],gridshape[0],gridshape[1],SVD_tc_data.shape[2]))

    for trial in range(SVD_tc_data.shape[0]):
        SVDout, SpatialAmp, SpatialPhase, TemporalAmp, TemporalPhase, = complexSVD(SVD_tc_data[trial],n_mode)
        _, _, most_resp_mode[trial] = TemporalImportance_Amp(TemporalAmp,stim_start,period,Thresh=Thresh,baselineEnd=0)
        # print(most_resp_mode[trial])
        rec_a = SVDModeReconstruct(SVDout,most_resp_mode[trial])
        ft, signIF= instantaneous_frequency(rec_a,fs)
        rec_a_rct = reorgChannels(rec_a,channel_list,gridshape)
        # print(rec_a_rct.shape)
        pm,pd,dx,dy = phase_gradient_complex_multiplication(rec_a_rct,pixel_spacing_x,pixel_spacing_y,signIF)
        # print(pd.shape)


        # wave length and velocity
        # Spacial wavelength: reciprocal of spatial frequency  空间频率倒数
        # spatial frequency：梯度模值/2*pi
        # velocity：Spacial wavelength*temporal frequency

        ft_rct = reorgChannels(ft,channel_list,gridshape)
        low_waveLength_trials[trial] = 1/pm
        low_waveVelocity_trials[trial] = ft_rct/pm
        
        # 重复一遍高频信号
        SVDout, SpatialAmp, SpatialPhase, TemporalAmp, TemporalPhase, = complexSVD(SVD_tc_data1[trial],n_mode)
        _, _, most_resp_mode1[trial] = TemporalImportance_Amp(TemporalAmp,stim_start,period,Thresh=Thresh,baselineEnd=0)
        # print(most_resp_mode[trial])
        # mostRespSPhase1[trial] = SpatialPhase[:,most_resp_mode1[trial]]
        rec_a = SVDModeReconstruct(SVDout,most_resp_mode1[trial])
        ft, signIF= instantaneous_frequency(rec_a,fs)
        rec_a_rct = reorgChannels(rec_a,channel_list,gridshape)
        # print(rec_a_rct.shape)
        pm,pd,dx,dy = phase_gradient_complex_multiplication(rec_a_rct,pixel_spacing_x,pixel_spacing_y,signIF)
        # print(pd.shape)
        ft_rct = reorgChannels(ft,channel_list,gridshape)
        
        high_waveLength_trials[trial] = 1/pm
        high_waveVelocity_trials[trial] = ft_rct/pm


    # 绘制波长波速直方图
    if fig1 == None:
        fig1 = plt.figure()
    if fig2 == None:
        fig2 = plt.figure()
    f1_ax1 = fig1.add_subplot(111)
    low_wl = low_waveLength_trials[:,:,:,tt].reshape(-1)
    low_wl = low_wl[low_wl<10]
    high_wl = high_waveLength_trials[:,:,:,tt].reshape(-1)
    high_wl = high_wl[high_wl<10]
    num_bins = 100
    n, bins, patches = f1_ax1.hist(low_wl,num_bins, density=True,facecolor='blue', alpha=0.5) 
    n, bins, patches = f1_ax1.hist(high_wl,num_bins, density=True,facecolor='red', alpha=0.5) 
    # f1_ax1.set_xscale('log')
    f1_ax1.legend(['low-freq wave','high-freq wave'])
    f1_ax1.set_xlabel('WaveLength(mm/cycle)') 
    f1_ax1.set_ylabel('Probability') 
    f1_ax1.set_title('Histogram of WaveLength') 

    f1_ax2 = fig2.add_subplot(111)
    low_wv = low_waveVelocity_trials[:,:,:,tt].reshape(-1)
    low_wv = low_wv[low_wv<200]
    low_wv = low_wv[low_wv>0]/1000
    high_wv = high_waveVelocity_trials[:,:,:,tt].reshape(-1)
    high_wv = high_wv[high_wv<200]
    high_wv = high_wv[high_wv>0]/1000
    # print(low_waveLength_trials[1,:,:,tt])
    num_bins = 100
    n, bins, patches = f1_ax2.hist(low_wv,num_bins, density=True,facecolor='blue', alpha=0.5) 
    n, bins, patches = f1_ax2.hist(high_wv,num_bins, density=True,facecolor='red', alpha=0.5) 
    # f1_ax2.set_xscale('log')
    f1_ax2.legend(['low-freq wave','high-freq wave'])
    f1_ax2.set_xlabel('WaveVelocity(m/s)') 
    f1_ax2.set_ylabel('Probability') 
    f1_ax2.set_title('Histogram of WaveVelocity') 
    fig1.subplots_adjust(bottom=0.2)
    fig2.subplots_adjust(bottom=0.2)
    if show_flag:
        plt.show()
    return fig1, fig2


    # Spacial PhaseDiff and gradient
def spacial_phase_gradient(x,y,ct_sig, fs, band, stim_start, fast_response_channel, channel_list, bad_channel_list, pixel_spacing_x, pixel_spacing_y, Thresh, gridshape, n_mode, tt, show_gdirection=True, fig=None, show_flag=True):
    SVD_tc_data = ct_sig.swapaxes(0,1)
    period = SVD_tc_data.shape[2]

    Tamp = np.zeros((SVD_tc_data.shape[0],SVD_tc_data.shape[2],n_mode))
    sig = np.zeros((SVD_tc_data.shape[0],n_mode))
    most_resp_mode = np.zeros((SVD_tc_data.shape[0],),dtype=int)
    mostRespSPhase = np.zeros((SVD_tc_data.shape[0],SVD_tc_data.shape[1]))
    pd_trials = np.zeros((SVD_tc_data.shape[0],gridshape[0],gridshape[1],SVD_tc_data.shape[2]))
    

    for trial in range(SVD_tc_data.shape[0]):
        SVDout, SpatialAmp, SpatialPhase, TemporalAmp, TemporalPhase, = complexSVD(SVD_tc_data[trial],n_mode)
        Tamp[trial], sig[trial], most_resp_mode[trial] = TemporalImportance_Amp(TemporalAmp,stim_start,period,Thresh=Thresh,baselineEnd=0)
        # print(most_resp_mode[trial])
        mostRespSPhase[trial] = SpatialPhase[:,most_resp_mode[trial]]
        rec_a = SVDModeReconstruct(SVDout,most_resp_mode[trial])
        ft, signIF= instantaneous_frequency(rec_a,fs)
        rec_a_rct = reorgChannels(rec_a,channel_list,gridshape)
        # print(rec_a_rct.shape)
        pm,pd,dx,dy = phase_gradient_complex_multiplication(rec_a_rct,pixel_spacing_x,pixel_spacing_y,signIF)
        # print(pd.shape)
        pd_trials[trial] = pd

        # wave length and velocity
        # Spacial wavelength: reciprocal of spatial frequency  空间频率倒数
        # spatial frequency：梯度模值/2*pi
        # velocity：Spacial wavelength*temporal frequency

   
    # spacial phase gradient
    gradientDirection_array_tt = np.angle(np.mean(np.exp(1j*pd_trials[:,:,:,tt]),0))
    gradientDirection_var_array_tt = 1 - np.abs(np.mean(np.exp(1j*pd_trials[:,:,:,tt]),0))
    vec = gradientDirection_var_array_tt*np.exp(1j*gradientDirection_array_tt)
    # print(vec)
    

    AlignedAngles, AlignedVar, Pvals = mostRespSVDphaseDiff(mostRespSPhase,fast_response_channel)
    AlignedAngles_Gr = np.zeros(AlignedAngles.shape)
    AlignedVar_Gr = np.zeros(AlignedVar.shape)
    Pvals_Gr = np.zeros(Pvals.shape)

    for loc,id in enumerate(channel_list):
        AlignedAngles_Gr[loc] = AlignedAngles[id]
        AlignedVar_Gr[loc] = AlignedVar[id]
        Pvals_Gr[loc] = Pvals[id]
        if (id in bad_channel_list or Pvals[id]<0.0006):
            AlignedAngles_Gr[loc] = -float('inf')
            vec[loc//gridshape[1],loc%gridshape[1]]=0
    AlignedAngles_Gr = AlignedAngles_Gr.reshape(gridshape)
    AlignedVar_Gr = AlignedVar_Gr.reshape(gridshape)
    Pvals_Gr = Pvals_Gr.reshape(gridshape)
    # print(Pvals_Gr)
    # levels = np.arange(-np.pi, np.pi, 0.001)
    if fig==None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    ax_ = ax.pcolor(x-pixel_spacing_x/2,y-pixel_spacing_y/2,AlignedAngles_Gr,vmin=-np.pi, vmax=np.pi ,cmap='rainbow')
    ax.set_title(f'{band[0]}-{band[1]}Hz Phase Gridient')
    # ax.set_title('high-frequency Phase Gridient')
    fig.colorbar(ax_,ax = ax,ticks=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi],label='Phase')
    if show_gdirection:
        _, ax = plot_vector_field(x,y,vec,pixel_spacing_x,pixel_spacing_y,norm=True,ax=ax,show_flag=False)
    ax.invert_xaxis()
    ax.set_xlabel('AP(ms)')
    ax.set_ylabel('ML(ms)')

    if show_flag:
        plt.show()
    return fig, Pvals_Gr
    # # p值显示
    # plt.matshow(Pvals_Gr)
    # plt.title('Pvals')
    # plt.show()

def spacial_phase_diff(ct_sig, stim_start, channel_diff,Thresh,n_mode,band,fig=None,show_flag=True):
    # # spacial phase difference
    if fig==None:
        fig=plt.figure()
    
    SVD_tc_data = ct_sig.swapaxes(0,1)
    period = SVD_tc_data.shape[2]
    mostRespSPhase = np.zeros((SVD_tc_data.shape[0],SVD_tc_data.shape[1]))
    

    for trial in range(SVD_tc_data.shape[0]):
        SVDout, SpatialAmp, SpatialPhase, TemporalAmp, TemporalPhase, = complexSVD(SVD_tc_data[trial],n_mode)
        _, _, most_resp_mode = TemporalImportance_Amp(TemporalAmp,stim_start,period,Thresh=Thresh,baselineEnd=0)
        # print(most_resp_mode[trial])
        mostRespSPhase[trial] = SpatialPhase[:,most_resp_mode]


    bin_num = 20
    ph_dif = (mostRespSPhase[:,channel_diff[0]]-mostRespSPhase[:,channel_diff[1]])
    ph_dif[ph_dif<0] = ph_dif[ph_dif<0]+2*np.pi
    
    phaseDiff_pl_ax = fig.add_subplot(111,projection='polar')
    bars = phaseDiff_pl_ax.hist(ph_dif,bin_num,(0,2*np.pi))
    phaseDiff_pl_ax.set_title(f'{band[0]}-{band[1]}Hz Phase difference')
    fig.subplots_adjust(top=0.8)
    # phaseDiff_pl_ax.set_title('Phase difference(high-frequency)')
    if show_flag:
        plt.show()
    return fig

def SNR_plotting(x,y,SNR,chan_list,gridshape,fig=None,show_flag=True):
    SNR_Gr = np.zeros(SNR.shape)
    for loc,id in enumerate(chan_list):
        SNR_Gr[loc] = SNR[id]
    SNR_Gr = SNR_Gr.reshape(gridshape)
    # print(SNR_Gr)
    if fig==None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    ax_ = ax.pcolor(x,y,SNR_Gr,cmap='rainbow')
    ax.set_title(f'SNR(dB)')
    # ax.set_title('high-frequency Phase Gridient')
    fig.colorbar(ax_,ax = ax)
    ax.invert_xaxis()
    ax.set_xlabel('AP(ms)')
    ax.set_ylabel('ML(ms)')
    if show_flag:
        plt.show()
    return fig




