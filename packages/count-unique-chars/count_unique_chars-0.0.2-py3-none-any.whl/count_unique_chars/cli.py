import argparse

from count_unique_chars.count_unique_chars import UniqueCharsCounter

def create_parser():
    parser = argparse.ArgumentParser(description='Count the number of unique characters in a given string or file.')
    parser.add_argument('--file', type=str, help='Path to a file to count unique characters in.')
    parser.add_argument('--string', type=str, help='A string to count unique characters in.')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.file:
        try:
            with open(args.file, 'r') as f:
                text = f.read()
        except FileNotFoundError as e:
            parser.error('File not found.')
    elif args.string:
        text = args.string
    else:
        parser.error('At least one of --file or --string must be provided.')
    unique_chars_counter = UniqueCharsCounter()
    result = unique_chars_counter.count_unique_chars(text)
    print('Number of unique characters:', result)