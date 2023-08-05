

class SafeStreamReader(object):
    """recover stream current position after doing something will cause the position move.
    """

    def __init__(self, stream):
        self.stream = stream
        self.original_position = stream.tell()
    
    def __enter__(self):
        self.stream.seek(0)
        return self.stream

    def __exit__(self, type, value, traceback):
        self.stream.seek(self.original_position)

