from unicodedata import category

import requests
from endersgame.datasources.streamgenerator import stream_generator, VALID_PUBLIC_CATEGORIES
from endersgame.datasources.streamurl import stream_url


def stream_generator_generator(start_stream_id=0, category='train', return_float=False):
    """
    Returns the next valid stream generator that checks for the existence of the remote file.

    Parameters:
    - start_stream_id (int): The starting stream ID to look for.
    - category:              Only works for 'train'

    Yields:
    - A stream generator for the next valid stream.
    """
    assert category.lower() in VALID_PUBLIC_CATEGORIES,' Only test and train data is avaiable'

    stream_id = start_stream_id
    while True:
        # Construct the first URL to check if the stream exists
        url = stream_url(category=category, stream_id=stream_id, file_number=1)

        response = requests.head(url)
        if response.status_code == 200:
            # If the file exists, yield the stream generator for this stream_id
            yield stream_generator(stream_id=stream_id, category=category, return_float=return_float)
        else:
            break

        stream_id += 1  # Move to the next stream


if __name__ == '__main__':
    # Example usage of the stream_generator_generator

    # Get the next stream:
    gen_generator = stream_generator_generator(start_stream_id=13, category='train', return_float=False)

    # Use the next stream:
    try:
        gen = next(gen_generator)  # Get the first valid stream generator
        count = 1
        for x in gen:
            count += 1
            if count > 10000:
                break
        print(f'Last value received is {x}')
    except StopIteration:
        print("No valid streams found.")
