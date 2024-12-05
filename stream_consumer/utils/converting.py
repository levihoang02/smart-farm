import json
from datetime import datetime

def convert_to_json(input_string):
    """
    Convert a formatted string to a JSON object, parsing numeric values as floats and timestamp as a datetime.

    Args:
        input_string (str): The formatted input string.

    Returns:
        str: A JSON-formatted string.
    """
    data = {}
    try:
        for item in input_string.split(", "):
            key, value = item.split(": ", 1)  # Split only on the first occurrence of ": "
            if key == "timestamp":
                try:
                    # Parse the timestamp into ISO 8601 format
                    timestamp = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S.%f")
                    data[key] = timestamp.isoformat()
                except ValueError:
                    data[key] = value.strip()  # Keep as a string if parsing fails
            else:
                try:
                    value = float(value)  # Convert numeric values to float
                except ValueError:
                    value = value.strip()  # Keep non-numeric values as strings
                data[key] = value
    except Exception as e:
        print(f"Error processing string: {e}")
        return None

    # Convert the dictionary to JSON
    return data