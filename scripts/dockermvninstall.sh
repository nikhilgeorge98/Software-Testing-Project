#!/bin/bash

set -o pipefail

java_version=$1
username="ngeorge98"
image_name="myopenjdk$java_version"

# echo "$image_name"
# exit 0

target_dir="STProjecttargets"
project_dir="Software Testing Project"
repositories_path="../../${target_dir}"

csv_file="buildsdocker${image_name}.csv"

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

# run maven build inside docker container
run_maven_in_docker() {
  local repo_name="$1"
  # local java_version="$2"

  echo "$(pwd)"
  echo "$username/$image_name"
  
#   docker run --rm -v "$(pwd):/app" -w /app -it myopenjdk$java_version
  docker run --rm -v "$(pwd):/app" -w /app $username/$image_name mvn install -fae 2>&1 | tee -a outputdocker$image_name.log "../../${project_dir}/logs/${repo_name}/outputdocker$image_name.log"

}

for repo_dir in "$repositories_path"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    # Check if the repository is already in the CSV
    if repository_exists_in_csv "$repo_name"; then
      echo "$repo_name is already in the CSV. Skipping..."
      continue
    else
      echo "$repo_name name is not in csv"
      cd "$repo_dir" || continue  # Change repo dir
      
      mkdir -p "../../${project_dir}/logs/${repo_name}"

      run_maven_in_docker "$repo_name"      
      if [[ "$?" -ne 0 ]]; then
        echo "$repo_name,Failure" >> "../../${project_dir}/scripts/${csv_file}"
      else
        echo "$repo_name,Success" >> "../../${project_dir}/scripts/${csv_file}"
      fi

      cp -f "../../${project_dir}/scripts/${csv_file}" "../../${project_dir}"
      # cp -f "../../${project_dir}/logs/outputdockerjdk$java_version.log" "../../${project_dir}"
      
      # Return to the original directory
      cd - > /dev/null 
    fi
  fi
done

echo "Build process complete."
