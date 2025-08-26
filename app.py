import pandas as pd

# Convert dictionary to a DataFrame
df = pd.read_csv("csv-files/test.csv")
min_list = []
max_list = []
with open("text-files/input.txt", "r") as f:
    for line in f:
        line = line.strip()
        min_occur = None
        max_occur = None
        if len(line) == 0:
            pass
        else:
            line = line[1:-1]
            min_max = line.split("..")
            min_occur = int(min_max[0])
            if min_max[1] != "*":
                max_occur = int(min_max[1])
        min_list.append(min_occur)
        max_list.append(max_occur)
# print(df.head())

print(max_list)
print(min_list)

df["min"] = min_list
df["max"] = max_list
df.to_csv("csv-files/test.csv", index=False)
print("✅ Overwritten csv-files/test.csv")

print(df.head())