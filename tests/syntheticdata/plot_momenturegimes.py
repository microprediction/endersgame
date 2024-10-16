from midone.syntheticdata.momentumregimes import momentum_regimes


if __name__=='__main__':
    import matplotlib.pyplot as plt
    data = momentum_regimes(n=1000)
    plt.plot(data)
    plt.title("Simulated Data with Alternating Momentum and Bounce Regimes")
    plt.show()
