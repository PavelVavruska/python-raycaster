class ReusablePool:
    """
    Manage reusable objects.
    """

    def __init__(self, size, class_ref):
        self._reusables = [class_ref() for _ in range(size)]

    def acquire(self):
        if self._reusables:
            return self._reusables.pop()

    def release(self, reusable):
        self._reusables.append(reusable)