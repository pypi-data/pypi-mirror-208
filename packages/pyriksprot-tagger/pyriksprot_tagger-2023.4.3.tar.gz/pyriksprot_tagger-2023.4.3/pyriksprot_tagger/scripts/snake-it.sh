#!/bin/bash
source .env
export OMP_NUM_THREADS=16
for ((year=1920;year<=2020;year++)); do
	echo $year
	nohup make annotate YEAR=$year PROCESSES_COUNT=1 &>> tag.${RIKSPROT_REPOSITORY_TAG}.log
done
