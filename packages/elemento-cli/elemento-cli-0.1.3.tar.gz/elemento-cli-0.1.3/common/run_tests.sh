#! /bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

for test in `find . -name 'test_*'`; do
    python3 $test || break
done
