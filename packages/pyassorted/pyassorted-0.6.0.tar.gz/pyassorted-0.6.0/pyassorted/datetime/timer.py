import time


class Timer(object):
    """The Timer class is a context manager that measures elapsed time.

    Examples
    --------
    >>> import time
    >>> from pyassorted.datetime import Timer
    >>>
    >>> timer = Timer()
    >>> timer.click()
    >>> time.sleep(1)
    >>> timer.click()
    >>> print(round(timer.read()))  # 1
    >>>
    >>> with timer:
    ...     time.sleep(1)
    >>> print(round(timer.read()))  # 1
    """

    def __init__(self):
        self.q = []

    def click(self) -> float:
        """Click the timer.

        Returns
        -------
        float
            The elapsed time.
        """

        self.q.append(time.time())
        return self.read()

    def read(self, intervals: int = 1) -> float:
        """Read the elapsed time.

        Parameters
        ----------
        intervals : int, optional
            The number of intervals to read, by default 1

        Returns
        -------
        float
            The elapsed time.

        Raises
        ------
        ValueError
            If the number of intervals is less than 1.
        ValueError
            If the number of intervals is greater than the number of clicks.
        """

        if intervals >= 1:
            intervals = int(intervals)
        else:
            raise ValueError(
                "Value intervals must be an integer greater than or equal to 1"
            )
        if not self.q:
            return 0
        elif len(self.q) == 1:
            return 0
        elif len(self.q) - 1 < intervals:
            raise ValueError(f"Value intervals must be less than {len(self.q)}")
        else:
            return self.q[-1] - self.q[-1 - intervals]

    def reset(self):
        """Reset the timer."""

        self.q = []

    def __enter__(self):
        self.click()
        return self

    def __exit__(self, *args):
        self.click()

    def __str__(self):
        return str(self.elapsed_time)

    def __repr__(self):
        return str(self.elapsed_time)
