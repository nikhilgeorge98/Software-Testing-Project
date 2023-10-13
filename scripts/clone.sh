#!/bin/bash

# Define the CSV file containing repository URLs
csv_filename="pr-data.csv"
csv_file="../data/${csv_filename}"

target_dir="STProjecttargets"
project_dir="Software Testing Project"

# Check if the CSV file exists
if [ ! -f "$csv_file" ]; then
    echo "CSV file ($csv_file) not found."
    exit 1
fi

# Function to clone a repository if it doesn't exist
clone_repository_if_not_exists() {
    local repo_url="$1"
    local repo_name=$(basename "$repo_url" .git)
    cd "../../${target_dir}"
    echo "In repo dir now $(PWD)..."
    
    if [ ! -d "$repo_name" ]; then
        echo "Cloning $repo_url..."
        git clone "$repo_url"
    else
        echo "$repo_name already exists, skipping cloning."
    fi
    cd "../${project_dir}/scripts"
    echo "Back here $(PWD)..."
}

# Read the CSV file and clone repositories
while IFS=',' read -r repo_url _
do
    # Remove leading/trailing spaces and quotes if any
    repo_url=$(echo "$repo_url" | sed -e 's/^ *//' -e 's/ *$//' -e 's/^"//' -e 's/"$//')
    
    # Clone the repository if the URL is not empty
    if [ -n "$repo_url" ]; then
        clone_repository_if_not_exists "$repo_url"
    fi
done < "$csv_file"

echo "Cloning completed."
