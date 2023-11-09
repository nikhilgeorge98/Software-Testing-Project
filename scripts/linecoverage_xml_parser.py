import xml.etree.ElementTree as ET
import os
import csv
from itertools import combinations


def extract_blocks_from_xml(xml_file_path):
    """Extract blocks from the XML file."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    block_data = {}
    for block in root.findall('block'):
        block_classname = block.attrib['classname']
        block_method = block.attrib['method']
        block_number = block.attrib['number']
        tests = [test.attrib['name'] for test in block.find('tests').findall('test')]
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


def write_differences_to_csv(output_file, xml_files):
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["XML File 1", "XML File 2", "Classname", "Method", "Number", "Tests in File 1", "Tests in File 2"])
        for xml_file_1, xml_file_2 in xml_files:
            differences = compare_xml_reports(xml_file_1, xml_file_2)
            if differences:
                for diff in differences:
                    block_info, tests_1, tests_2 = diff
                    block_classname, block_method, block_number = block_info
                    writer.writerow([os.path.basename(xml_file_1), os.path.basename(xml_file_2), block_classname, block_method, block_number, ', '.join(tests_1), ', '.join(tests_2) if tests_2 else 'None'])


if __name__ == '__main__':
    directory = "TestReports"
    xml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xml") and file.startswith("linecoverage")]
    xml_files = xml_files[:10]
    pairs = list(combinations(xml_files, 2))  
    output_file = "linecoverage_differences.csv"
    write_differences_to_csv(output_file, pairs)
    print(f"Differences written to {output_file}")







