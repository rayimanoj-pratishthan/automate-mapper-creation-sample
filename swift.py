import pandas as pd

result = []

with open("text-files/input.txt") as f:
    lines = f.readlines()

    for l in lines: 
        ll = l.strip("\n")

        result.append(ll)

    
df = pd.read_csv("csv-files/test.csv")
if len(result) == len(df):
    df["swift"] = result

df.to_csv("csv-files/test.csv", index=False)
print("✅ Overwritten csv-files/test.csv")
