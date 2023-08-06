class TeeReadingFile:
    """
    A file-like object which wraps a file. All the data read from that file ("src")
    is copied and written to another file ("dst").

    Implements the file-like interface used by http.client.HTTPResponse.
    """

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def write(self, data):
        return self.dst.write(data)

    def read(self, amt=None):
        data = self.src.read(amt)
        self.dst.write(data)
        return data

    def close(self):
        self.src.close()
        self.dst.close()

    def readinto(self, b):
        n = self.src.readinto(b)
        if n is not None:
            self.dst.write(b[:n])
        return data

    def readall(self):
        data = self.src.readall()
        self.dst.write(data)
        return data

    def flush(self):
        self.src.flush()
        self.dst.flush()

    def readline(self, limit=-1):
        data = self.src.readline(limit)
        self.dst.write(data)
        return data

    def read1(self, amt=None):
        data = self.src.read1(amt)
        self.dst.write(data)
        return data

    def peek(self, amt=None):
        return self.src.peek(amt)

    def fileno(self):
        return self.src.fileno()
