
import ctypes
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
import wave
import  time
from commFunction import get_data_array,make_out_file
import numpy as np
import librosa

def resample(infile,target_amplerate,outfile=None):
    data,fs,ch = get_data_array(infile)
    print(data)
    if fs == target_amplerate:
        return infile

    refdata = librosa.resample(data.astype(np.float32), orig_sr=fs ,target_sr=target_amplerate)


    if outfile is None:
        outfile = infile[:-4] +'_' +str(target_amplerate) + '.wav'

    make_out_file(outfile,refdata,fs,ch)

    return outfile
    pass
# 多声道转1声道 采样率转换
def restruct(infile,target_amplerate,outfile=None):
    onechannelfile = infile
    data,fs,chn = get_data_array(infile)
    if fs == target_amplerate and chn == 1:
        return infile
    if chn != 1:
        onechannelfile = infile[:-4] + '_mono.wav'
        data =  np.array([data[n] for n in range(len(data)) if n%chn==0])
        wavfile = wave.open(onechannelfile, 'wb')
        wavfile.setnchannels(1)
        wavfile.setsampwidth(2)
        wavfile.setframerate(fs)
        wavfile.writeframes(data.tobytes())
        wavfile.close()
        time.sleep(1)
    #uint64_t Resample_s16(const int16_t *input, int16_t *output, int inSampleRate, int outSampleRate, uint64_t inputSize,uint32_t channels)

    return resample(onechannelfile,target_amplerate,outfile=outfile)
    pass

if __name__ == '__main__':
    dst = r'E:/02_ai_vad/aivad-seqs/Speech/T0055G0092S0001.wav'
    noise = r'E:/02_ai_vad/aivad-seqs/Noise/car_horn-1.wav'
    sam = 8000
    print(restruct(noise,sam,'1.wav'))
