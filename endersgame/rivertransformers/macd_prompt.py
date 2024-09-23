

class MovingAverageConditionalDivergence:
    """
    A mixin to track rivertransformers signals based on Moving Average Convergance Divergence (MACD) and perhaps generalizations of the same.

    Usage:

          .reset_macd(**macd_params)
          .tick_macd(y=y)
          .get_macd()

    All state is stored under the `.macd` property to avoid any conflicts.

    """

    def __init__(self, **macd_params):
        self.reset_macd(**macd_params)

    def tick_macd(self, y:float):
        """
             Use river package to update running estimates of MACD components
        """

    def get_macd(self)->dict:
        """
          :return: Returns dictionary of MACD signals
        """


if __name__=='__main__':
    # Create a test set using Brownian motion
    # Import some other package to compute MACD in batch fashion each and every data point
    # Compute MACD using the class provided here
    # Compare the results
    pass
