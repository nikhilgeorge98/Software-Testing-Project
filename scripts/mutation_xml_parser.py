import xml.etree.ElementTree as ET
import os
import csv

def extract_mutations_from_xml(xml_file_path):
    """Extract mutations from the XML file."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    mutations_data = {}
    for mutation in root.findall('mutation'):
        status = mutation.attrib['status']
        mutated_class = mutation.find('mutatedClass').text
        mutated_method = mutation.find('mutatedMethod').text
        line_number = mutation.find('lineNumber').text
        mutator = mutation.find('mutator').text
        description = mutation.find('description').text
        killing_tests_element = mutation.find('killingTests')
        killing_tests = killing_tests_element.text.split('|') if killing_tests_element is not None and killing_tests_element.text is not None else []
        succeeding_tests_element = mutation.find('succeedingTests')
        succeeding_tests = succeeding_tests_element.text.split('|') if succeeding_tests_element is not None and succeeding_tests_element.text is not None else []
        mutations_data[(status, mutated_class, mutated_method, line_number, mutator, description)] = (killing_tests, succeeding_tests)
    return mutations_data



def compare_xml_reports(xml_file_1, xml_file_2, test_differences_count):
    """Compare two XML reports for mutation tests."""
    mutations_data_1 = extract_mutations_from_xml(xml_file_1)
    mutations_data_2 = extract_mutations_from_xml(xml_file_2)
    differences = []
    for mutation_key in mutations_data_1:
        if mutation_key in mutations_data_2:
            killing_tests_1, succeeding_tests_1 = mutations_data_1[mutation_key]
            killing_tests_2, succeeding_tests_2 = mutations_data_2[mutation_key]
            set_killing_1 = set(killing_tests_1)
            set_killing_2 = set(killing_tests_2)
            set_succeeding_1 = set(succeeding_tests_1)
            set_succeeding_2 = set(succeeding_tests_2)
            if set_killing_1 != set_killing_2 or set_succeeding_1 != set_succeeding_2:
                differences.append((mutation_key, set_killing_1 - set_killing_2, set_killing_2 - set_killing_1,
                                    set_succeeding_1 - set_succeeding_2, set_succeeding_2 - set_succeeding_1))


                # Update test_differences_count for each test in the mutation
                # for test in set_killing_1 | set_killing_2 | set_succeeding_1 | set_succeeding_2:
                for test in set_succeeding_1 - set_succeeding_2:
                    if test not in test_differences_count:
                        test_differences_count[test] = {'SuccIn': set()}
                    test_differences_count[test]['SuccIn'].add(xml_file_1)

                for test in set_succeeding_2 - set_succeeding_1:
                    if test not in test_differences_count:
                        test_differences_count[test] = {'SuccIn': set()}
                    test_differences_count[test]['SuccIn'].add(xml_file_2)
    return differences


def get_num_tests(xml_files):
    num_tests_dict = {}
    for xml_file_pair in xml_files:
        for xml_file in xml_file_pair:
            mutations_data = extract_mutations_from_xml(xml_file)
            for mutation_key, (killing_tests, succeeding_tests) in mutations_data.items():
                status, mutated_class, _, _, _, _ = mutation_key
                if mutated_class in num_tests_dict:
                    num_tests_dict[mutated_class].update(killing_tests)
                    num_tests_dict[mutated_class].update(succeeding_tests)
                else:
                    num_tests_dict[mutated_class] = set(killing_tests + succeeding_tests)
    return num_tests_dict




def write_differences_to_csv(output_file, xml_files):
    all_differences = []
    summary_dict = {}
    test_differences_count = {}
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["XML File 1", "XML File 2", "Status", "Mutated Class", "Mutated Method", "Line Number", "Mutator",
             "Description", "Unique Killing Tests 1", "Unique Killing Tests 2", "Unique Succeeding Tests 1",
             "Unique Succeeding Tests 2", "Flaky Tests"])
        for xml_file_1, xml_file_2 in xml_files:
            differences = compare_xml_reports(xml_file_1, xml_file_2, test_differences_count)
            if differences:
                for mutation_info, unique_killing_1, unique_killing_2, unique_succeeding_1, unique_succeeding_2 in differences:
                    status, mutated_class, mutated_method, line_number, mutator, description = mutation_info
                    writer.writerow(
                        [os.path.basename(xml_file_1), os.path.basename(xml_file_2), status, mutated_class,
                         mutated_method, line_number, mutator, description, ', '.join(unique_killing_1),
                         ', '.join(unique_killing_2), ', '.join(unique_succeeding_1),
                         ', '.join(unique_succeeding_2)])

                    if mutated_class not in summary_dict:
                        summary_dict[mutated_class] = {'flaky_tests': 0, 'flaky_test_set': set()}

                    if (unique_killing_1 or unique_killing_2 or unique_succeeding_1 or unique_succeeding_2):
                        if not (
                                unique_killing_1 | unique_killing_2 | unique_succeeding_1 | unique_succeeding_2).intersection(
                                summary_dict[mutated_class]['flaky_test_set']):
                           
                            summary_dict[mutated_class]['flaky_tests'] += 1
                            summary_dict[mutated_class]['flaky_test_set'].update(
                                unique_killing_1 | unique_killing_2 | unique_succeeding_1 | unique_succeeding_2)

        num_tests_dict = get_num_tests(xml_files)
        writer.writerow([])
        writer.writerow(["Mutated Class", "Total Tests", "Flaky Tests", "Flaky Test List"])
        for mutated_class, info in summary_dict.items():
            flaky_test_list = list(info['flaky_test_set'])
            writer.writerow(
                [mutated_class, len(num_tests_dict[mutated_class]), len(flaky_test_list), ', '.join(flaky_test_list)])

        writer.writerow([])
        writer.writerow(["Test", "Mutant Survived Count", "Mutant Survived In"])
        for test, succ in test_differences_count.items():
            writer.writerow([test, len(succ['SuccIn']), succ['SuccIn']])
    print(f"Differences and Summary written to {output_file}")



if __name__ == '__main__':
    directory = "TestReports"
    xml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xml") and file.startswith("mutations")]
    pairs = [(xml_files[i], xml_files[j]) for i in range(len(xml_files)) for j in range(i + 1, len(xml_files))]
    output_file = "mutation_differences.csv"
    write_differences_to_csv(output_file, pairs)













