from io import BytesIO


class JavaStream(BytesIO):
    """
    A JavaStream able to manage stream from java
    make interface between a java stream and BytesIO python
    each read, seek does operation on java stream: stream_java.
    """

    def __init__(self, stream_java):
        self.stream_java = stream_java
        self._pos = 0

    def seek(self, pos, **kwargs):
        skip = pos - self._pos
        self._pos = self._pos + self.stream_java.skip(skip)

    def readable(self) -> bool:
        return True

    def read(self, *args, **kwargs) -> bytes:
        if len(args) > 0 and isinstance(args[0], int) and args[0] > 0:
            length_to_read = args[0]
        else:
            length_to_read = 1000
        # bug
        # print('into read')
        arr = bytearray()
        index = 0
        while index < length_to_read:
            byte_read = self.stream_java.read()
            if byte_read < 0:
                break
            bytes_python = byte_read.to_bytes(1, byteorder='big')
            arr.append(bytes_python[0])
            index = index + 1
        self._pos = self._pos+index
        return arr

    def readinto(self, __buffer) -> int:
        # debug
        # print('into readinto')
        index = 0
        while index < len(__buffer):
            byte_read = self.stream_java.read()
            if byte_read < 0:
                break
            bytes_python = byte_read.to_bytes(1, byteorder='big')
            __buffer[index] = bytes_python[0]
            index = index + 1
        self._pos = self._pos+index
        return index

    def readinto1(self, __buffer) -> int:
        return self.readinto(__buffer)

    def read1(self, *args, **kwargs) -> bytes:
        return self.read(*args, **kwargs)

    def tell(self, *args, **kwargs) -> bytes:
        return self._pos

    def close(self) -> None:
        super().close()
        self.stream_java.close()
