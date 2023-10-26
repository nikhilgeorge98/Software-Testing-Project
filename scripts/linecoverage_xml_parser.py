import xml.etree.ElementTree as ET
import os

def extract_blocks_from_xml(xml_file_path):
    """Extract blocks from the XML file."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    block_data = {}

    for block in root.findall('block'):
        block_classname = block.attrib['classname']
        block_method = block.attrib['method']
        block_number = block.attrib['number']

        # Extracting tests
        tests = [test.attrib['name'] for test in block.find('tests').findall('test')]

        # Using a tuple to store block data and associate it with its tests
        block_data[(block_classname, block_method, block_number)] = tests

    return block_data

def compare_xml_reports(xml_file_1, xml_file_2):
    """Compare two XML reports for block tests coverage."""
    block_data_1 = extract_blocks_from_xml(xml_file_1)
    block_data_2 = extract_blocks_from_xml(xml_file_2)

    differences = []

    for block_key in block_data_1:
        if block_key not in block_data_2 or set(block_data_1[block_key]) != set(block_data_2[block_key]):
            differences.append((block_key, block_data_1[block_key], block_data_2.get(block_key, None)))

    return differences

if __name__ == '__main__':
    directory = "TestReports"
    xml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xml") and file.startswith("linecoverage")]

    # Ensure that only 10 reports are considered (the first 10 found if more are present)
    xml_files = xml_files[:10]

    for i in range(len(xml_files)):
        for j in range(i+1, len(xml_files)):
            print(f"Comparing {xml_files[i]} with {xml_files[j]}")
            
            differences = compare_xml_reports(xml_files[i], xml_files[j])
            if differences:
                for diff in differences:
                    block_info, tests_1, tests_2 = diff
                    block_classname, block_method, block_number = block_info

                    print(f"Difference found: Classname - {block_classname}, Method - {block_method}, Number - {block_number}")
                    print(f"Tests in {xml_files[i]}: {', '.join(tests_1)}")
                    if tests_2:
                        print(f"Tests in {xml_files[j]}: {', '.join(tests_2)}")
                    else:
                        print(f"Tests in {xml_files[j]}: None")
                    print("----------")
            print("===================================")

