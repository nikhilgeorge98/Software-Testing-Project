#!/bin/bash

# Define the directory where your repositories are located
target_dir="STProjecttargets"
project_dir="Software Testing Project"
repositories_path="../../${target_dir}"

# Define the CSV file to append successful builds
target_csv_file="pit_builds.csv"

# Source csv file which has succesful build list
source_csv_file="../build_successes.csv"

# Create or initialize the CSV file with a header if it doesn't exist
if [ ! -f "$target_csv_file" ]; then
  echo "Repository,Build_Status" > "$target_csv_file"
fi

# Function to check if a repository is already in the CSV file
repository_exists_in_csv() {
  local repo_name="$1"
  local target_csv_file="$2"
  if grep -q "^$repo_name," "$target_csv_file"; then
    return 0  # Repository exists in CSV
  else
    return 1  # Repository does not exist in CSV
  fi
}

# Iterate through the repositories
for repo_dir in "$repositories_dir"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    # Check if repository was built successfully without PIT
    if repository_exists_in_csv "$repo_name" "$source_csv_file"; then
    
        # Check if the repository is already in the PIT build CSV
        if repository_exists_in_csv "$repo_name" "$target_csv_file"; then
            echo "$repo_name is already in PIT build CSV. Skipping..."
            continue
        else
            # Run and check the exit status
            echo "$repo_name name is not in PIT build CSV"
            cd "$repo_dir" || continue  # Change to the repository directory

            mvn test-compile org.pitest:pitest-maven:mutationCoverage
            if [[ "$?" -ne 0 ]] ; then
                echo "$repo_name,Failure" >> "../../${project_dir}/scripts/${target_csv_file}"
            else
                echo "$repo_name,Success" >> "../../${project_dir}/scripts/${target_csv_file}"
            fi
            
            # Return to the original directory
            cd - > /dev/null
        fi
    else
        echo "$repo_name was not mvn test build success. Skipping..."
        continue
    fi

  fi
done

echo "PIT build complete."