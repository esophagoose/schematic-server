import olefile
import zlib
import logging


class Schematic:
    def __init__(self) -> None:
        self._position = 0
        self.name = "Unknown"

    def __str__(self) -> str:
        return f"Schematic<{self.name}>"

    def __repr__(self) -> str:
        return f"Schematic<{self.name}>"

    def read(self, filepath: str) -> 'Schematic':
        with open(filepath, "rb") as datastream:
            ole = olefile.OleFileIO(datastream)
            self.raw_content = ole.openstream("FileHeader").read()
            self.raw_storage = ole.openstream("Storage").read()
            self.raw_additional = ole.openstream("Additional").read()
            self.records = self.read_records(self.raw_content)
            self.records += self.read_records(self.raw_additional)
            self.storage = self.read_storage(self.raw_storage)
            self.name = filepath.split("/")[-1].upper()
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
            if streamer.read_int(1) == 0:
                logging.warning("Bad padding found!")
            if streamer.read_int(1) == 1:
                logging.warning("Bad type found!")
            if streamer.read_int(1) == 0xd0:
                logging.warning("Bad magic value found!")
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
    logging.basicConfig(level=logging.INFO)
    s = Schematic().read("designs/ZooidReceiver/ZRRadio.SchDoc")
    print(s.storage.keys())
