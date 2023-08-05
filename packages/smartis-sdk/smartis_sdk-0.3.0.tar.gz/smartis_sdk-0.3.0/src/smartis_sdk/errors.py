class ApiLimitError(Exception):
    def __init__(self, retry_after: int, *args):
        self.retry_after = retry_after
        self.message = args[0] if args else None

    def __str__(self):
        return f'ApiLimitError, {self.message} ' if self.message else 'ApiLimitError'
