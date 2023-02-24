import olefile
import zlib


class Schematic:
    def __init__(self) -> None:
        self._position = 0

    def read(self, filepath) -> 'Schematic':
        with open(filepath, "rb") as datastream:
            ole = olefile.OleFileIO(datastream)
            raw_content = ole.openstream("FileHeader").read()
            raw_storage = ole.openstream("Storage").read()
            self.records = self.read_records(raw_content)
            self.storage = self.read_storage(raw_storage)
        return self
    
    def read_records(self, data):
        blocks = []
        streamer = DataStreamer(data)
        while not streamer.eof():
            payload_size = streamer.read_int(2)
            assert streamer.read_int(1) == 0, "Bad pad in header"
            assert streamer.read_int(1) == 0, "Bad type in header"
            payload = streamer.read(payload_size)
            assert payload[-1] == 0, "Invalid ending byte"
            blocks.append(payload[:-1].decode("latin1"))
        return blocks


    def read_storage(self, data):
        streamer = DataStreamer(data)
        # Validate there's a valid header
        payload_size = streamer.read_int(2)
        assert streamer.read_int(1) == 0, "Bad pad in header"
        assert streamer.read_int(1) == 0, "Bad type in header"
        header = streamer.read(payload_size)
        if b"|HEADER=Icon storage" not in header or header[-1] != 0:
            raise ValueError(f"Invalid header: {header}")

        # Read in data
        images = {}
        while not streamer.eof():
            streamer.read_int(2)  # payload size; not used
            assert streamer.read_int(1) == 0, "Bad pad"
            assert streamer.read_int(1) == 1, "Bad type"
            assert streamer.read_int(1) == 0xd0, "Bad magic"
            filename_length = streamer.read_int(1)
            filename = streamer.read(filename_length)
            compressed_size = streamer.read_int(4)
            image = zlib.decompress(streamer.read(compressed_size))
            images[filename] = image
        return images


class DataStreamer:
    def __init__(self, data) -> None:
        self.data = data
        self.pos = 0

    def read(self, length) -> bytes:
        self.pos += length
        return self.data[self.pos - length:self.pos]

    def read_int(self, length) -> int:
        return int.from_bytes(self.read(length), "little")
    
    def eof(self) -> bool:
        return self.pos + 1 >= len(self.data)


if __name__ == "__main__":
    s = Schematic().read("nRF52-Quadcopter/pca20017_mcu.SchDoc")
    print(s.storage.keys())
