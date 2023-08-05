import numpy as np
import librosa
from sklearn.metrics.pairwise import cosine_similarity

def custom_func(audio_file):
    print("1.mfcc\n2.mfcc_delta\n3.mfcc_double_delta\n4.delta_double_delta\n5.delta\n6.double_delta")
    print("Enter your Option:")
    n=int(input())
    if n==1:
        return mfcc(audio_file)
    elif n==2:
        return mfcc_delta(audio_file)
    elif n==3:
        return mfcc_double_delta(audio_file)
    elif n==4:
        return delta_double_delta(audio_file)
    elif n==5:
        return delta(audio_file)
    elif n==6:
        return double_delta(audio_file)




def mfcc(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    cov = np.cov(S)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(S, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def mfcc_delta(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta = librosa.feature.delta(S, width=3)
    # delta_delta = librosa.feature.delta(S, order=2, width=3)
    features = np.concatenate((S, delta), axis=0)
    cov = np.cov(features)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(features, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def mfcc_double_delta(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta_delta = librosa.feature.delta(S, order=2, width=3)
    features = np.concatenate((S, delta_delta), axis=0)
    cov = np.cov(features)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(features, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def delta_double_delta(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta = librosa.feature.delta(S, width=3)
    delta_delta = librosa.feature.delta(S, order=2, width=3)
    features = np.concatenate((delta, delta_delta), axis=0)
    cov = np.cov(features)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(features, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def delta(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta = librosa.feature.delta(S, width=3)
    cov = np.cov(delta)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(delta, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def double_delta(audio_file):
    speaker_name = (audio_file.split('/')[-1]).split('.')[0]
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta_delta = librosa.feature.delta(S, order=2, width=3)
    cov = np.cov(delta_delta)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(delta_delta, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d