
import csv
from endersgame.datasources.streamurl import stream_url

"""
       Just for convenience, here is a float generator with a limited amount of data stored on github
       
       gen = stream_generator(stream_id=0, category='train')
       for x in gen:
           #do something with x 
       
"""

VALID_PUBLIC_CATEGORIES = ['train','test']


def stream_generator(stream_id, category='train', verbose=False, return_float=False):
    """
    A generator that yields values from remote CSV files on GitHub.

    Parameters:
    - stream_id (int): The index of the currency pair.
    - category (str): One of 'train', 'test', or 'validate'.

    Yields:
    - float: The next value from the sequence of CSV files.
    """
    assert category.lower() in VALID_PUBLIC_CATEGORIES,'Only train and test data is available,sorry! '

    import requests
    file_number = 1  # Start from the first file
    while True:
        # Construct the raw URL for the current file
        url = stream_url(category=category, stream_id=stream_id, file_number=file_number)
        try:
            # Fetch the content of the CSV file from GitHub
            response = requests.get(url)
            if response.status_code != 200:
                # If the file doesn't exist, assume we've reached the end
                if verbose:
                    print(f"No more files found for stream_id={stream_id} in category='{category}'.")
                break

            # Read the CSV content
            content = response.content.decode('utf-8').strip()
            lines = content.splitlines()
            reader = csv.DictReader(lines)

            # Yield each value from the 'value' column
            values_found = False
            for row in reader:
                values_found = True
                value = float(row['value'])
                if return_float:
                    yield value
                else:
                    yield {'x':value}

            if not values_found:
                # If the file is empty or doesn't contain 'value' column
                print(f"File stream_{stream_id}_file_{file_number}.csv is empty or invalid.")

            file_number += 1  # Move to the next file

        except Exception as e:
            # Handle any exceptions (e.g., network errors)
            print(f"An error occurred while processing file_number={file_number}: {e}")
            break


if __name__=='__main__':
    gen = stream_generator(stream_id=0)
    count = 1
    for x in gen:
        count += 1
        if count > 10000:
            break
    print(f'last value received is {x}')