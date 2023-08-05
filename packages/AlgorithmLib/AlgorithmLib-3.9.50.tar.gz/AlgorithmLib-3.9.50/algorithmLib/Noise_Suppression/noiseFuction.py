# -*- coding: utf-8 -*-
import sys,os
from os import  path

sys.path.append(os.path.dirname(path.dirname(__file__)))

from commFunction import get_rms,make_out_file,get_ave_rms
import numpy as np

from SNR_ESTIMATION.MATCH_SIG import match_sig
from commFunction import get_data_array
import scipy.signal as sg

speechSection = [12, 15]
noiseSection = [0, 10]
FRAME_LEN = 9600
frame_shift = 4800


def get_maxima(values:np.ndarray):
    """极大值"""
    max_index = sg.argrelmax(values)[0]
    return max_index,values[max_index]

def get_minima(values:np.ndarray):
    """极小值"""
    min_index = sg.argrelmin(values)[0]
    return min_index,values[min_index]


def get_data_pairs(srcFile=None,testFile=None):
    """
    Parameters
    ----------
    srcFile
    testFile
    Returns
    -------
    """

    samples = int(match_sig(refFile=srcFile, testFile=testFile))

    dataSrc, fs, chn = get_data_array(srcFile)
    dataTest, fs2, chn2 = get_data_array(testFile)

    print(dataTest,dataSrc,samples)
    assert fs == fs2
    assert  chn2 == chn
    assert samples > 0

    dataTest = dataTest[samples:]
    M,N = len(dataSrc),len(dataTest)
    targetLen = min(M,N)
    return dataSrc[:targetLen],dataTest[:targetLen],fs,chn


def cal_noise_converge(dataSrc,dataTest,fs,chn):
    """
    Parameters
    ----------
    dataSrc
    dataTest
    Returns
    -------
    """
    srcSpeechLevel = get_rms(dataSrc[fs*speechSection[0]:fs*speechSection[1]])
    curSpeechLevel = get_rms(dataTest[fs*speechSection[0]:fs*speechSection[1]])

    # log（V1 / V2) = X/20

    gain = np.power(10,(srcSpeechLevel - curSpeechLevel)/20)
    newData = dataTest.astype(np.float32) * gain
    make_out_file('source.wav', dataSrc.astype(np.int16), fs, chn)
    make_out_file('target.wav',newData.astype(np.int16),fs,chn)

    n_sengen = len(newData) // FRAME_LEN
    MAX_RMS = -120
    for a in range(n_sengen):
        curLevel = get_rms(newData[a*FRAME_LEN:(a+1)*FRAME_LEN])
        print(MAX_RMS,curLevel)
        if curLevel > MAX_RMS:
            MAX_RMS = curLevel
        if curLevel < MAX_RMS - 20:
            break
    converge = a * FRAME_LEN / fs

    nsLevel = get_ave_rms(dataSrc[int(converge * fs) :noiseSection[1]* fs]) - get_ave_rms(newData[int(converge * fs) :noiseSection[1]* fs])
    return converge, nsLevel
    #TODO 收敛时间
    #TODO 降噪量


def cal_noise_Supp(srcFile,testFile,nslabmode=False,start=0.2,end=15.8,noiseType='None'):
    """
    Parameters
    ----------
    data
    Returns
    -------
    """
    nosieVariable = {'bubble': 4, 'car': 4.5, 'restaurant': 7,'white':3,'traffic':4,'metro':3.5,'None':4}

    if nslabmode:
        #确定计算边界
        dataSrc, fs, chn = get_data_array(testFile)
        overallLen = len(dataSrc)
        lowTmp,upperTmp = 0,overallLen
        if start is None or start < 0.1:
            dataFloor = dataSrc[0:int(0.1*fs)]
            Floor = get_rms(dataFloor)

        else:
            #  计算src noise
            lowTmp = int(start * fs)
            dataFloor = dataSrc[0:lowTmp]
            Floor = get_rms(dataFloor)

        if end is None:
            dataDegrad = dataSrc[overallLen-fs:overallLen]
        else:
            upperTmp = int(end*fs)
            dataDegrad = dataSrc[int((end-2)*fs):upperTmp]
        Degrad = get_rms(dataDegrad)

        # 计算rms求最大值
        dataSrc = dataSrc[lowTmp:upperTmp]
        datanew = dataSrc.astype(np.float32)
        n_sengen = (len(datanew)-FRAME_LEN)//frame_shift
        MAX_RMS,maxindex,MIN_RMS,minindex = -120,0,0,0
        index = 0
        x,y = [],[]
        for a in range(n_sengen):
            index += 1
            curLevel = get_rms(datanew[a * frame_shift:a * frame_shift + FRAME_LEN])
            if curLevel > MAX_RMS:
                MAX_RMS = curLevel
                maxindex = index
            x.append(index*frame_shift/fs)
            y.append(curLevel)
        # 找到第一个拐点
        for i,curlel in enumerate(y):
            if i < maxindex:
                continue
            else:
                if curlel < MAX_RMS - nosieVariable[noiseType]/2-3:
                    break
        firindex = i
        firstconvertime = (i) * frame_shift / fs

        #计算先验噪声
        lastindex = (len(datanew) - 2 * fs)/frame_shift
        post = y[int(lastindex):]

        pre_std = np.std(post, ddof=1)

        #计算最小值
        index = 0
        for a in range(n_sengen):
            index += 1
            curLevel = get_rms(datanew[a * frame_shift:a * frame_shift + FRAME_LEN])
            if curLevel < MIN_RMS and index > firindex:
                MIN_RMS = curLevel
                minindex = index
        # 求极小值
        minimadex,minmavalue = get_minima(np.array(y))
        for a in range (len(minimadex)):
            if minmavalue[a] < MIN_RMS + 2 and minimadex[a] < minindex:
                MIN_RMS = minmavalue[a]
                minindex = minimadex[a]
                break
        #找到第二个拐点
        revers = y[::-1]
        for i,curlel in enumerate(revers):
            if  i < len(y)-minindex:
                continue
            if curlel > MIN_RMS + 2*pre_std:
                break
        secondConvertime = (len(y)-i) * frame_shift / fs
        #计算后验噪声
        postdata = y[int(len(y)-i):]
        post_std = np.std(postdata, ddof=1)
        post_Degrad  = get_rms(datanew[int(secondConvertime*fs):])
        noise_src = MAX_RMS - nosieVariable[noiseType] / 2
        post_src = get_rms(datanew[:int(firstconvertime*fs)])
        # print('firstconvertime  is {}'.format(firstconvertime))
        # print('secondConvertime  is {}'.format(secondConvertime))
        # print('prestd  is {}'.format(pre_std))
        # print('poststd  is {}'.format(post_std))
        # print('noise src is {}'.format(noise_src))
        # print('post noise src is {}'.format(post_src))
        # print('noise floor is {}'.format(Floor))
        # print('noise Degrad is {}'.format(Degrad))
        # print('post noise Degrad is {}'.format(post_Degrad))
        # print('ns gain is {}'.format(post_src-post_Degrad))


        # import matplotlib.pyplot as plt
        # plt.plot(x,y)
        # plt.show()
        return firstconvertime,secondConvertime,Floor,post_src,post_Degrad,post_std
    else:
        srcdata, dstdata, fs, chn = get_data_pairs(srcFile=srcFile, testFile=testFile)
        return  cal_noise_converge(srcdata,dstdata,fs,chn)


if __name__ == '__main__':
    src = 'car_noise_speech.wav'
    dst = 'speech_cn.wav'
    dst2 = 'mixDstFile3.wav'
    dur = cal_noise_Supp(src,dst2,nslabmode=True)
    print(dur)
    pass