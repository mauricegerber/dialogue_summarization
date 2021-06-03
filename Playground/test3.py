import pandas as pd
import numpy as np


df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [1,7,5]]),
                   columns=['a', 'b', 'c'])
print(df)


def Nlargestelement(l, n):
    #l = list(l)
    Nlargestelement_list = []

    for i in range(0, n): 
        max_value = 0
        
        for j in range(len(l)):     
            if l[j] > max_value:
                max_value = l[j]
                
        l.remove(max_value)
        Nlargestelement_list.append(max_value)
    
    return min(Nlargestelement_list)

n_word_score = Nlargestelement(df["c"], 4)
print(n_word_score)