import pandas as pd

from keybert import KeyBERT


#transcript = pd.read_csv("C:\\Users\\basil\\myCloud\\01 Studium\\ZHAW\\Bachelor Wirtschaftsingenieurwesen\\6. Semester\\BA\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")
transcript = pd.read_csv("C:\\Users\\basil\\Documents\\summarization\\summarization\\Dash\\us_election_2020_vice_presidential_debate.csv")


kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
own_stop_words = {'\\', 'o', "needn't", "should've", 'ourselves', 'did', 'nor', 'this', "that'll", 'hers', 'for', ']', 'most', 'then', 'by', 'does', 
                    'after', 'so', '.', 'there', 'to', 'd', ')', 'that', 're', 'their', 'my', 'ours', 'hasn', 'doesn', "hadn't", 'yours', "isn't", 'what', 'with',
                    'between','#', '[', "won't", '-', '%', 'me', 'who', 'from', 'down', 'myself', 'mightn', "she's", 'we', 'before', 'mustn', 'once', '*', 'be',
                    'during', ';', 'up', 'no', 've', 'theirs', 'him', '~', 'll', 'under', '<', "hasn't", 'having', '}', 'has', 'm', 'shouldn', '!', '/', 'again',
                    'very', 'they', 'have', 'both', 'just', 'don', 'weren', 'wouldn', 'why', '"', "couldn't", 'doing', 'those', '^', "mustn't", "aren't", 'while',
                    ',', 'now', "you'd", 's', 'about', 'if', 'when', 'will', 'are', "'", 'should', 'all', 'had', 'itself', 'in', "you've", 'few', 'below', 'them',
                    'shan', 'the', 'it', 'which', 'was', 'wasn', 'its', "weren't", '(', '`', '�', '|', 'each', "haven't", 'any', 'y', 'an', "didn't", 'until',
                    'haven', 'on', 'you', 'over', 'here', 'how', "mightn't", '+', 'she', 'himself', 'as', 'more', 'same', "wouldn't", '@', 'her', 'themselves',
                    'because', 'is', 'couldn', 'own', 'but', 'can', '=', '{', ':', 'only', 'yourself', 'further', 'didn', 'being', 'his', 'some', "don't", 'such',
                    'i', 'into', '?', "shan't", 'he', 'these', 'other', "wasn't", 'yourselves', 'won', 'above', "shouldn't", 'do', 'whom', 'and', "you're",
                    'through', "it's", 'aren', 'needn', 'not', '>', 'isn', 'out', "doesn't", 'at', 'than', 'our', 'where', 't', 'been', 'of', 'or', 'were', 
                    'ain', 'ma', 'your', '&', '_', 'hadn', 'herself', "you'll", 'a', 'am', 'too', 'off', '$', 'against',
                    "trump", "thank", "biden", "joe", "donald"}

for j in range(len(transcript)):
    try:
        keywords = kw_extractor.extract_keywords(transcript["text"][j], keyphrase_ngram_range=(2,3), stop_words = own_stop_words, diversity=1, use_mmr=True)
        # Keyprhase range = min/max number of words. Smaller range = better performance
        # For using diversity parameter, use_mmr=True is needed
        # stop words = "english" or own set
        print(j,": ",keywords)
    except:
        print("empty")
