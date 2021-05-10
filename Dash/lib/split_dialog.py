from nltk.corpus import stopwords, wordnet
from textblob import TextBlob
import nltk
from collections import Counter
import string
import re
import math
adj_punctuation = string.punctuation.replace("'", "")

def split_dialog(data, steps, use_all=True, n=15):
    
    def analyse_minute(timestamp):
        minute = 0
        if len(timestamp) > 5:
            minute = 60 * int(timestamp[0:timestamp.find(":",0,len(timestamp))])
            timestamp = timestamp[timestamp.find(":",0,len(timestamp))+1:]
            
        minute += int(timestamp[0:timestamp.find(":",0,len(timestamp))])
        return(minute)
    
    nrow = len(data)-1
    last_min = data[nrow]["Time"]
    l_min = analyse_minute(last_min)

    minutes_seq = range(0, l_min+steps, steps)
    minutes = minutes_seq[1:]
    
    

    def eliminate_stopwords(text):
        # stop_words = set(stopwords.words("english"))
        # stop_words |= set(["Thank", "Joe", "Biden", "Donald", "Trump", "America", "American", "President", "Harris", "I'm", "would", "know", "we're", "one", "two", "three", "four", 
        # "first", "said", "going", "say", "think", "go", "made"])
        # sw_lower = [each_string.lower() for each_string in stop_words]
        # text_sp = text.split()

        # words_small = [each_string.lower() for each_string in text_sp]
        # words = [x for x in words_small if x not in sw_lower]
        
        sw = ["i", "rei", "k.", "okay", "hi", "president"]
        # words = TextBlob(text)
        # print(words)

        sentences = nltk.sent_tokenize(text) #tokenize sentences
        nouns = [] #empty to array to hold all nouns

        for sentence in sentences:
            for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                    nouns.append(word)
        nouns_filtered = [x for x in nouns if x not in sw]
        
        return nouns_filtered
    
    
    # def tf(text, index_min):
    #     bagOfWords = text.translate(str.maketrans('', '', adj_punctuation)).split(' ')
    #     uniqueWords.update(set(bagOfWords))
        
    #     numofwords = dict.fromkeys(uniqueWords, 0)
    #     for word in bagOfWords:
    #         numofwords[word] += 1
    #     print("asdfa")
    #     # Compute TF
    #     tfDict = {}
    #     bagOfWordsCount = len(bagOfWords)
    #     for word, count in numofwords.items():
    #         tfDict[word] = count / float(bagOfWordsCount)

    #     return numofwords, tfDict


    text = ""
    index_min = 0
    text_data = []

    counts = {}
    all_unique_words = set()
    
    # uniqueWords = set()
    # list_of_numwords = []
    # list_of_tfdicts = []
    blocks = []
    
    for i in range(nrow+1):
        t = data[i]["Utterance"]
        min_count = analyse_minute(data[i]["Time"])

        if min_count < minutes[index_min]:
            text += " " + t.lower()
            
        else:
            words = eliminate_stopwords(text)

            all_unique_words.update(set(words))

            for unique_word in all_unique_words:
                if unique_word not in counts:
                    counts[unique_word] = [0] * len(minutes)
            
            for word in words:
                counts[word][index_min] += 1

            counts_all = Counter(words)
            
            if not use_all:
                counts_n = dict()
                for key, value in counts_all.most_common(n):
                    counts_n[key] = value
            else:
                counts_n = counts_all
            
            blocks.append(text)
            # numwords, tfdicts = tf(text, index_min)
            # list_of_numwords.append(numwords)
            # list_of_tfdicts.append(tfdicts)
            text_data.append(counts_n)
            index_min += 1
            text = data[i]["Utterance"].lower()

        if i == nrow:
            words = eliminate_stopwords(text)

            all_unique_words.update(set(words))

            for unique_word in all_unique_words:
                if unique_word not in counts:
                    counts[unique_word] = [0] * len(minutes)
            
            for word in words:
                counts[word][index_min] += 1

            counts_all = Counter(words)
            
            if not use_all:
                counts_n = dict()
                for key, value in counts_all.most_common(n):
                    counts_n[key] = value
            else:
                counts_n = counts_all
            
            blocks.append(text)
            # numwords, tfdicts = tf(text, index_min)
            # list_of_numwords.append(numwords)
            # list_of_tfdicts.append(tfdicts)

            text_data.append(counts_n)
    

    def computeTF(wordDict, bagOfWords):
        tfDict = {}
        bagOfWordsCount = len(bagOfWords)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bagOfWordsCount)
        return tfDict

    uniqueWords = set()
    bagofwords_list = []
   

    for block in blocks:
        bagofwords = block.translate(str.maketrans('', '', adj_punctuation)).split(' ')
        bagofwords.append(bagofwords)
        uniqueWords.update(set(bagofwords))

    numofwords_list = []
    for dic in bagofwords_list:
        numofwords = dict.fromkeys(uniqueWords, 0)
        for word in dic:
            numofwords[word] += 1
        computeTF(numofwords, dic)
        numofwords_list.append(numofwords)



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
    
    idfs = computeIDF(numofwords_list)


    # Compute TF-IDF
    list_of_tfidf = []
    for dictionary in list_of_tfdicts:
        tfidf = {}
        for word, val in dictionary.items():
            tfidf[word] = val * idfs[word]
        list_of_tfidf.append(tfidf)
    
    df = pd.DataFrame(list_of_tfidf)

    tfidf_dict = {}
    for column in df:
        tfidf_dict[column] = df[column]
    print(tfidf_dict)
    return text_data, minutes_seq, counts, tfidf_dict