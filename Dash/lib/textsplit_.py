import word2vec
import pandas as pd
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from textsplit.tools import get_penalty, get_segments
from textsplit.algorithm import split_optimal

def textsplit(transcript, segment_len=30):

    text = ""
    utterance_breaks = [0]
    for utterance in transcript["Utterance"].str.lower():
        sentenced_utterance = sent_tokenize(utterance)
        utterance_breaks.append(utterance_breaks[-1] + len(sentenced_utterance))
        text += utterance + " "
    del utterance_breaks[0]

    wrdvec_path = "./lib/wrdvecs.bin"
    model = word2vec.load(wrdvec_path)
    wrdvecs = pd.DataFrame(model.vectors, index=model.vocab)
    del model

    sentenced_text = sent_tokenize(text)
    vecr = CountVectorizer(vocabulary=wrdvecs.index)
    sentence_vectors = vecr.transform(sentenced_text).dot(wrdvecs)
    penalty = get_penalty([sentence_vectors], segment_len)

    optimal_segmentation = split_optimal(sentence_vectors, penalty, seg_limit=250)
    segmented_text = get_segments(sentenced_text, optimal_segmentation)
    lengths_optimal = [len(segment) for segment in segmented_text for sentence in segment]

    normalized_splits = [0]
    for split in optimal_segmentation.splits:
        diff = list(map(lambda ub: split - ub, utterance_breaks))
        smallest_positive_value_index = max([i for i in range(len(diff)) if diff[i] > 0])
        normalized_splits.append(smallest_positive_value_index+1)
    normalized_splits.append(len(transcript)-1)
    normalized_splits = list(set(normalized_splits))
    normalized_splits.sort()

    return normalized_splits, optimal_segmentation.splits, lengths_optimal