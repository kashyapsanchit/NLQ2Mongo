import json
from datetime import datetime

def check_query(user_input, data):
    
    user_input = "".join(user_input.split()).lower()
    data = json.loads(data['data'])

    for document in data: 

        if "".join(document['user_input'].split()).lower() == user_input:
            print("Query already exists in cache")
            return document

    
    return False


def is_valid_epoch(epoch_string):
    """
    Checks if the given string is a valid epoch timestamp.
    :param epoch_string: The string to check
    :return: True if the string is a valid epoch timestamp, False otherwise
    """
    try:
        # Convert the string to an integer
        epoch = int(epoch_string)
        
        # Ensure the epoch is a positive number
        if epoch < 0:
            return False
        
        # Using datetime to verify it can be converted
        datetime.fromtimestamp(epoch / 1000)  # If the timestamp is in milliseconds
        
        return True
    except (ValueError, OverflowError):
        # ValueError: If the string isn't numeric
        # OverflowError: If the epoch is out of range for datetime
        return False
