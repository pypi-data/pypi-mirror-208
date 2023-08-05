# -*- coding: UTF-8 -*-
import sys,os
from os import  path

sys.path.append(os.path.dirname(path.dirname(__file__)))
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes

# void gaintable_estimation(const emxArray_real_T *ref, const emxArray_real_T *sig,
#   double fs_ref, double fs_sig, double type, double gain_table[11], double DR[11],
#   double *limiter, double *err)

def cal_gain_table(refFile=None, testFile=None,targetType=0):
    '''
    Parameters
    ----------
    refFile
    testFile
    targetType  0:speech,1:music

    Returns
    -------

    '''
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile,True)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile,True)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')

    import platform
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/gaintable.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/gaintable.dylib')
    if cur_paltform == 'Linux':
        mydll = CDLL(sys.prefix + '/gaintable.so')
    mydll.gaintable_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double,c_double,POINTER(c_double),POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    data_format = c_double*11
    gain_table = data_format()
    DR = data_format()
    limiter,err = c_double(0.0),c_double(0.0)
    mydll.gaintable_estimation(byref(refstruct),byref(teststruct),c_double(refsamplerate),c_double(refsamplerate),c_double(targetType),gain_table,DR,byref(limiter),byref(err))

    if err.value == 0.0:
        return limiter.value,gain_table,DR
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Documents\我的POPO\0\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\0\speech_gaintable.wav'
    lim,gain_table,DR = cal_gain_table(refFile=file,testFile=test,targetType=0)
    print(lim,gain_table[0],DR[2])
    print(gain_table,DR)
    for a in gain_table:
        print(a)
    for a in DR:
        print(a)
    pass