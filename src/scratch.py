import pandas as pd

data = {'one': [0,1,1,2], 'two':[2,3,4,3]}
df = pd.DataFrame(data=data)

print('Original df')
print(df)

df.loc[df['one'] == 1, ['two']] = df.loc[df['one'] == 1, ['two']].apply(lambda x: x + 1)

print('New df')
print(df)