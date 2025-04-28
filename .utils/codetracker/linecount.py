import os

def count_lines_and_chars_in_py_files(directory):
    """
    Count the number of lines and characters in all .py files in the given directory.

    Args:
        directory (str): The directory path to search for .py files.

    Returns:
        dict: A dictionary with filenames as keys and a tuple of (line_count, char_count) as values.
    """
    results = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    char_count = sum(len(line) for line in lines)
                    results[file] = (line_count, char_count)
    return results

# Example usage
if __name__ == "__main__":
    directory = '.'  # Current directory
    results = count_lines_and_chars_in_py_files(directory)
    total_lines = sum(line_count for line_count, _ in results.values())
    total_chars = sum(char_count for _, char_count in results.values())
    print(f"Total lines in all .py files: {total_lines}")
    print(f"Total characters in all .py files: {total_chars}")
    print(f"{'File Name':<30} {'Lines':<10} {'Characters':<10}")
    print("-" * 50)
    for file, (line_count, char_count) in results.items():
        print(f"{file:<30} {line_count:<10} {char_count:<10}")
