#!/bin/bash


CONFIG_YAML_PATH="example_config.yaml"

# INPUT_FILE_PATH="data/conversations_sv_subset_filtered.jsonl"

OUTPUT_FILE_PATH="out_file_temp.jsonl"
NUM_PROCESSING_WORKERS=24


cmd="python3 filter_main.py
      --in_file $INPUT_FILE_PATH
      --out_file $OUTPUT_FILE_PATH
      --config_file $CONFIG_YAML_PATH
      --num_workers $NUM_PROCESSING_WORKERS"

echo "Executing command:"
echo $cmd
echo ""

$cmd
