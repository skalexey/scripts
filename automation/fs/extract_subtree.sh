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
COMMAND_TEMPLATE="${4:-mkdir -p \"\$(dirname \"\$2\")\" && cp \"\$1\" \"\$2\"}"  # Default command creates the parent directory for files or full directory path for folders and copies the file

# Print all the variables if verbose mode is enabled
if [ "$VERBOSE" = true ]; then
    echo "SOURCE_DIR: $SOURCE_DIR"
    echo "TARGET_DIR: $TARGET_DIR"
    echo "FILE_PATTERN: $FILE_PATTERN"
    echo "COMMAND_TEMPLATE: $COMMAND_TEMPLATE"
    echo "SKIP_MD5_CHECK: $SKIP_MD5_CHECK"
    echo "VERBOSE: $VERBOSE"
fi

# Check if source directory, target directory, and file pattern are provided
if [ -z "$SOURCE_DIR" ] || [ -z "$TARGET_DIR" ] || [ -z "$FILE_PATTERN" ]; then
	echo "Usage: $0 <source_directory> <target_directory> <file_pattern> [command_template] [-i|--skip-md5-check] [--verbose]"
	echo "Example: $0 /path/to/OneDrive /path/to/target_directory '*.docx' 'mkdir -p \"\$(dirname \"\$2\")\" && cp \"$1\" \"$2\"'"
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

# Function to calculate the MD5 checksum
calculate_md5() {
	local file="$1"
	local md5
	if command -v md5 &> /dev/null; then
		md5=$(md5 "$file" | awk -F ' = ' '{print $2}')
	elif command -v md5sum &> /dev/null; then
		md5=$(md5sum "$file" | awk '{print $1}')
	else
		echo "Error: Neither md5 nor md5sum command found!"
		exit 1
	fi
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

# Initialize progress tracking and file processing count
processed_size=0
processed_count=0  # Counter for files that are actually processed

# Define color for command highlighting (e.g., bold cyan)
COLOR="\033[1;36m"
RESET="\033[0m"

# Process each file
# Process each file
for file in "${file_list[@]}"; do
	# Normalize each file path
	absolute_file=$(realpath "$file")
	
	# Get the relative path by stripping SOURCE_DIR from absolute_file
	relative_path="${absolute_file#$SOURCE_DIR}"
	relative_dir=$(dirname "$relative_path")
	
	# Determine the full destination path
	dest="$TARGET_DIR/$relative_dir/$(basename "$file")"
	
	# Construct the command by replacing placeholders $1 and $2 with the file paths
	exec_command="${COMMAND_TEMPLATE//\$1/$absolute_file}"
	exec_command="${exec_command//\$2/$dest}"

	# Retrieve the size of the current file
	file_size=$(get_file_size "$file")  

	# Check if the destination file already exists and compare MD5 checksums if enabled
	if [ -f "$dest" ]; then
		src_md5=$(calculate_md5 "$file")
		dest_md5=$(calculate_md5 "$dest")

		# Always print MD5s if verbose mode is on
		if [ "$VERBOSE" = true ]; then
			echo "MD5 of source file ($file): $src_md5"
			echo "MD5 of destination file ($dest): $dest_md5"
		fi

		# Skip the file if MD5 checksums match
		if [ "$SKIP_MD5_CHECK" = false ] && [ "$src_md5" = "$dest_md5" ]; then
			echo "Skipping $file -> $dest (files are identical)"
			processed_size=$((processed_size + file_size))
			progress=$((processed_size * 100 / total_size))
			echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
			continue
		fi
	fi

	# Run the specified command with source and destination as arguments, highlighting the command
	echo -e "Executing: ${COLOR}$exec_command${RESET}"
	eval "$exec_command"
	
	# Increment processed count and update processed size
	processed_count=$((processed_count + 1))
	processed_size=$((processed_size + file_size))
	progress=$((processed_size * 100 / total_size))
	
	# Display progress
	echo -ne "Progress: $progress% ($((processed_size / 1024 / 1024)) MB of $((total_size / 1024 / 1024)) MB)\r"
done

# Final summary
echo -e "\nOperation complete."
echo "Command applied to $processed_count of $total_count files"
