# -*- coding: UTF-8 -*-
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
import ctypes
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_

# void SNR_estimation(const emxArray_real_T *ref, const emxArray_real_T *sig,
#                     double fs, double *SNR, double *err)


def cal_snr_music(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile,False)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile,False)
    if refsamplerate != testsamplerate:
        raise TypeError('Different format of ref and test files!')

    import platform
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/snr_music.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/snr_music.dylib')

    mydll.SNR_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double, POINTER(c_double),POINTER(c_double)]
    snr,err = c_double(0.0),c_double(0.0)
    mydll.SNR_estimation(byref(refstruct),byref(teststruct),c_double(refsamplerate),byref(snr),byref(err))

    if err.value == 0.0:
        return snr.value
    else:
        return None

if __name__ == '__main__':
    cal_snr_music(refFile='speech.wav',testFile='music_rap.wav')
    pass