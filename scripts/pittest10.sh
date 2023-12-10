#!/bin/bash

set -o pipefail

target_dir="STProjecttargets"
project_dir="Software Testing Project"
repositories_path="../../${target_dir}"

target_csv_file="PIT10.csv"

source_csv_file="../pit_buildsNOW.csv"

if [ ! -f "$target_csv_file" ]; then
  echo "Repository,PIT_Build_Status" > "$target_csv_file"
fi

# Check if repository is already in csv
repository_exists_in_csv() {
  local repo_name="$1"
  local csv_file="$2"
  if grep -q "^$repo_name," "$csv_file"; then
    return 0  # exist
  else
    return 1  # not exist
  fi
}

for repo_dir in "$repositories_path"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    if repository_exists_in_csv "$repo_name" "$source_csv_file"; then
    
        # Check if the repository is already in the PIT build CSV
        if repository_exists_in_csv "$repo_name" "$target_csv_file"; then
            echo "$repo_name is already in PIT build CSV. Skipping..."
            continue
        else
            echo "$repo_name name is not in PIT build CSV"
            cd "$repo_dir" || continue  # Change to the repository directory

            cp -f "../../${project_dir}/scripts/run10.sh" .

            mkdir -p "TestReports"
            rm -r TestReports/*

            ./run10.sh 2>&1 | tee -a "../../${project_dir}/Final/logs/${repo_name}pit10.log"
            if [[ "$?" -ne 0 ]] ; then
                echo "$repo_name,Failure" >> "../../${project_dir}/scripts/${target_csv_file}"
            else
                echo "$repo_name,Success" >> "../../${project_dir}/scripts/${target_csv_file}"
            fi

            cp -f "../../${project_dir}/scripts/${target_csv_file}" "../../${project_dir}"
            
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