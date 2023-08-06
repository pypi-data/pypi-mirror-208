class ErrorHistory:
    """
    Contains and manage an error history queue.
    """
    def __init__(self):
        self._history: list[Exception] = []

    def append(self, exception: Exception):
        """
        Add the given exception to the queue.
        :param exception: The exception
        """
        self._history.append(exception)

    def clear(self):
        """
        Clear the queue.
        """
        self._history.clear()

    def render(self, backtraces=False) -> str:
        """
        Render the exception queue into a formatted string.
        :param backtraces: Whether the backtraces should be rendered or not.
        :return: the rendered queue
        """
        if len(self._history) == 0:
            return ''

        max_length = max(self._history, key=lambda e: len(e.__class__.__name__))
        max_length = len(max_length.__class__.__name__)

        lines = []
        for ex in self._history:
            if backtraces and ex.__traceback__ is not None:
                lines.append(ex.__traceback__)
            lines.append(f'{ex.__class__.__name__: <{max_length + 1}}> {ex}')

        return '\n'.join(lines)

    def __iter__(self) -> Exception:
        for ex in self._history:
            yield ex

    def __len__(self) -> int:
        return len(self._history)

    def __getitem__(self, item: int) -> Exception:
        return self._history[item]
