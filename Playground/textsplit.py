import os
import word2vec
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import string

base_path = "C:/Users/pasca/myCloud/01 Studium/ZHAW/Bachelor Wirtschaftsingenieurwesen/6. Semester/BA/summarization/Playground"

transcript = pd.read_csv(
    filepath_or_buffer=base_path + "/Merge experiment.csv",
    header=0,
    names=["Speaker", "Time", "End time", "Duration", "Utterance"],
    usecols=["Speaker", "Time", "Utterance"]
)

text = ""
for utterance in transcript["Utterance"].str.lower():
    text += utterance

corpus_path = base_path + './text8'  # be sure your corpus is cleaned from punctuation and lowercased
# print(corpus_path)
# if not os.path.exists(corpus_path):
#     !wget http://mattmahoney.net/dc/text8.zip
#     !unzip {corpus_path}

links = {'tale2cities': 'https://www.gutenberg.org/files/98/98-0.txt',  # a tale of two cities
         'siddartha': 'http://www.gutenberg.org/cache/epub/2500/pg2500.txt'}  # siddartha

for link in links.values():
    text_path = os.path.basename(link)
    # print(text_path)
    # if not os.path.exists(text_path):
    #     !wget {link}

wrdvec_path = base_path + './wrdvecs.bin'
if not os.path.exists(wrdvec_path):
    word2vec.word2vec(corpus_path, wrdvec_path, cbow=1, iter_=5, hs=1, threads=8, sample='1e-5', window=15, size=200, binary=1)

model = word2vec.load(wrdvec_path)
wrdvecs = pd.DataFrame(model.vectors, index=model.vocab)
del model
print(wrdvecs.shape)

from textsplit.tools import SimpleSentenceTokenizer
sentence_tokenizer = SimpleSentenceTokenizer()

from textsplit.tools import get_penalty, get_segments
from textsplit.algorithm import split_optimal, split_greedy, get_total

# link = links['siddartha']
link = links['tale2cities']
segment_len = 30  # segment target length in sentences
book_path = os.path.basename(link)
print(book_path)

# with open(base_path + "/" + book_path, 'rt', encoding="utf8") as f:
#     text = f.read()  #.replace('\n', ' ')  # punkt tokenizer handles newlines not so nice

sentenced_text = sentence_tokenizer(text)
# print(sentenced_text)

# print(sentenced_text)
vecr = CountVectorizer(vocabulary=wrdvecs.index)
# print(vecr)

sentence_vectors = vecr.transform(sentenced_text).dot(wrdvecs)

penalty = get_penalty([sentence_vectors], segment_len)
print('penalty %4.2f' % penalty)

penalty = penalty * 3

optimal_segmentation = split_optimal(sentence_vectors, penalty, seg_limit=250)
segmented_text = get_segments(sentenced_text, optimal_segmentation)

print('%d sentences, %d segments, avg %4.2f sentences per segment' % (
    len(sentenced_text), len(segmented_text), len(sentenced_text) / len(segmented_text)))

with open(base_path + "/" + book_path + '.seg', 'wt', encoding="utf8") as f:
    for i, segment_sentences in enumerate(segmented_text):
        segment_str = ' // '.join(segment_sentences)
        gain = optimal_segmentation.gains[i] if i < len(segmented_text) - 1 else 0
        segment_info = ' [%d sentences, %4.3f] ' % (len(segment_sentences), gain) 
        print(segment_str + '\n8<' + '=' * 30 + segment_info + "=" * 30, file=f)

greedy_segmentation = split_greedy(sentence_vectors, max_splits=len(optimal_segmentation.splits))
greedy_segmented_text = get_segments(sentenced_text, greedy_segmentation)
lengths_optimal = [len(segment) for segment in segmented_text for sentence in segment]
lengths_greedy = [len(segment) for segment in greedy_segmented_text for sentence in segment]
plt.plot(range(len(lengths_optimal)), lengths_optimal)
plt.plot(range(len(lengths_greedy)), lengths_greedy)


# df = pd.DataFrame({'greedy':lengths_greedy, 'optimal': lengths_optimal})
# df.plot.line(figsize=(18, 3), title='Segment lenghts over text')
# df.plot.hist(bins=30, alpha=0.5, figsize=(10, 3), title='Histogram of segment lengths')

totals = [get_total(sentence_vectors, seg.splits, penalty) 
          for seg in [optimal_segmentation, greedy_segmentation]]
print('optimal score %4.2f, greedy score %4.2f' % tuple(totals))
print('ratio of scores %5.4f' % (totals[0] / totals[1]))
plt.show()