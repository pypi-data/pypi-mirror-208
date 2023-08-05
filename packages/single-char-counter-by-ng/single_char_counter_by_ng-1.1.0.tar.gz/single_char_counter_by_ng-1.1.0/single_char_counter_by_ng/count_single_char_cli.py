import argparse

from single_char_counter_by_ng.count_single_char import count_single_char
from single_char_counter_by_ng.count_single_char_in_file import count_single_char_in_file


def count_single_char_cli(args):
    """Count the number of characters occurring only once in a string or a text file. """
    if args.file:  # If passed two parameters, the parameter '--file' has higher priority.
        print(count_single_char_in_file(
            args.file, case_insensitive=args.case_insensitive))
    elif args.string:
        print(count_single_char(args.string, case_insensitive=args.case_insensitive))
    else:
        print("No input specified. Please provide either --file or --string argument.")


def parse_arguments():
    """Parse command line arguments. """
    parser = argparse.ArgumentParser(
        description="Count the number of characters occurring only once in a string or a text file.")
    parser.add_argument("--file", "-f", type=str, metavar="",
                        help="Path to text file for count single char")
    parser.add_argument("--string", "-s", type=str,
                        metavar="", help="Text for count single char")
    parser.add_argument("--case_insensitive", "-i", action="store_true",
                        help="Perform case-insensitive counting")

    parse_args = parser.parse_args()
    return parse_args


if __name__ == "__main__":
    args = parse_arguments()
    count_single_char_cli(args)
