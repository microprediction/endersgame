def demo():
    from midone.datasources.streamgenerator import stream_generator
    gen = stream_generator(stream_id=0, category='train')  # 'train', 'test'

    xs = list()
    count = 0
    for x in gen:
        count += 1
        xs.append(x)
        if count > 10000:
            break

    import matplotlib.pyplot as plt
    plt.plot(xs)
    plt.show()

if __name__=='__main__':
    demo()
