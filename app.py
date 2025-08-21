import pandas as pd

# Convert dictionary to a DataFrame
df = pd.read_csv("test.csv",index_col=None)

print(df.head())
