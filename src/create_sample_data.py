import numpy as np
import pandas as pd
from helper_methods import get_descriptive_stats

n = 40

columns = ['Student ID', 'Quiz 1', 'Test 1', 'Final', 'Neighborhood', 'Race']
# Create data
data = np.ndarray(shape=(n, len(columns)), dtype='object')
# Student
data[:,0] = np.arange(0,n)
# Quiz 1
data[:,1] = np.random.normal(loc=30, scale=15, size=n)
# Test 1
data[:,2] = np.random.normal(loc=50, scale=8, size=n)
# Final
data[:,3] = np.random.normal(loc=57, scale=28, size=n)
# Neighborhood
neighborhoods = ['West Central', 'Logan', 'Riverside', 'Peaceful Valley', "Brown's Addition"]
data[:,4] = np.random.choice(neighborhoods, n)
# Race
races = ['White', 'Black', 'American Indian', 'Asian']
data[:,5] = np.random.choice(races, n)


# Create DataFrame
df = pd.DataFrame(
    columns = columns,
    data = data,
    dtype = 'object'
)


# Convert to float
numerical_cols = ['Quiz 1', 'Test 1', 'Final']
for numerical_col in numerical_cols:
    df[numerical_col] = df[numerical_col].astype('float')


# Quiz 1 score adjustments
df.loc[df['Race'] == races[0], 'Quiz 1'] = df.loc[df['Race'] == races[0], ['Quiz 1']].apply(lambda x: x - 20)

df.loc[df['Race'] == races[1],'Quiz 1'] = df.loc[df['Race'] == races[1], ['Quiz 1']].apply(lambda x: x + 15)

df.loc[df['Race'] == races[2],'Quiz 1'] = df.loc[df['Race'] == races[2], ['Quiz 1']].apply(lambda x: x + 50)

df.loc[df['Race'] == races[3],'Quiz 1'] = df.loc[df['Race'] == races[3],['Quiz 1']].apply(lambda x: x - 10)

df.loc[df['Neighborhood'] == neighborhoods[0], ['Quiz 1']] = 50

df.loc[df['Neighborhood'] == neighborhoods[1], ['Quiz 1']] = 30

df.loc[df['Neighborhood'] == neighborhoods[3], ['Quiz 1']] = 70


# Test 1 score adjustments
df[df['Race'] == races[3]]['Test 1'].update(df[df['Race'] == races[3]]['Test 1'].apply(lambda x: np.random.normal(loc=30, scale=2)))

df[df['Neighborhood'] == neighborhoods[0]]['Test 1'].update(df[df['Neighborhood'] == neighborhoods[0]]['Test 1'].apply(lambda x: x + 40))

df[df['Neighborhood'] == neighborhoods[1]]['Test 1'].update(df[df['Neighborhood'] == neighborhoods[1]]['Test 1'].apply(lambda x: x -  30))


# Final score adjustments
df[df['Race'] == races[0]]['Final'].update(df[df['Race'] == races[0]]['Final'].apply(lambda x: np.random.normal(loc=90, scale=2)))

df[df['Race'] == races[1]]['Final'].update(df[df['Race'] == races[1]]['Final'].apply(lambda x: np.random.normal(loc=70, scale=3)))

df[df['Race'] == races[2]]['Final'].update(df[df['Race'] == races[2]]['Final'].apply(lambda x: np.random.normal(loc=30, scale=1)))

df[df['Race'] == races[3]]['Final'].update(df[df['Race'] == races[3]]['Final'].apply(lambda x: np.random.normal(loc=10, scale=2)))

df[df['Neighborhood'] == neighborhoods[0]]['Final'].update(df[df['Neighborhood'] == neighborhoods[0]]['Final'].apply(lambda x: x -  30))

df[df['Neighborhood'] == neighborhoods[1]]['Final'].update(df[df['Neighborhood'] == neighborhoods[1]]['Final'].apply(lambda x: x -  10))

df[df['Neighborhood'] == neighborhoods[2]]['Final'].update(df[df['Neighborhood'] == neighborhoods[2]]['Final'].apply(lambda x: x +  30))

df[df['Neighborhood'] == neighborhoods[3]]['Final'].update(df[df['Neighborhood'] == neighborhoods[3]]['Final'].apply(lambda x: x +  10))


# Create Total
df['Total'] = df[['Quiz 1', 'Test 1', 'Final']].sum(axis=1)


# Rearrange columns
df = df[['Student ID', 'Quiz 1', 'Test 1', 'Final', 'Total', 'Neighborhood', 'Race']]


# Save data
filename = './example_data/example_data.csv'
df.to_csv(filename, index=False)


# Print to check
for group_var in ['Race', 'Neighborhood']:
    for measure_var in numerical_cols:
        print(f'\n\nGroup Var: {group_var}, Measure Var: {measure_var}')
        print(get_descriptive_stats(df=df, group_var=group_var, measure_var=measure_var))