import ctypes,os,platform
import sys,librosa
from ctypes import *
from formatConvert import pcm2wav
import numpy as np
import sys,os
from os import  path
sys.path.append('../')
from commFunction import get_data_array
from PCC.Pearson_CC import get_max_cc_by_dll




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


def cal_fine_delay(reffile, testfile,targetfs=8000):
    """"""
    delaysearchRange = 4
    delayThreshhold = 0.3
    single_frame_size = 1
    refdata,fs,ch = get_data_array(reffile)
    testdata,fs,ch = get_data_array(testfile)
    refdata = librosa.resample(refdata.astype(np.float32), orig_sr=fs ,target_sr=targetfs)

    testdata = librosa.resample(testdata.astype(np.float32), orig_sr=fs ,target_sr=targetfs)


    cal_len = min(len(refdata),len(testdata))

    caltimes = (cal_len - (delaysearchRange + single_frame_size) * targetfs) // (single_frame_size * targetfs)
    caltimes = int(caltimes)
    print(caltimes)
    assert  caltimes > 0
    cc_list = []
    for times in range(caltimes):
        start = int(times * single_frame_size * targetfs)
        srcblock = refdata[start:start + single_frame_size*targetfs]
        dstbloack = testdata[start:start + (single_frame_size+delaysearchRange)*targetfs]
        maxCoin, startPoint = get_max_cc_by_dll(srcblock, dstbloack, get_my_dll(), 3)
        if maxCoin > delayThreshhold:
            cc_list.append(round((startPoint / 8000) * 1000, 2))
    if len(cc_list) == 0:
        return  4000
    else:
        return sum(cc_list)/len(cc_list)

if __name__ == '__main__':
       ref = '1.wav'
       test = '2.wav'
       cal_fine_delay(pcm2wav(ref),pcm2wav(test),48000)
       pass