import json
import pandas as pd
from collections import OrderedDict

def csv_to_json_tree(input_csv, output_file="tree.json"):
    # read CSV
    df = pd.read_csv(input_csv)

    # drop rows where tag is NaN or empty
    df = df.dropna(subset=["tag"])
    df = df[df["tag"].str.strip() != ""]

    nodes = [(int(row["level"]), row["tag"].strip()) for _, row in df.iterrows()]
    root = OrderedDict()
    stack = [(-1, "", root)]  # (level, path, dict reference)

    for level, label in nodes:
        # go back to correct parent
        while stack and stack[-1][0] >= level:
            stack.pop()

        parent_path = stack[-1][1]
        parent_dict = stack[-1][2]

        current_path = f"{parent_path}.{label}" if parent_path else label

        parent_dict[label] = OrderedDict()
        stack.append((level, current_path, parent_dict[label]))

    # recursive function to add sourceField/groupSourceField
    def annotate(d, path):
        for key in list(d.keys()):
            full_path = f"{path}.{key}" if path else key
            value = d[key]

            if value:  # has children
                annotate(value, full_path)
                new_obj = OrderedDict()
                new_obj["groupSourceField"] = full_path
                new_obj.update(value)
                d[key] = new_obj
            else:  # leaf
                d[key] = OrderedDict()
                d[key]["sourceField"] = full_path

    annotate(root, "")

    with open(output_file, "w") as f:
        json.dump(root, f, indent=4)

    print(f"JSON tree written to {output_file} ✅")


# Example usage
csv_to_json_tree("test.csv", "tree.json")
