#!/bin/bash

counter=1

for ((i = 1; i <= 10; i++)); do
    mvn test-compile -DfullMutationMatrix=true -DexportLineCoverage=true org.pitest:pitest-maven:mutationCoverage
    if [[ "$?" -ne 0 ]]; then
        exit -1
    fi
    mv target/pit-reports/mutations.xml "target/pit-reports/mutations${counter}.xml"
    mv "target/pit-reports/mutations${counter}.xml" TestReports/
    mv target/pit-reports/linecoverage.xml "target/pit-reports/linecoverage${counter}.xml"
    mv "target/pit-reports/linecoverage${counter}.xml" TestReports/
    
    counter=$((counter + 1))
    echo -e "Done...$counter\n"
done