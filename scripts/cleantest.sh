#!/bin/bash

# Define the directory where your repositories are located
target_dir="STProjecttargets"
project_dir="Software Testing Project"
repositories_path="../../${target_dir}"

# Define the CSV file to append successful builds
csv_file="clean_builds.csv"

# Create or initialize the CSV file with a header if it doesn't exist
if [ ! -f "$csv_file" ]; then
  echo "Repository,Build_Status" > "$csv_file"
fi

# Function to check if a repository is already in the CSV file
repository_exists_in_csv() {
  local repo_name="$1"
  if grep -q "^$repo_name," "$csv_file"; then
    return 0  # Repository exists in CSV
  else
    return 1  # Repository does not exist in CSV
  fi
}

# Iterate through the repositories
for repo_dir in "$repositories_path"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    # Check if the repository is already in the CSV
    if repository_exists_in_csv "$repo_name"; then
      echo "$repo_name is already in the CSV. Skipping..."
      continue
    else
      # Run 'mvn clean test' and check the exit status
      echo "$repo_name name is not in csv"
      cd "$repo_dir" || continue  # Change to the repository directory

      mvn clean test
      if [[ "$?" -ne 0 ]] ; then
          echo "$repo_name,Failure" >> "../../${project_dir}/scripts/${csv_file}"
      else
          echo "$repo_name,Success" >> "../../${project_dir}/scripts/${csv_file}"
      fi

      # Return to the original directory
      cd - > /dev/null
    fi

  fi
done

echo "Build process complete."