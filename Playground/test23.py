import pandas as pd
import numpy as np
df = pd.DataFrame({'A': [1, 2,3,4],
                   'B': [11, 12,13,14],
                   'C': [21, 22,33,44],
                   'D': [21, 22,33,44]})
#print(df.to_dict("split"))



df_dict = {}
for column in df:
    df_dict[column] = list(df[column])
print(df_dict)