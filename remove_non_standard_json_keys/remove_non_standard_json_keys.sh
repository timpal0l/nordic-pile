#!/bin/bash

COMMON_PATH="/data/nordic_pile/jsonl_train_format/final_data"

in_file="$COMMON_PATH/final_merged/code_cd.jsonl"
out_file="$COMMON_PATH/temp_json_keys/code_cd.jsonl"

python remove_non_standard_json_keys.py --input_file $in_file --output_file $out_file
