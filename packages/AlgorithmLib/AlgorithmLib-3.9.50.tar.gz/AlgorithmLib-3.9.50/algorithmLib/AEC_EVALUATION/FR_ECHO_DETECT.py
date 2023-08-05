import ctypes,platform
import librosa
from ctypes import *
from formatConvert import pcm2wav

import sys
sys.path.append('../')
from commFunction import get_data_array,get_rms
from PCC.Pearson_CC import get_max_cc_by_dll
from scipy import signal
import numpy as np


def get_my_dll():
    """
    :return:
    """
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/pcc.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/pcc.dylib')
    if cur_paltform == 'Linux':
        mydll = CDLL(sys.prefix + '/pcc.so')
    return mydll


def cal_fullref_echo(reffile, testfile):
    """"""
    echoThreshold = 0.5
    target_fs = 8000
    framehLenth = int(0.2 * target_fs)
    frameshift = int(0.1 * target_fs)
    searchRange = int(1.8  * target_fs)
    lowf = 100
    hif = 7000
    #use_section = [[16.,18.74],[19.09,21.76],[22.13,24.64],[25.11,27.85],[28.32,31]]
    use_section = [[1.62, 3.84], [4.33, 6.8], [7.28, 10.2], [10.56, 13.23], [13.635, 16.57]]
    refdata,fs1,ch = get_data_array(reffile)
    testdata,fs2,ch = get_data_array(testfile)

    refdata = band_pass_filter(lowf,hif,refdata,fs1)
    testdata = band_pass_filter(lowf,hif,testdata,fs2)

    refdata = librosa.resample(refdata.astype(np.float32), orig_sr=fs1 ,target_sr=target_fs)

    testdata = librosa.resample(testdata.astype(np.float32), orig_sr=fs2 ,target_sr=target_fs)


    suspectItems = []

    for subsection in use_section:
        startpoint = int(target_fs * subsection[0])
        endpoint = int(target_fs * subsection[1])
        caltimes = (endpoint - startpoint-framehLenth) // frameshift
        for a in range(caltimes):
            relstart = startpoint+frameshift * a
            currefdata = refdata[relstart:relstart + framehLenth]
            curtestdata = testdata[relstart:relstart + framehLenth+searchRange]
            currefrms = get_rms(currefdata)
            curitem = [currefdata, curtestdata, relstart / target_fs,currefrms,relstart]
            suspectItems.append(curitem)
    for suspectitem in suspectItems:
        maxCoin, startpot = get_max_cc_by_dll(suspectitem[0], suspectitem[1], get_my_dll(), 3)
        refeng = suspectitem[3]
        testeng = get_rms(suspectitem[1][startpot:startpot+len((suspectitem[0]))])
        echoTime = (suspectitem[-1]+startpot)/target_fs
        srcTime = suspectitem[2]
        if maxCoin > echoThreshold and refeng > -45 and testeng > -35:
            print('An echo was detected at the {}-second mark of the file with a magnitude of {} dB.'.format(echoTime,
                                                                                                             testeng))
            return True
    return False

def band_pass_filter(lowfre,hifre,data,fs):
    f1 = lowfre  # 带通滤波器的下截止频率
    f2 = hifre  # 带通滤波器的上截止频率
    Wn = [f1 / (fs / 2), f2 / (fs / 2)]
    b, a = signal.butter(4, Wn, btype='band')  # 4阶Butterworth带通滤波器

    # 使用滤波器对信号进行滤波
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data
    # 绘制滤波前后的信号图像



if __name__ == '__main__':
    print('>>>>>>>>>>>>>')
    ref = 'src_bak.wav'
    test = 'pc_1.wav'
    cal_fullref_echo(pcm2wav(ref),pcm2wav(test))
    print('>>>>>>>>>>>>>')
    ref = 'src_bak.wav'
    test = 'pc_8.wav'
    cal_fullref_echo(pcm2wav(ref),pcm2wav(test))
    print('>>>>>>>>>>>>>')
    # ref = 'src_bak.wav'
    # test = '3.wav'
    # cal_fullref_echo(pcm2wav(ref),pcm2wav(test))
    # print('>>>>>>>>>>>>>')
    # ref = 'src_bak.wav'
    # test = '4.wav'
    # cal_fullref_echo(pcm2wav(ref), pcm2wav(test))
    # print('>>>>>>>>>>>>>')
    pass