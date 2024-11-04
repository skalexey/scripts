#!/bin/bash

# Default options
SKIP_MD5_CHECK=false  # Default is to check MD5
VERBOSE=false  # Default verbose mode to off

# Parse options and parameters
POSITIONAL_ARGS=()

while [[ "$#" -gt 0 ]]; do
	case "$1" in
		-i|--skip-md5-check)
			SKIP_MD5_CHECK=true
			shift
			;;
		--verbose)
			VERBOSE=true
			shift
			;;
		*)
			POSITIONAL_ARGS+=("$1")  # Collect positional arguments
			shift
			;;
	esac
done

# Restore positional arguments
set -- "${POSITIONAL_ARGS[@]}"
SOURCE_DIR="$1"
TARGET_DIR="$2"
FILE_PATTERN="$3"
COMMAND="${4:-cp}"  # Default to "cp" if no command is specified

# Print all the variables if verbose mode is enabled
if [ "$VERBOSE" = true ]; then
    echo "SOURCE_DIR: $SOURCE_DIR"
    echo "TARGET_DIR: $TARGET_DIR"
    echo "FILE_PATTERN: $FILE_PATTERN"
    echo "COMMAND: $COMMAND"
    echo "SKIP_MD5_CHECK: $SKIP_MD5_CHECK"
    echo "VERBOSE: $VERBOSE"
fi

# Check if source directory, target directory, and file pattern are provided
if [ -z "$SOURCE_DIR" ] || [ -z "$TARGET_DIR" ] || [ -z "$FILE_PATTERN" ]; then
	echo "Usage: $0 <source_directory> <target_directory> <file_pattern> [command] [-i|--skip-md5-check] [--verbose]"
	echo "Example: $0 /path/to/OneDrive /path/to/target_directory '*.docx' cp"
	exit 1
fi

# Function to get file size
get_file_size() {
	local file="$1"
	local size
	if [[ "$OSTYPE" == "darwin"* ]]; then
		size=$(stat -f%z "$file")
	elif [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
		size=$(stat -c%s "$file")
	else
		echo "Unsupported OS: $OSTYPE"
		exit 1
	fi
	echo "$size"
}

# Function to calculate the MD5 checksum and store it for reuse
declare -A FILE_MD5S
calculate_md5() {
	local file="$1"
	# Return stored MD5 if already calculated
	if [[ -n "${FILE_MD5S[$file]}" ]]; then
		echo "${FILE_MD5S[$file]}"
		return
	fi
	
	local md5
	if command -v md5 &> /dev/null; then
		md5=$(md5 "$file" | awk -F ' = ' '{print $2}')
	elif command -v md5sum &> /dev/null; then
		md5=$(md5sum "$file" | awk '{print $1}')
	else
		echo "Error: Neither md5 nor md5sum command found!"
		exit 1
	fi
	FILE_MD5S["$file"]=$md5
	echo "$md5"
}

# Normalize SOURCE_DIR and TARGET_DIR to absolute paths without trailing slashes
SOURCE_DIR=$(realpath "$SOURCE_DIR")
TARGET_DIR=$(realpath "$TARGET_DIR")

# Find all files matching the pattern
file_list=()
while IFS= read -r file; do
	file_list+=("$file")
done < <(find "$SOURCE_DIR" -type f -name "$FILE_PATTERN")

# Calculate total count of files
total_count=${#file_list[@]}

# Check if there are any files to process
if [ "$total_count" -eq 0 ]; then
	echo "No files found matching the pattern $FILE_PATTERN in $SOURCE_DIR"
	exit 0
fi

# Calculate total size of all matching files with a progress indicator
total_size=0
current_count=0
for file in "${file_list[@]}"; do
	# Retrieve and add file size to total
	file_size=$(get_file_size "$file")
	total_size=$((total_size + file_size))
	current_count=$((current_count + 1))
	
	# Calculate and display progress percentage
	progress=$((current_count * 100 / total_count))
	echo -ne "Calculating total size... ${progress}%\r"
done

# Print a newline after the progress display is complete
echo -e "\nTotal size of matching files: $((total_size / 1024 / 1024)) MB"

# Create the target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Initialize progress tracking and file processing count
processed_size=0
processed_count=0  # Counter for files that are actually processed

# Define color for command highlighting (e.g., bold cyan)
COLOR="\033[1;36m"
RESET="\033[0m"

# Process each file
for file in "${file_list[@]}"; do
	# Normalize each file path
	absolute_file=$(realpath "$file")
	
	# Get the relative path by stripping SOURCE_DIR from absolute_file
	relative_path="${absolute_file#$SOURCE_DIR}"
	relative_dir=$(dirname "$relative_path")
	
	# Ensure the path is correctly joined with a slash
	dest_dir="$TARGET_DIR/$relative_dir"
	mkdir -p "$dest_dir"
	
	# Determine the destination path
	dest="$dest_dir/$(basename "$file")"
	
	# Check if the destination file already exists and compare MD5 checksums if enabled
	file_size=$(get_file_size "$file")  # Retrieve the size of the current file
	if [ "$SKIP_MD5_CHECK" = false ] && [ -f "$dest" ]; then
		src_md5=$(calculate_md5 "$file")
		dest_md5=$(calculate_md5 "$dest")
		if [ "$VERBOSE" = true ]; then
			echo "MD5 of source file ($file): $src_md5"
			echo "MD5 of destination file ($dest): $dest_md5"
		fi
		if [ "$src_md5" = "$dest_md5" ]; then
			echo "Skipping $file -> $dest (files are identical)"
			# Update processed size with skipped file's size
			processed_size=$((processed_size + file_size))
			progress=$((processed_size * 100 / total_size))
			echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
			continue
		fi
	fi

	# Run the specified command with source and destination as arguments, highlighting the command
	echo -e "Executing: ${COLOR}$COMMAND \"$file\" \"$dest\"${RESET}"
	$COMMAND "$file" "$dest"
	
	# Increment processed count and update processed size
	processed_count=$((processed_count + 1))
	processed_size=$((processed_size + file_size))  # Update processed size
	progress=$((processed_size * 100 / total_size))
	
	# Display progress
	echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
done

# Final summary
echo -e "\nOperation complete."
echo "Command applied to $processed_count of $total_count files"

