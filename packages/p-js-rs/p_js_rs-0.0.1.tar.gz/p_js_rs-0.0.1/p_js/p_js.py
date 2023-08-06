import json
import gzip
try:
    import pytest
except ImportError:
    print('WARNING: py.test not found. falling back to unittest. For more informative errors, install py.test')

# Continue with the rest of your code, using unittest or other alternatives

class PJS:
    """
    PJS is a utility class for writing and reading JSON data.

    Example Usage:
        data = {"key": "value"}
        PJS.write(data, "output")

        read_data = PJS.read("output")
        print(read_data)
    """

    @staticmethod
    def write_compressed_data(data: dict | list, file_name: str) -> None:
        """
        Writes the given JSON-serializable data to a compressed JSON file.

        Args:
            data (dict | list): The JSON-serializable data to be written.
            file_name (str): The name of the output file without the extension.

        Returns:
            None
        """
        serialized_data = json.dumps(data, indent=2)
        compressed_data = gzip.compress(serialized_data.encode("utf-8"))
        with open(f"{file_name}.json.gz", "wb") as file:
            file.write(compressed_data)

    @staticmethod
    def write(data: dict | list, file_name: str) -> None:
        """
        Writes the given JSON-serializable data to a JSON file.

        Args:
            data (dict | list): The JSON-serializable data to be written.
            file_name (str): The name of the output file without the extension.

        Returns:
            None
        """
        serialized_data = json.dumps(data, indent=2)
        with open(f"{file_name}.json", "w") as file:
            file.write(serialized_data)

    @staticmethod
    def read_compressed_data(file_name: str) -> dict:
        """
        Reads compressed JSON data from the specified file and returns it as a dictionary.

        Args:
            file_name (str): The name of the input file without the extension.

        Returns:
            dict: The JSON data read from the file.
        """
        with open(f"{file_name}.json.gz", "rb") as file:
            compressed_data = file.read()
            decompressed_data = gzip.decompress(compressed_data)
            json_data = decompressed_data.decode("utf-8")
            data = json.loads(json_data)
            return data

    @staticmethod
    def read(file_name: str) -> dict:
        """
        Reads JSON data from the specified file and returns it as a dictionary.

        Args:
            file_name (str): The name of the input file without the extension.

        Returns:
            dict: The JSON data read from the file.
        """
        with open(f"{file_name}.json", "r") as file:
            data = json.loads(file.read())
            return data


