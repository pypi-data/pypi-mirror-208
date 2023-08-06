# Count-unique-chars

A small Python utility to count the number of unique characters in a given string or file.

# Installation

You can install the count_unique_chars package using pip:
```
pip install count-unique-chars
```

# Dependencies
```
pytest==7.3.1
pytest-mock==3.10.0	
```

# Usage

Run the script with a file argument
```
count_unique_chars --file path/to/file
```

Run the script with a string argument
```
count_unique_chars --string "your string"
```

When both --file and --string are provided, --file takes priority
```
count_unique_chars --file path/to/file --string "your string"
```

# License

This project is licensed under the MIT License. 