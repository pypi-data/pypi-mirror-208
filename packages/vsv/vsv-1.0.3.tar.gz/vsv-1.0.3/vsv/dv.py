import numpy as np
import librosa
from sklearn.metrics.pairwise import cosine_similarity
def gen_vsv_vector(audio_file):
    audio, sr = librosa.load(audio_file, sr=48000)
    frame_length = int(sr * 0.025)  # 25 ms
    hop_length = int(sr * 0.010)  # 10 ms
    n_fft = 512
    n_mels = 40
    n_components = 10

    

    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft,hop_length=hop_length, n_mels=n_mels)
    S = np.log(S + 1e-9)
    delta = librosa.feature.delta(S, width=3)
    delta_delta = librosa.feature.delta(S, order=2, width=3)
    features = np.concatenate((S, delta, delta_delta), axis=0)
    cov = np.cov(features)
    
    U, s, Vh = np.linalg.svd(cov)
    A = np.dot(np.dot(U, np.diag(np.sqrt(s))), U.T)
    x = np.mean(features, axis=1)
    d=np.dot(A, U.T)
    d = np.dot(np.dot(A, U.T), (x))
    return d

def CalcCS(embedd1, embedd2):
    return cosine_similarity(embedd1, embedd2)