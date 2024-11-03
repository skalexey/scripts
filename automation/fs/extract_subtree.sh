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

if [ "$VERBOSE" = true ]; then
    # Print all the variables for debugging
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

# Function to get file size, compatible with different platforms
get_file_size() {
	local file="$1"
	if [[ "$OSTYPE" == "darwin"* ]]; then
		# macOS
		stat -f%z "$file"
	elif [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "cygwin"* || "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
		# Linux and Windows (MinGW, Cygwin)
		stat -c%s "$file"
	else
		echo "Unsupported OS: $OSTYPE"
		exit 1
	fi
}

# Function to calculate the MD5 checksum, trying md5 first, then md5sum
calculate_md5() {
	local file="$1"
	if command -v md5 &> /dev/null; then
		# macOS `md5` command outputs "MD5 (<filename>) = <checksum>"
		md5 "$file" | awk -F ' = ' '{print $2}'
	elif command -v md5sum &> /dev/null; then
		# Linux `md5sum` outputs "<checksum> <filename>"
		md5sum "$file" | awk '{print $1}'
	else
		echo "Error: Neither md5 nor md5sum command found!"
		exit 1
	fi
}

# Find all files matching the pattern and calculate the total size in bytes
total_size=0
file_list=()
while IFS= read -r file; do
	file_list+=("$file")
	file_size=$(get_file_size "$file")
	total_size=$((total_size + file_size))
done < <(find "$SOURCE_DIR" -type f -name "$FILE_PATTERN")

# Calculate total count of files matched
total_count=${#file_list[@]}

# Check if there are any files to process
if [ "$total_count" -eq 0 ]; then
	echo "No files found matching the pattern $FILE_PATTERN in $SOURCE_DIR"
	exit 0
fi

echo "Total size of matching files: $((total_size / 1024 / 1024)) MB"

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
	# Get the directory path of the found file relative to the source directory
	relative_dir=$(dirname "$file" | sed "s|$SOURCE_DIR||")
	
	# Create the same directory structure in the target directory
	mkdir -p "$TARGET_DIR$relative_dir"
	
	# Determine the destination path
	dest="$TARGET_DIR$relative_dir/$(basename "$file")"
	
	# Check if the destination file already exists and compare MD5 checksums if enabled
	if [ "$SKIP_MD5_CHECK" = false ] && [ -f "$dest" ]; then
		src_md5=$(calculate_md5 "$file")
		dest_md5=$(calculate_md5 "$dest")
		if [ "$VERBOSE" = true ]; then
			echo "MD5 of source file ($file): $src_md5"
			echo "MD5 of destination file ($dest): $dest_md5"
		fi
		if [ "$src_md5" = "$dest_md5" ]; then
			echo "Skipping $file -> $dest (files are identical)"
			processed_size=$((processed_size + $(get_file_size "$file")))
			progress=$((processed_size * 100 / total_size))
			echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
			continue
		fi
	fi

	# Run the specified command with source and destination as arguments, highlighting the command
	echo -e "Executing: ${COLOR}$COMMAND \"$file\" \"$dest\"${RESET}"
	$COMMAND "$file" "$dest"
	
	# Increment processed count
	processed_count=$((processed_count + 1))
	
	# Update processed size and calculate progress
	processed_size=$((processed_size + $(get_file_size "$file")))
	progress=$((processed_size * 100 / total_size))
	
	# Display progress
	echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
done

# Final summary
echo -e "\nOperation complete."
echo "Command applied to $processed_count of $total_count files"
