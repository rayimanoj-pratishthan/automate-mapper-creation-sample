import pandas as pd

def reformat_text_file(input_file):
    result = []
    result.append("")
    inside_quotes = False
    buffer = []

    with open(input_file, "r") as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip("\n")

        if stripped.startswith('"') and stripped.endswith('"'):
            # Case: whole quoted line in one line
            result.append(stripped.strip('"'))
        elif stripped.startswith('"'):
            # Start of multiline quoted block
            inside_quotes = True
            buffer.append(stripped.strip('"'))
        elif stripped.endswith('"') and inside_quotes:
            # End of multiline quoted block
            buffer.append(stripped.strip('"'))
            result.append(" ".join(buffer))
            buffer = []
            inside_quotes = False
        elif inside_quotes:
            # Middle of multiline quoted block
            buffer.append(stripped)
        else:
            # Normal line
            result.append(stripped.strip('"'))

    # If file ends while still inside quotes, flush buffer
    if buffer:
        result.append(" ".join(buffer))

    return result


# Read CSV
df = pd.read_csv("csv-files/test.csv")

# Parse text file
result = reformat_text_file("text-files/input.txt")

print("length of parsed result:", len(result))
print("rows in df:", len(df))

# Assign result to dataframe if lengths match
if len(result) == len(df):
    df["type"] = result
else:
    print("⚠️ Length mismatch: cannot assign result to DataFrame")

df.to_csv("csv-files/test.csv", index=False)
print("✅ Overwritten csv-files/test.csv")

