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

target_csv_file="pit_buildsdocker${image_name}.csv"

source_csv_file="../buildsdocker${image_name}.csv"

poms="../pomschanged.csv"

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

# run PIT inside docker container
run_PIT_in_docker() {
  local repo_name="$1"
  # local java_version="$2"

  echo "$(pwd)"
  echo "$username/$image_name"
  
#   docker run --rm -v "$(pwd):/app" -w /app -it myopenjdk$java_version
  # docker run --rm -v "$(pwd):/app" -w /app $username/$image_name ./run10.sh 2>&1 | tee -a pitoutputdocker$image_name.log "../../${project_dir}/logs/${repo_name}/pitoutputdocker$image_name.log"
  docker run --rm -v "$(pwd):/app" -w /app $username/$image_name /bin/bash -c "sed -i -e 's/\r$//' run10.sh; ./run10.sh;"
  # docker run --rm -v "$(pwd):/app" -w /app -it $username/$image_name 

}

for repo_dir in "$repositories_path"/*; do
  if [ -d "$repo_dir" ]; then
    repo_name=$(basename "$repo_dir")
    
    # Check if pom changed
    if repository_exists_in_csv "$repo_name" "$poms"; then
    
        # Check if the repository is already in the PIT build CSV
        if repository_exists_in_csv "$repo_name" "$target_csv_file"; then
            echo "$repo_name is already in PIT build CSV. Skipping..."
            continue
        else
            echo "$repo_name name is not in PIT build CSV"
            cd "$repo_dir" || continue  # Change to the repository directory

            cp -f "../../${project_dir}/scripts/run10.sh" .
            mkdir -p "TestReports"

            run_PIT_in_docker "$repo_name"
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