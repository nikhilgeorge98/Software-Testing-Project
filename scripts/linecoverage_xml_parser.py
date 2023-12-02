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

def get_num_tests(xml_files):
    num_tests_dict = {}

    for xml_file_pair in xml_files:
        for xml_file in xml_file_pair:
            block_data = extract_blocks_from_xml(xml_file)

            for block_key, tests in block_data.items():
                if block_key not in num_tests_dict:
                    num_tests_dict[block_key] = set()

                num_tests_dict[block_key].update(tests)

    return num_tests_dict


def write_differences_to_csv(output_file, xml_files):
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["XML File 1", "XML File 2", "Classname", "Method", "Number", "Tests in File 1", "Tests in File 2"])

        block_summaries = {}  

        for xml_file_1, xml_file_2 in xml_files:
            differences = compare_xml_reports(xml_file_1, xml_file_2)
            if differences:
                for diff in differences:
                    block_info, tests_1, tests_2 = diff
                    block_classname, block_method, block_number = block_info
                    writer.writerow([os.path.basename(xml_file_1), os.path.basename(xml_file_2), block_classname, block_method, block_number, ', '.join(tests_1), ', '.join(tests_2) if tests_2 else 'None'])

                    block_summaries[block_info] = (set(tests_1), set(tests_2) if tests_2 else set())

        writer.writerow([])  
        writer.writerow(["Block Name", "Total Num Tests", "Num Flaky Tests", "Flaky Tests"])
        num_test_dict = get_num_tests(xml_files)
        for block_info, (tests_1, tests_2) in block_summaries.items():
            block_classname, block_method, block_number = block_info
            tests_1 = set(tests_1) if tests_1 else set()
            tests_2 = set(tests_2) if tests_2 else set()
            different_tests = (tests_1 - tests_2) | (tests_2 - tests_1)
            
            if different_tests:
                print(f"num_tests: {num_test_dict[(block_classname, block_method, block_number)]}, different_tests: {different_tests}")
                writer.writerow([f"{block_classname}::{block_method}::{block_number}", len(num_test_dict[(block_classname, block_method, block_number)]), len(different_tests), ', '.join(different_tests) if different_tests else 'None'])

if __name__ == '__main__':
    directory = "TestReports"
    xml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xml") and file.startswith("linecoverage")]
    xml_files = xml_files[:10]
    pairs = list(combinations(xml_files, 2))  
    output_file = "linecoverage_differences.csv"
    write_differences_to_csv(output_file, pairs)
    print(f"Differences written to {output_file}")
