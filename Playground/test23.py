import pandas as pd
import numpy as np
import math
df = pd.DataFrame({'A': [1, 2,3,4],
                   'B': [11, 12,13,14],
                   'C': [21, 22,33,44],
                   'D': [21, 22,33,44]})
#print(df.to_dict("split"))


dic = {"a": [1,2,3], "b":[4,5,6]}


myList = list(range(1,9))
myInt = 9
myList.reverse()
newList = [math.log(myInt / x) for x in myList]

print(newList)