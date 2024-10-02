import requests
from endersgame.datasources.streamgenerator import stream_generator


def stream_generator_generator(start_stream_id=0, category='train'):
    """
    Returns the next valid stream generator that checks for the existence of the remote file.

    Parameters:
    - start_stream_id (int): The starting stream ID to look for.
    - category:              Only works for 'train'

    Yields:
    - A stream generator for the next valid stream.
    """
    stream_id = start_stream_id
    while True:
        # Construct the URL to check if the stream exists
        url = f'https://raw.githubusercontent.com/microprediction/endersdata/main/data/{category}/stream_{stream_id}_file_1.csv'

        # Check if the file exists by making a head request
        response = requests.head(url)
        if response.status_code == 200:
            # If the file exists, yield the stream generator for this stream_id
            yield stream_generator(stream_id, category)
        else:
            # If the file does not exist, stop checking
            break

        stream_id += 1  # Move to the next stream


if __name__ == '__main__':
    # Example usage of the stream_generator_generator

    # Get the next stream:
    gen_generator = stream_generator_generator(start_stream_id=13, category='train')

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
