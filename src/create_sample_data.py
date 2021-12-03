import numpy as np
import pandas as pd

n = 40

columns = ['Student ID', 'Quiz 1', 'Assignment 1', 'Quiz 2', 'Final', 'Race', 'Neighborhood']
data = np.ndarray(shape=(n, len(columns)), dtype='object')
#data = np.zeros(shape=(n, len(columns)))
# Student
data[:,0] = np.arange(0,n)
# Quiz 1
data[:,1] = np.random.normal(loc=30, scale=15, size=n)
# Assignment 1
data[:,2] = np.random.normal(loc=60, scale=20, size=n)
# Quiz 2
data[:,3] = np.random.normal(loc=50, scale=8, size=n)
# Final
data[:,4] = np.random.normal(loc=57, scale=28, size=n)
# Race
races = ['White', 'Black', 'American Indian', 'Asian']
data[:,5] = np.random.choice(races, n)
# Neighborhood
neighborhoods = ['West Central', 'Logan', 'Riverside', 'Peaceful Valley', "Brown's Addition"]
data[:,6] = np.random.choice(neighborhoods, n)

# Create DataFrame
df = pd.DataFrame(
    columns = columns,
    data = data,
    dtype = 'object'
)

numerical_cols = ['Quiz 1', 'Assignment 1', 'Quiz 2', 'Final']
for numerical_col in numerical_cols:
    df[numerical_col] = df[numerical_col].astype('float')

# Bump Black students Quiz 1 score lower
df[df['Race'] == 'Black']['Quiz 1'] -= 10

# Bump American Indian students Quiz 2 score lower
df[df['Race'] == 'Black']['Quiz 1'] -= 8

# Bump Asian students Final score higher
df[df['Race'] == 'Asian']['Final'] += 12

# Create Total
df['Total'] = df[['Quiz 1', 'Assignment 1', 'Quiz 2', 'Final']].sum(axis=1)

# Rearrange columns
df = df[['Quiz 1', 'Assignment 1', 'Quiz 2', 'Final', 'Total', 'Race', 'Neighborhood']]

# Save data
filename = './example_data/example_data.csv'
df.to_csv(filename)
print(df)