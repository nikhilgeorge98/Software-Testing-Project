import xml.etree.ElementTree as ET
import os

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

        # Extracting killing and succeeding tests
        killing_tests = mutation.find('killingTests').text.split('|') if mutation.find('killingTests').text else []
        succeeding_tests = mutation.find('succeedingTests').text.split('|') if mutation.find('succeedingTests').text else []

        # Using a tuple to store mutation data and associate it with its tests
        mutations_data[(status, mutated_class, mutated_method, line_number, mutator, description)] = (killing_tests, succeeding_tests)

    return mutations_data


def compare_xml_reports(xml_file_1, xml_file_2):
    """Compare two XML reports for mutation tests."""
    mutations_data_1 = extract_mutations_from_xml(xml_file_1)
    mutations_data_2 = extract_mutations_from_xml(xml_file_2)

    differences = []

    # Find mutations that have different tests between the two reports
    for mutation_key in mutations_data_1:
        if mutation_key in mutations_data_2:
            killing_tests_1, succeeding_tests_1 = mutations_data_1[mutation_key]
            killing_tests_2, succeeding_tests_2 = mutations_data_2[mutation_key]

            # Convert lists to sets for comparison
            set_killing_1 = set(killing_tests_1)
            set_killing_2 = set(killing_tests_2)

            set_succeeding_1 = set(succeeding_tests_1)
            set_succeeding_2 = set(succeeding_tests_2)

            # Check for differences between the sets
            if set_killing_1 != set_killing_2 or set_succeeding_1 != set_succeeding_2:
                differences.append((mutation_key, (killing_tests_1, succeeding_tests_1), (killing_tests_2, succeeding_tests_2)))

    return differences



if __name__ == '__main__':
    directory = "TestReports"
    xml_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xml") and file.startswith("mutations")]


    for i in range(len(xml_files)):
        for j in range(i+1, len(xml_files)):
            print(f"Comparing {xml_files[i]} with {xml_files[j]}")

            differences = compare_xml_reports(xml_files[i], xml_files[j])

            if differences:
                for diff in differences:
                    mutation_info, tests_1, tests_2 = diff
                    status, mutated_class, mutated_method, line_number, mutator, description = mutation_info

                    killing_tests_1, succeeding_tests_1 = tests_1
                    killing_tests_2, succeeding_tests_2 = tests_2

                    # Convert lists to sets for comparison
                    set_killing_1 = set(killing_tests_1)
                    set_killing_2 = set(killing_tests_2)

                    set_succeeding_1 = set(succeeding_tests_1)
                    set_succeeding_2 = set(succeeding_tests_2)

                    # Determine unique tests in each XML file
                    unique_killing_1 = set_killing_1 - set_killing_2
                    unique_killing_2 = set_killing_2 - set_killing_1

                    unique_succeeding_1 = set_succeeding_1 - set_succeeding_2
                    unique_succeeding_2 = set_succeeding_2 - set_succeeding_1

                    print(f"Difference found: Class - {mutated_class}, Method - {mutated_method}, Line - {line_number}, Mutator - {mutator}, Status - {status}")

                    if unique_killing_1:
                        print(f"Unique killing tests in {xml_files[i]}: {', '.join(unique_killing_1)}")
                    if unique_killing_2:
                        print(f"Unique killing tests in {xml_files[j]}: {', '.join(unique_killing_2)}")

                    if unique_succeeding_1:
                        print(f"Unique succeeding tests in {xml_files[i]}: {', '.join(unique_succeeding_1)}")
                    if unique_succeeding_2:
                        print(f"Unique succeeding tests in {xml_files[j]}: {', '.join(unique_succeeding_2)}")

                    print("----------")
            print("===================================")
