import word2vec
#from gensim.models import word2vec
import pandas as pd
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from textsplit.tools import get_segments
from textsplit.algorithm import split_greedy

def textsplit(transcript, language, max_splits=None, min_gain=None):

    text = ""
    utterance_breaks = [0]
    for utterance in transcript["Utterance"].str.lower():
        sentenced_utterance = sent_tokenize(utterance)
        utterance_breaks.append(utterance_breaks[-1] + len(sentenced_utterance))
        text += utterance + " "
    del utterance_breaks[0]

    if language == "english":
        wrdvec_path = "./functions/wrdvecs.bin"
    else:
        wrdvec_path = "./functions/wrdvecs_german.bin"
    model = word2vec.load(wrdvec_path)
    wrdvecs = pd.DataFrame(model.vectors, index=model.vocab)
    del model

    sentenced_text = sent_tokenize(text)
    vecr = CountVectorizer(vocabulary=wrdvecs.index)
    sentence_vectors = vecr.transform(sentenced_text).dot(wrdvecs)

    greedy_segmentation = split_greedy(sentence_vectors, penalty=min_gain, max_splits= max_splits)
    segmented_text = get_segments(sentenced_text, greedy_segmentation)
    lengths_optimal = [len(segment) for segment in segmented_text for sentence in segment]

    normalized_splits = [0]
    for split in greedy_segmentation.splits:
        diff = list(map(lambda ub: split - ub, utterance_breaks))
        smallest_positive_value_index = max([i for i in range(len(diff)) if diff[i] > 0])
        normalized_splits.append(smallest_positive_value_index+1)
    normalized_splits.append(len(transcript)-1)
    normalized_splits = list(set(normalized_splits))
    normalized_splits.sort()

    return normalized_splits, greedy_segmentation.splits, lengths_optimal