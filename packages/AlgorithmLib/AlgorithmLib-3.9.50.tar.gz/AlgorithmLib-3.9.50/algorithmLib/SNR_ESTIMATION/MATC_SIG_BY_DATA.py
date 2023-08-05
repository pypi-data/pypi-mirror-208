# -*- coding: UTF-8 -*-
import copy
import sys
import time
import sys,os
from os import  path

sys.path.append(os.path.dirname(path.dirname(__file__)))
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_from_datablock,get_data_array,get_none_data_of_ctypes_
import  ctypes
import numpy as np

# DLL_EXPORT void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type,emxArray_real_T *sig_out, double *delay, double *err)


# void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type, emxArray_real_T *sig_out, double *delay, double
#                 *err)

# void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type, emxArray_real_T *sig_out, double *delay, double
#                 *err)

def match_sig(refData=None,testData=None,refsamplerate=48000):
    """
    Parameters
    ----------
    refFile
    testFile
    outFile
    audioType  0:speech,1:music

    Returns
    -------

    """
    assert len(refData) == len(testData)
    nframes = len(refData)
    print(time.time())
    refstruct = get_data_of_ctypes_from_datablock(refData,nframes)
    print(time.time())
    teststruct = get_data_of_ctypes_from_datablock(testData,nframes)
    print(time.time())
    outStruct = get_none_data_of_ctypes_(nframes)

    import platform
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/matchsig.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/matchsig.dylib')

    mydll.matchsig_2.argtypes = [POINTER(emxArray_real_T), POINTER(emxArray_real_T), POINTER(emxArray_real_T),c_double,c_double,
                                     POINTER(c_double), POINTER(c_double)]
    delay, err = c_double(0.0), c_double(0.0)
    print(time.time())
    mydll.matchsig_2(byref(refstruct), byref(teststruct), byref(outStruct),c_double(refsamplerate),c_double(0),byref(delay), byref(err))
    print(time.time())
    if err.value > 0.0:
        return None
    else:
        return delay.value




if __name__ == '__main__':
    ref = r'C:\Users\vcloud_avl\Documents\我的POPO\src.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\test.wav'
    refdata,fs,ch = get_data_array(ref)
    testdata,fs,ch = get_data_array(test)
    testdata = testdata[:96000]
    refdata = refdata[:96000]
    print(time.time())
    print(match_sig(refData=refdata, testData=testdata))
    print(time.time())
    print(np.corrcoef(refdata,testdata))
    print(time.time())
    pass