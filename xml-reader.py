import xml.etree.ElementTree as ET

ns = {"xs": "http://www.w3.org/2001/XMLSchema"}

def parse_xsd(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Collect complexType definitions into a dictionary
    complex_types = {}
    for ctype in root.findall("xs:complexType", ns):
        name = ctype.get("name")
        if name:
            complex_types[name] = ctype

    results = []

    def walk_element(parent_path, elem):
        name = elem.get("name")
        etype = elem.get("type")

        if name:
            # default values
            min_occurs = elem.get("minOccurs", "1")
            max_occurs = elem.get("maxOccurs", "1")

            occurs_str = f"[minOccurs={min_occurs},maxOccurs={max_occurs}]"

            full_path = f"{parent_path}.{name}" if parent_path else name
            results.append(f"{full_path} {occurs_str}")

            # If element refers to a named complexType
            if etype in complex_types:
                walk_complex_type(full_path, complex_types[etype])

            # If inline complexType exists
            inline_complex = elem.find("xs:complexType", ns)
            if inline_complex is not None:
                walk_complex_type(full_path, inline_complex)

    def walk_complex_type(parent_path, ctype):
        # Handle sequence
        sequence = ctype.find("xs:sequence", ns)
        if sequence is not None:
            for child in sequence.findall("xs:element", ns):
                walk_element(parent_path, child)

        # Handle choice
        choice = ctype.find("xs:choice", ns)
        if choice is not None:
            for child in choice.findall("xs:element", ns):
                walk_element(parent_path, child)

    # Start with all top-level elements
    for elem in root.findall("xs:element", ns):
        walk_element("", elem)

    return results


if __name__ == "__main__":
    xsd_file = "xsd-files/SwiftCase-Investigations-SR2025_RQFI_COMP_UGs_InvestigationRequest_SR2025_20250323_1023_iso15enriched.xsd"  # change this to your file
    paths = parse_xsd(xsd_file)

    for p in paths:
        print(p)
