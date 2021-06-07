import sys
import os
import word2vec
import pandas as pd

sys.path.insert(0, os.path.split(sys.path[0])[0])
path = sys.path[0]

corpus_path = "C:/Users/pasca/Downloads/deu_wikipedia_2016_300K/deu_wikipedia_2016_300K-sentences.txt"

wrdvec_path = path + "/wrdvecs_german.bin"


word2vec.word2vec(corpus_path, wrdvec_path, cbow=1, iter_=5, hs=1, threads=8, sample='1e-5', window=15, size=200, binary=1)

model = word2vec.load(wrdvec_path)
wrdvecs = pd.DataFrame(model.vectors, index=model.vocab) # dataframe with [71291 rows x 200 columns], row indices are words
del model
print(wrdvecs.shape)



