from nltk.corpus import stopwords, wordnet
from textblob import TextBlob
import nltk
from collections import Counter


def split_dialog(data, steps):
    
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
        
        sw = ["i", "rei", "k.", "okay"]
        # words = TextBlob(text)
        # print(words)

        sentences = nltk.sent_tokenize(text) #tokenize sentences
        nouns = [] #empty to array to hold all nouns

        for sentence in sentences:
            for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                    nouns.append(word)
        nouns_filtered = [x for x in nouns if x not in sw]
        
        return nouns_filtered
    
    text = ""
    text_old = ""
    index_min = 0
    text_data = []
    
    for i in range(nrow+1):
        t = data[i]["Utterance"]
        min_count = analyse_minute(data[i]["Time"])

        if min_count < minutes[index_min]:
            text += " " + t.lower()
            
        else:
            words = eliminate_stopwords(text)
            counts = Counter(words)
            text_data.append(counts)
            index_min += 1
            text = data[i]["Utterance"]

        if i == nrow:
            words = eliminate_stopwords(text)
            counts = Counter(words)
            text_data.append(counts)
   
    return text_data, minutes_seq