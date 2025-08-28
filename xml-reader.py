import xml.etree.ElementTree as ET
import json

ns = {"xs": "http://www.w3.org/2001/XMLSchema"}


def parse_restrictions(elem):
    restrictions = {}

    restriction = elem.find(".//xs:restriction", ns)
    if restriction is not None:
        base = restriction.get("base")
        if base:
            restrictions["base"] = base

        # minLength, maxLength, length, totalDigits, fractionDigits
        for tag in ["minLength", "maxLength", "length", "totalDigits", "fractionDigits"]:
            r = restriction.find(f"xs:{tag}", ns)
            if r is not None and r.get("value"):
                restrictions[tag] = r.get("value")

        # pattern
        for p in restriction.findall("xs:pattern", ns):
            restrictions.setdefault("patterns", []).append(p.get("value"))

        # enumeration
        for e in restriction.findall("xs:enumeration", ns):
            restrictions.setdefault("enumerations", []).append(e.get("value"))

    return restrictions


def parse_xsd(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Collect complexType definitions
    complex_types = {}
    for ctype in root.findall("xs:complexType", ns):
        name = ctype.get("name")
        if name:
            complex_types[name] = ctype

    # 🔑 Collect simpleType definitions too
    simple_types = {}
    for stype in root.findall("xs:simpleType", ns):
        name = stype.get("name")
        if name:
            simple_types[name] = parse_restrictions(stype)

    def walk_element(parent_dict, parent_path, elem):
        name = elem.get("name")
        etype = elem.get("type")

        if name:
            min_occurs = elem.get("minOccurs", None)
            max_occurs = elem.get("maxOccurs", None)

            full_path = f"{parent_path}.{name}" if parent_path else name

            # insert this element in parent dict
            parent_dict[name] = {}
            if min_occurs is not None:
                parent_dict[name]["minOccurs"] = int(min_occurs)
            if max_occurs is not None:
                parent_dict[name]["maxOccurs"] = int(max_occurs) if max_occurs.isdigit() else max_occurs

            # expand children if complexType is defined
            has_children = False
            if etype in complex_types:
                has_children = walk_complex_type(parent_dict[name], full_path, complex_types[etype])
            inline_complex = elem.find("xs:complexType", ns)
            if inline_complex is not None:
                has_children = walk_complex_type(parent_dict[name], full_path, inline_complex) or has_children

            # mark groupSourceField vs sourceField
            if has_children:
                parent_dict[name]["groupSourceField"] = full_path
            else:
                parent_dict[name]["sourceField"] = full_path

            # 🔑 restrictions (priority: inline > referenced simpleType)
            restr = parse_restrictions(elem)
            if not restr and etype in simple_types:
                restr = simple_types[etype]

            if restr:
                parent_dict[name].update(restr)

    def walk_complex_type(parent_dict, parent_path, ctype):
        has_children = False
        sequence = ctype.find("xs:sequence", ns)
        if sequence is not None:
            for child in sequence.findall("xs:element", ns):
                walk_element(parent_dict, parent_path, child)
                has_children = True
        choice = ctype.find("xs:choice", ns)
        if choice is not None:
            for child in choice.findall("xs:element", ns):
                walk_element(parent_dict, parent_path, child)
                has_children = True
        return has_children

    result = {}
    for elem in root.findall("xs:element", ns):
        walk_element(result, "", elem)

    return result


if __name__ == "__main__":
    xsd_file = "xsd-files/SwiftCase-Investigations-SR2025_RQFI_UTEX_UGs_InvestigationResponse_SR2025_20250323_1033_iso15enriched.xsd"
    json_output = parse_xsd(xsd_file)

    with open("elements.json", "w") as f:
        json.dump(json_output, f, indent=4)
