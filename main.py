import pandas as pd
import json
from collections import OrderedDict

def csv_to_json_tree(input_csv, output_file="tree.json"):
    # read CSV
    df = pd.read_csv(input_csv)

    # drop rows where tag is NaN or empty
    df = df.dropna(subset=["tag"])
    df = df[df["tag"].str.strip() != ""]

    nodes = [
        (int(row["level"]), row["tag"].strip(), row.get("min"), row.get("max"))
        for _, row in df.iterrows()
    ]

    root = OrderedDict()
    stack = [(-1, "", root)]  # (level, path, dict reference)

    for level, label, min_val, max_val in nodes:
        # go back to correct parent
        while stack and stack[-1][0] >= level:
            stack.pop()

        parent_path = stack[-1][1]
        parent_dict = stack[-1][2]

        current_path = f"{parent_path}.{label}" if parent_path else label

        node = OrderedDict()
        # Attach min/max if valid
        if pd.notna(min_val):
            node["minOccur"] = int(min_val)
        if pd.notna(max_val):
            node["maxOccur"] = int(max_val)

        parent_dict[label] = node
        stack.append((level, current_path, node))

    # recursive function to add sourceField/groupSourceField
    def annotate(d, path):
        for key in list(d.keys()):
            full_path = f"{path}.{key}" if path else key
            value = d[key]

            # extract any existing min/max before overwriting
            min_val = value.pop("minOccur", None)
            max_val = value.pop("maxOccur", None)

            if any(isinstance(v, dict) for v in value.values()):  # has children
                annotate(value, full_path)
                new_obj = OrderedDict()
                new_obj["groupSourceField"] = full_path
                if min_val is not None:
                    new_obj["minOccur"] = min_val
                if max_val is not None:
                    new_obj["maxOccur"] = max_val
                new_obj.update(value)
                d[key] = new_obj
            else:  # leaf
                leaf = OrderedDict()
                leaf["sourceField"] = full_path
                if min_val is not None:
                    leaf["minOccur"] = min_val
                if max_val is not None:
                    leaf["maxOccur"] = max_val
                d[key] = leaf

    annotate(root, "")

    with open(output_file, "w") as f:
        json.dump(root, f, indent=4)

    print(f"JSON tree written to {output_file} ✅")

# Example usage
csv_to_json_tree("test.csv", "json-files/Mapper.json")
