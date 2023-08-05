# -*- coding: UTF-8 -*-
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes
import platform

# void SNR_transient(const emxArray_real_T *ref, const emxArray_real_T *ref_noise,
#                    const emxArray_real_T *sig, double fs, double *SNR, double
#                    *noise_dB, double *err)


# void attackrelease_estimation(const emxArray_real_T *ref, const emxArray_real_T *
#   sig, double fs_ref, double fs_sig, double *time_attack, double *time_release,
#   double *err)
def cal_attack_release(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile,True)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile,True)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')

    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/attackrelease.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/attackrelease.dylib')
    if cur_paltform == 'linux':
        mydll = CDLL(sys.prefix + '/attackrelease.so')
    mydll.attackrelease_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double, POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    time_attack,time_release,err = c_double(0.0),c_double(0.0),c_double(0.0)
    mydll.attackrelease_estimation(byref(refstruct),byref(teststruct),c_double(refsamplerate),c_double(refsamplerate),byref(time_attack),byref(time_release),byref(err))

    if err.value == 0.0:
        return time_attack.value,time_release.value
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Documents\我的POPO\0\speech_attackrelease.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\0\speech_attackrelease.wav'
    print(cal_attack_release(refFile=file,testFile=test))
    pass