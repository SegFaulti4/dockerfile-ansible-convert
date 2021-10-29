#!/bin/bash

mkdir "./dataset/source"
echo "Extracting..."
tar -xJf ./dataset/source.tar.xz -C ./dataset/
echo "Done!"

find ./dataset/source -type f | sort > ./phase_1/in.txt
