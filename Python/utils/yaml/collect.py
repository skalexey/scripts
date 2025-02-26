import yaml
from pathlib import Path
from typing import Any, Union

class CommandsRequest:
    def __init__(self, path: Union[Path, str], fields: Any):
        self.path = Path(path)
        self.fields = fields

class Input:
    def __init__(self, requests: list[CommandsRequest], default_commands: str):
        self.requests = requests
        self.default_commands = default_commands

def extract_from_yaml(file_path: Path, fields_spec: Any) -> list:
    """Extracts commands from a YAML file based on field specifications."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print(f"Failed to load {file_path}: {e}")
        return []

    extracted = []

    def search_fields(node, fields):
        """Recursively search YAML structure based on specified fields."""
        if isinstance(fields, dict):
            for key, subfields in fields.items():
                if isinstance(node, dict) and key in node:
                    value = node[key]
                    if isinstance(subfields, list):
                        # Handle list of conditions for filtering
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    for condition in subfields:
                                        if all(item.get(k) == v for k, v in condition.items() if v is not None):
                                            # Collect from the field mentioned as None
                                            for k, v in condition.items():
                                                if v is None and k in item:
                                                    extracted.append(item[k])
                        else:
                            search_fields(value, subfields)
                    else:
                        search_fields(value, subfields)
                elif isinstance(node, list):
                    for item in node:
                        search_fields(item, fields)
        elif isinstance(fields, set):
            # Directly collect from the specified fields in a set
            if isinstance(node, dict):
                for key in fields:
                    if key in node:
                        extracted.append(node[key])
        elif isinstance(fields, str) and isinstance(node, dict):
            # Direct lookup for a single key
            if fields in node:
                extracted.append(node[fields])

    search_fields(data, fields_spec)
    return extracted

def load_commands(data: Input) -> list:
    """Processes input structure and extracts relevant commands."""
    all_commands = [data.default_commands]

    for request in data.requests:
        file_path = request.path
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        commands = extract_from_yaml(file_path, request.fields)
        all_commands.extend(commands)

    return all_commands

def merge_commands(commands: list[str], delimiter: str = " ") -> str:
    """Concatenates all commands while preserving their original order."""
    all_commands = []

    for command_string in commands:
        # Split and preserve order
        tokens = command_string.split()
        i = 0
        while i < len(tokens):
            if tokens[i].startswith("+"):
                # Attempt to construct a full command (e.g., "+set mycmd")
                cmd = tokens[i]
                i += 1
                if i < len(tokens) and not tokens[i].startswith("+"):
                    cmd += f" {tokens[i]}"  # Combine with next word (e.g., "+set mycmd")
                    i += 1

                # Capture value (everything after the command)
                value = []
                while i < len(tokens) and not tokens[i].startswith("+"):
                    value.append(tokens[i])
                    i += 1

                # Preserve order (do not merge)
                all_commands.append(f"{cmd} {' '.join(value)}".strip())

            else:
                i += 1  # Skip non-command tokens (shouldn't happen in normal cases)

    # Join with the specified delimiter
    return delimiter.join(all_commands)

def merge_and_group_commands(commands: list[str], delimiter: str = " ") -> tuple[str, set[str]]:
    """Merges command strings while tracking repeated commands (without values)."""
    command_map = {}
    repeated_commands = []
    seen_commands = set()

    for command_string in commands:
        # Split into individual tokens
        tokens = command_string.split()
        i = 0
        while i < len(tokens):
            if tokens[i].startswith("+"):
                # Attempt to construct a full command (e.g., "+set mycmd")
                cmd = tokens[i]
                i += 1
                if i < len(tokens) and not tokens[i].startswith("+"):
                    cmd += f" {tokens[i]}"  # Combine with next word (e.g., "+set mycmd")
                    i += 1

                # Capture value (everything after the command)
                value = []
                while i < len(tokens) and not tokens[i].startswith("+"):
                    value.append(tokens[i])
                    i += 1

                # Track repeated commands (preserving order)
                if cmd in seen_commands and cmd not in repeated_commands:
                    repeated_commands.append(cmd)
                seen_commands.add(cmd)

                # Store the latest occurrence of the command
                command_map[cmd] = " ".join(value) if value else ""

            else:
                i += 1  # Skip non-command tokens (shouldn't happen in normal cases)

    # Reconstruct the final merged command string
    merged_commands = [f"{cmd} {value}".strip() for cmd, value in command_map.items()]
    return delimiter.join(merged_commands), repeated_commands
