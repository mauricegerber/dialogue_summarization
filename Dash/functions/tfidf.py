import string
import math
from nltk.tokenize import word_tokenize
import pandas as pd

# based on https://towardsdatascience.com/natural-language-processing-feature-engineering-using-tf-idf-e8b9d00e7e76

def tfidf(documents):

    def computeTF(wordDict, bagOfWords):
        tfDict = {}
        bagOfWordsCount = len(bagOfWords)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bagOfWordsCount)
        return tfDict

    def computeIDF(documents):
        N = len(documents)
        idfDict = dict.fromkeys(documents[0].keys(), 0)
        for document in documents:
            for word, val in document.items():
                if val > 0:
                    idfDict[word] += 1
        
        for word, val in idfDict.items():
            idfDict[word] = math.log(N / float(val))
        return idfDict

    def computeTFIDF(tfBagOfWords, idfs):
        tfidf = {}
        for word, val in tfBagOfWords.items():
            tfidf[word] = val * idfs[word]
        return tfidf

    bagOfWords = [word_tokenize(document.translate(str.maketrans("", "", string.punctuation))) for document in documents]

    uniqueWords = set([word for document in bagOfWords for word in document])

    numOfWords = []
    for i in range(len(documents)):
        numOfWords.append(dict.fromkeys(uniqueWords, 0))
        for word in bagOfWords[i]:
            numOfWords[i][word] += 1

    tf = []
    for i in range(len(documents)):
        tf.append(computeTF(numOfWords[i], bagOfWords[i]))

    idf = computeIDF(numOfWords)

    tfidf = []
    for i in range(len(documents)):
        tfidf.append(computeTFIDF(tf[i], idf))

    df = pd.DataFrame(tfidf)

    return df.transpose()