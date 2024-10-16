from unicodedata import category


def stream_url(category, stream_id, file_number):
    url = f'https://raw.githubusercontent.com/microprediction/endersdata/main/data/{category.lower()}/stream_{stream_id}_file_{file_number}.csv'
    return url


if __name__=='__main__':
    import pandas as pd
    url = stream_url(category='train',stream_id=13, file_number=1)
    df = pd.read_csv(url)

    import matplotlib.pyplot as plt
    plt.plot(df['value'])
    plt.show()