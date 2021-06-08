import string
import math
import pandas as pd

def tf_idf(data, steps):
    adj_punctuation = string.punctuation.replace("'", "")

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

    minutes_seq = range(0, l_min+steps+1, steps)
    minutes = minutes_seq[1:]
    
    uniqueWords = set()

    def tf(bagofwords):
        numofwords = dict.fromkeys(uniqueWords, 0)
        for word in bagofwords:
            numofwords[word] += 1

        # Compute TF
        tfDict = {}
        bagOfWordsCount = len(bagofwords)
        for word, count in numofwords.items():
            tfDict[word] = count / float(bagOfWordsCount)

        return numofwords, tfDict

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
    
    
    text = ""
    index_min = 0
    blocks = []
    list_of_bagofwords = []

    for i in range(nrow+1):
        t = data[i]["Utterance"]
        min_count = analyse_minute(data[i]["Time"])
     
        if min_count < minutes[index_min]:
            text += " " + t.lower()
            
        else:
            blocks.append([text])
            bagOfWords = text.translate(str.maketrans('', '', adj_punctuation)).split(' ')
            uniqueWords.update(set(bagOfWords))
            list_of_bagofwords.append(bagOfWords)
            index_min += 1
            text = data[i]["Utterance"].lower()
        
        if i == nrow:
            blocks.append([text])
            bagOfWords = text.translate(str.maketrans('', '', adj_punctuation)).split(' ')
            list_of_bagofwords.append(bagOfWords)
            uniqueWords.update(set(bagOfWords))
            

    list_of_numwords = []
    list_of_tfdicts = []
    for bag in list_of_bagofwords:
        numwords, tfdicts = tf(bag)
        list_of_numwords.append(numwords)
        list_of_tfdicts.append(tfdicts)

    # Compute IDF
    idfs = computeIDF(list_of_numwords)

    # Compute TF-IDF
    list_of_tfidf = []
    for dictionary in list_of_tfdicts:
        tfidf = {}
        for word, val in dictionary.items():
            tfidf[word] = val * idfs[word]
        list_of_tfidf.append(tfidf)
    
    df_tf = pd.DataFrame(list_of_tfdicts)
    df_idf = pd.DataFrame([idfs])
    df_tfidf = pd.DataFrame(list_of_tfidf)

    # for i in range(len(df.columns)):
    #     for j in range(len(df)):
    #         if df.iloc[j][i] > 0.015:
    #             print(df.columns[i], df.iloc[j][i])


    tf_dict = {}
    for column in df_tf:
        tf_dict[column] = list(df_tf[column])
    
    idf_dict = {}
    for column in df_idf:
        idf_dict[column] = list(df_idf[column])

    tfidf_dict = {}
    for column in df_tfidf:
        tfidf_dict[column] = list(df_tfidf[column])

    return tf_dict, idf_dict, tfidf_dict, minutes_seq