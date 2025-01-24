import json
from datetime import date
from typing import Any


# create class to log the data
class Logger:
    """Class to log data to a file in datasets."""

    # create method to read file
    def read_file(self, file_path: str) -> dict[date, str]:
        """Reads data from file_path.

        Returns:
            - dict[date, str]: data read from file
        """
        with open(file_path) as file:
            return json.load(file)

    # create method to write file
    def write_file(self, file_path: str, data: dict) -> None:
        """Writes data to file_path."""
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    # create method to compare two dicts and overwrite the first dict with the second dict where
    # the second dict has a different value or value at all
    def compare_dicts(
        self, original_dict: dict[Any, Any], new_dict: dict[Any, Any]
    ) -> dict[date, Any]:
        """Compares two dicts and overwrites the first dict with the second dict where the second dict has a different value or value at all.

        Params:
            - original_dict: dict[date, Any]: first dict (kept dict)
            - new_dict: dict[date, Any]: that will add its data to the original_dict
        """
        for key, value in new_dict.items():
            key = str(key)
            if key not in original_dict or original_dict[key] != value:
                original_dict[key] = value
        return original_dict

    # create method to log the data
    def log(self, file_path: str, data: dict[Any, Any]) -> None:
        """Logs the data to file_path.

        Handling comparing the data from the file and the dataq to be logged.
        """
        try:
            # read the file
            old_data = self.read_file(file_path)
        except FileNotFoundError:
            # if file not found, create a new file
            old_data = {}

        # compare the two dicts and overwrite the first dict with the second dict where
        # the second dict has a different value or value at all
        new_data = self.compare_dicts(old_data, data)

        # write the new data to the file
        self.write_file(file_path, new_data)

    # create method that will convert a list of dicts into a single dict and make a key of the
    # given field_name
    @staticmethod
    def convert_list_of_dicts_to_dict(list_of_dicts: list[dict], key_name: str) -> dict:
        """Converts a list of dicts into a single dict and makes a key of the given field_name."""
        result = {d[key_name]: d for d in list_of_dicts}
        return result

    @staticmethod
    def __convert_dict_to_standard_dict(input_dict: dict, key_name: str) -> dict:
        """Converts a list of dicts into a single dict and makes a key of the given field_name."""
        result = {[key_name]: dict for dict in input_dict}
        return result
