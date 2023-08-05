# coding=utf-8
import numpy as np

import librosa
import soundfile as sf

import math


def histogram_calculation(x=None, N=None, K=None):
    '''
    x:   audio samples
    N:   number of audio sample
    K:   bins of histogram
    '''
    x_max = np.max(x)
    x_min = np.min(x)
    denorm = x_max - x_min
    H = np.zeros(shape=[K, ], dtype=np.int32)
    for n in range(N):
        y = (x[n] - x_min) / denorm
        k = int(K * y)
        if k < K:
            H[k] = H[k] + 1
        else:
            H[k - 1] = H[k - 1] + 1
    return H


def clipping_coefficient_calculation(H=None, K=None):
    '''
    '''
    kl = 0
    kr = K - 1
    denorm = K - 1
    yl0 = H[kl]
    yr0 = H[kr]
    dl, dr = 0, 0
    Dmax = 0

    # # modify0
    # while kr > K//2:
    #     kr = kr - 1
    #     if H[kr] < yr0:
    #         dr = dr + 1
    #     else:
    #         break
    #     Dmax = np.maximum(Dmax, dr)
    # while kl < K//2:
    #     kl = kl + 1
    #     if H[kl] < yl0:
    #         dl = dl + 1
    #     else:
    #         break
    #     Dmax = np.maximum(Dmax, dl)
    # Rcl = 2*Dmax/denorm

    # while kr > kl:
    #     kl = kl + 1
    #     kr = kr - 1
    #     if H[kl] <= yl0:
    #         dl = dl + 1
    #     else:
    #         yl0 = H[kl]
    #         dl = 0
    #     if H[kr] <= yr0:
    #         dr = dr + 1
    #     else:
    #         yr0 = H[kr]
    #         dr = 0
    #     Dmax = np.maximum(Dmax, np.maximum(dl, dr))
    # Rcl = 2*Dmax/denorm
    # return Rcl

    # modify1
    index_l = 0
    index_r = K - 1
    dl_list = []  # [ [index, d, H[index] ]  ... ]
    dr_list = []
    while kr > kl:
        kl = kl + 1
        kr = kr - 1
        if H[kl] <= yl0:
            dl = dl + 1
        else:
            dl_list.append([index_l, dl, H[index_l]])
            index_l = kl
            yl0 = H[kl]
            dl = 0
        if H[kr] <= yr0:
            dr = dr + 1
        else:
            dr_list.append([index_r, dr, H[index_r]])
            index_r = kr
            yr0 = H[kr]
            dr = 0
        Dmax = np.maximum(Dmax, np.maximum(dl, dr))
    Rcl = 2 * Dmax / denorm

    dl_list.append([index_l, dl, H[index_l]])
    dr_list.append([index_r, dr, H[index_r]])
    list_all = []
    list_all.extend(dl_list)
    list_all.extend(dr_list)
    list_all.sort(key=lambda x: x[1], reverse=True)

    Dmax_index = list_all[0][0]
    Dmax_samples = list_all[0][2]

    # if Rcl >= 0.9:
    # print(list_all)
    # print('Dmax:')
    # print(Dmax)
    # print('Dmax index:')
    # print(list_all[0][0])
    # print('Dmax H[index]:')
    # print(list_all[0][2])
    # print('Rcl:')
    # print(Rcl)
    # print()

    return Rcl, Dmax_index, Dmax_samples


def get_rms(data=None):
    rms = math.sqrt(sum([x * x for x in data]) / len(data))
    dBrmsValue = 20 * math.log10(rms + 1.0E-6)
    return dBrmsValue



def clip_detect(audio_data=None, sr=None):
    '''
    audio_data:   audio samples    float [-1,1)
    sr:           sample_rate
    '''

    t = 30  # detect period /ms
    N = int(sr * t / 1000)  # number of audio sample in a detect unit
    K = 200  # number of histogram bins
    audio_piece = len(audio_data) // N  # 4000 samples one detect unit
    Rcl_list = []
    clipping_flag_list = []
    for i in range(audio_piece):
        audio_slice = audio_data[i * N:(i + 1) * N]

        dBrms = get_rms(audio_slice)  # 排除底噪段
        if dBrms < -50:
            Rcl_list.append(0)
            clipping_flag_list.append(0)
            continue

        x_max = np.max(audio_slice)  # 避免 histogram_calculation 中分母为零
        x_min = np.min(audio_slice)
        if x_max == x_min:
            Rcl_list.append(0)
            clipping_flag_list.append(0)
            continue

        H = histogram_calculation(x=audio_slice, N=N, K=K)
        Rcl, Dmax_index, Dmax_samples = clipping_coefficient_calculation(H=H, K=K)  # Rcl: ratio of clipping
        Rcl_list.append(Rcl)

        # Rcl ratio towards clipping_flag (0/1)
        if Rcl >= 0.9 and Dmax_samples > 4 * N / K:  # clipping detection flag
            Rcl = 1
        else:
            Rcl = 0

        clipping_flag_list.append(Rcl)

    clipping_ratio = np.zeros(shape=[len(audio_data), ], dtype=np.float32)
    clipping_detect_flag = np.zeros(shape=[len(audio_data), ], dtype=np.float32)
    for i in range(audio_piece):
        clipping_ratio[i * N:(i + 1) * N] = Rcl_list[i] * 10000 / 32768
        clipping_detect_flag[i * N:(i + 1) * N] = clipping_flag_list[i] * 10000 / 32768
    return sum(clipping_flag_list)/len(clipping_flag_list)
def cal_clip_index(testFile=None):
    """
    Parameters
    ----------
    testFile
    Returns
    -------

    """
    audio_data, sr = librosa.load(testFile, sr=None)  # float [-1,1)
    return clip_detect(audio_data=audio_data, sr=sr)

if __name__ == '__main__':

    clipindex = cal_clip_index('mixDstFile.wav')
    print(clipindex)