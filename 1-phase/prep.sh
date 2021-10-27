#!/bin/bash

mkdir "./dataset/gold"
echo "Extracting..."
tar -xJf ./dataset/gold.tar.xz -C ./dataset/
echo "Done!"

find ./dataset/gold -type f | sort > ./1-phase/in.txt
