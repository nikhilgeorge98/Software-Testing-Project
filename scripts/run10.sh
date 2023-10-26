#!/bin/bash

# Initialize the counter variable to 1
counter=1

# Loop 10 times
for ((i = 1; i <= 10; i++)); do
    mvn test-compile -DfullMutationMatrix=true -DexportLineCoverage=true org.pitest:pitest-maven:mutationCoverage
    mv target/pit-reports/mutations.xml "target/pit-reports/mutations${counter}.xml"
    mv "target/pit-reports/mutations${counter}.xml" TestReports/
    mv target/pit-reports/linecoverage.xml "target/pit-reports/linecoverage${counter}.xml"
    mv "target/pit-reports/linecoverage${counter}.xml" TestReports/
    
    counter=$((counter + 1))
    echo -e "Done...$counter\n"
done