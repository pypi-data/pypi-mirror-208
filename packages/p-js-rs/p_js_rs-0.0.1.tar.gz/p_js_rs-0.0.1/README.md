# PJS 

PJS is a utility class for writing and reading JSON data in Python.

## Example Usage

```python

from p_js import PJS

data = {"key": "value"}

# Write compressed data
PJS.write_compressed_data(data, "output")

# Read compressed data
read_data = PJS.read_compressed_data("output")
print(read_data)

# Github
https://github.com/Rajveer-Singh8124/P_JS


