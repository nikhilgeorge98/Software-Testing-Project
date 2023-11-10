#!/bin/bash

set -o pipefail

target_dir="STProjecttargets"
project_dir="Software Testing Project"
repositories_path="../../${target_dir}"

csv_file="builds.csv"

# if CSV doesn't exist
if [ ! -f "$csv_file" ]; then
  echo "Repository,Build_Status" > "$csv_file"
fi

# Check if repository is already in csv
repository_exists_in_csv() {
  local repo_name="$1"
  if grep -q "^$repo_name," "$csv_file"; then
    return 0  # exists
  else
    return 1  # not exist
  fi
}

# Iterate through repos
for repo_dir in "$repositories_path"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    if repository_exists_in_csv "$repo_name"; then
      echo "$repo_name is already in the CSV. Skipping..."
      continue
    else
      echo "$repo_name name is not in csv"
      cd "$repo_dir" || continue  # Change repo dir

      mkdir -p "../../${project_dir}/logs/${repo_name}"

      mvn install -fae 2>&1 | tee -a output.log "../../${project_dir}/logs/${repo_name}/output.log"
      if [[ "$?" -ne 0 ]] ; then
          echo "$repo_name,Failure" >> "../../${project_dir}/scripts/${csv_file}"
      else
          echo "$repo_name,Success" >> "../../${project_dir}/scripts/${csv_file}"
      fi

      cp -f "../../${project_dir}/scripts/${csv_file}" "../../${project_dir}"
      # cp -f "../../${project_dir}/logs/output.log" "../../${project_dir}"
      
      # Return to root
      cd - > /dev/null 
    fi

  fi
done

echo "Build process complete."