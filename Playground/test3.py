import sys
import os
import word2vec

sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]


wrdvec_path = path + "/Dash/functions/wrdvecs_german.bin"
corpus_path = "C:/Users/pasca/Downloads/enwiki_20180420_100d.txt"


word2vec.word2vec(corpus_path, wrdvec_path, cbow=1, iter_=5, hs=1, threads=8, sample='1e-5', window=15, size=200, binary=1)

