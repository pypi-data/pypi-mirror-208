from single_char_counter_by_ng.count_single_char import count_single_char


def count_single_char_in_file(path_to_file: str, case_insensitive: bool = False) -> int:
    """Returns the number of all characters in the file occurring only once. """
    if not isinstance(path_to_file, str):
        raise TypeError(
            f"Error: path to file should be a string, but got '{type(path_to_file).__name__}'")

    try:
        with open(path_to_file, "r") as f:
            file_text = f.read()
            file_text = "".join([char for char in file_text if char not in ["\n", " "]]) # Delete line break and space
            if case_insensitive:
                return count_single_char(file_text, case_insensitive=True)
            return count_single_char(file_text)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{path_to_file}' not found")
