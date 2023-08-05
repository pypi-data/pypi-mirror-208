# -*- coding: UTF-8 -*-
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes


# void SNR_transient(const emxArray_real_T *ref, const emxArray_real_T *ref_noise,
#                    const emxArray_real_T *sig, double fs, double *SNR, double
#                    *noise_dB, double *err)

def cal_snr_transient(refFile=None, noisetFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile,True)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile,True)
    noiseStruct,noisesamplerate,_ = get_data_of_ctypes_(noisetFile,True)
    if refsamplerate != testsamplerate or refsamplerate!= noisesamplerate:
        raise TypeError('Different format of ref and test files!')

    import platform
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/snr_transient.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/snr_transient.dylib')

    mydll.SNR_transient.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double, POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    snr_1,snr_2,err = c_double(0.0),c_double(0.0),c_double(0.0)
    mydll.SNR_transient(byref(refstruct),byref(noiseStruct),byref(teststruct),c_double(refsamplerate),byref(snr_1),byref(snr_2),byref(err))

    if err.value == 0.0:
        return snr_1.value,snr_2.value
    else:
        return None


if __name__ == '__main__':
    print(sys.prefix)
    speech = r'C:\Users\vcloud_avl\Documents\我的POPO\nearend_ref.wav'
    noise = r'C:\Users\vcloud_avl\Documents\我的POPO\noise.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\3_noise_suppression_1655194712.wav'
    print(cal_snr_transient(refFile=speech,noisetFile=noise,testFile=test))

    pass