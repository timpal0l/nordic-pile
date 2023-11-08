#!/bin/bash

# The server has 12 cores, 2 physical threads each => 24 logical cores.
# We use 2 extra threads for I/O, so it is likely not beneficial to increase the number of workers more.
NUM_PROCESSING_WORKERS=20

# MUST BE ABSOLUTE PATHS
CONFIG_BASE_PATH="/data/nordic_pile/jsonl_train_format/filter_configs"
ROOT_IN="/data/nordic_pile/jsonl_train_format/original"
ROOT_OUT="/data/nordic_pile/jsonl_train_format/cleaned"
mkdir -p $ROOT_OUT

echo ""
echo "ROOT_IN: ${ROOT_IN}"
echo "ROOT_OUT: ${ROOT_OUT}"
echo "CONFIG_BASE_PATH: ${CONFIG_BASE_PATH}"

for path_in_file in $(find $ROOT_IN -name "*.jsonl"); do
  echo ""

  if [[ $path_in_file == *"opus_templated"* ]]; then
    echo "Temporarily skipping opus translation data since it has been cleaned before being templated."
    continue
  fi

  # Replace ROOT_IN with ROOT_OUT
  path_out_file="${path_in_file/"$ROOT_IN"/"$ROOT_OUT"}"

  if test -f "$path_out_file"; then
    echo "File ${path_out_file} already exists, skipping."
    continue
  fi

  # in_dir="$(dirname "${path_in_file}")"
  echo "${path_out_file}" >> cleaned_files_21_06_2022.txt

  # Get output log path, same directory as output file
  out_dir="$(dirname "${path_out_file}")"
  file_name="$(basename "${path_in_file}")"
  file_name_no_extension="${file_name%.jsonl}"
  log_path="$out_dir/filtering_log_$file_name_no_extension.txt"

  # config_path="${in_dir}/config.yaml"
  # if ! test -f "$config_path"; then
  #   config_path="${ROOT_IN}/config.yaml"
  # fi

  # Create output directory
  mkdir -p $out_dir


  # Build command
  cmd="python3 filter_main.py
      --in_file $path_in_file
      --out_file $path_out_file
      --config_dir_path $CONFIG_BASE_PATH
      --num_workers $NUM_PROCESSING_WORKERS"

  echo "Executing command:"
  echo $cmd

  # Run command
  $cmd &> $log_path

done
