# void music_stability(const emxArray_real_T *ref, const emxArray_real_T *sig,
#                      double fs_ref, double fs_sig, double music_stability_ratio
#                      [1294], double *err)

# -*- coding: UTF-8 -*-
import sys,os
from os import  path

sys.path.append(os.path.dirname(path.dirname(__file__)))
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes

def cal_music_stablility(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile,True)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile,True)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')

    import platform
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/musicStability.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/musicStability.dylib')
    if cur_paltform == 'Linux':
        mydll = CDLL(sys.prefix + '/musicStability.so')
    mydll.music_stability.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double,POINTER(c_double),POINTER(c_double)]
    data_format = c_double*1294
    msr = data_format()
    err = c_double(0.0)
    mydll.music_stability(byref(refstruct),byref(teststruct),c_double(refsamplerate),c_double(refsamplerate),msr,byref(err))

    if err.value == 0.0:
        return msr
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Documents\我的POPO\0\music_stability.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\0\music_stability.wav'
    res = cal_music_stablility(refFile=file,testFile=test)
    for a in res:
        print(a)
    pass