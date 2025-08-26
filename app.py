import json
import xmlschema
from xmlschema.validators import XsdGroup


def strip_ns(name: str) -> str:
    """Remove namespace from element or attribute names."""
    if name and "}" in name:
        return name.split("}", 1)[1]  # take part after '}'
    return name


def xsd_to_json_schema(xsd_file, root_element=None):
    """
    Convert an XSD schema into a JSON skeleton with empty values.
    """
    schema = xmlschema.XMLSchema(xsd_file)

    # If no root is provided, take the first global element
    if root_element is None:
        root_element = list(schema.elements.keys())[0]

    def build_json(element):
        """
        Recursively build JSON skeleton from XSD element.
        """
        if element.type.is_complex():
            obj = {}

            # Handle attributes (if any)
            for attr_name, attr in element.type.attributes.items():
                obj[f"@{strip_ns(attr_name)}"] = ""  # attributes prefixed with @

            # Handle child elements if content model exists and is a group
            if isinstance(element.type.content, XsdGroup):
                for child in element.type.content.iter_elements():
                    key = strip_ns(child.name)
                    if child.max_occurs is None or child.max_occurs > 1:
                        obj[key] = [build_json(child)]
                    else:
                        obj[key] = build_json(child)

            return obj
        else:
            # Simple type → return empty string, or defaults based on type
            base_type = element.type.local_name
            if base_type in ("int", "integer", "long", "short"):
                return 0
            elif base_type in ("boolean",):
                return False
            elif base_type in ("float", "double", "decimal"):
                return 0.0
            elif base_type in ("date", "dateTime"):
                return ""
            else:
                return ""

    root = schema.elements[root_element]
    return {strip_ns(root.name): build_json(root)}

def save_json(data, filename="output.json"):
    """
    Save JSON skeleton to a file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON skeleton saved to {filename}")


if __name__ == "__main__":
    # Example usage
    xsd_path = "SwiftCase-Investigations-SR2025_RQFI_COMP_UGs_InvestigationRequest_SR2025_20250323_1023_iso15enriched.xsd"
    json_skeleton = xsd_to_json_schema(xsd_path)

    # Save to file
    save_json(json_skeleton, "schema_skeleton.json")