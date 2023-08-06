import h5py, sys, logging, os.path, json
from collections import OrderedDict

PARTIAL_READ_FLAG = 1 << 0


def extract_calibration(input_hdf_file, channel_count=512):
    sample_rate = 0

    f = h5py.File(input_hdf_file, "r")

    intermediate_data = f["IntermediateData"]
    per_channel_data = OrderedDict()
    channels = range(1, 1 + channel_count)
    for c in channels:
        channel_name = "Channel_{}".format(c)
        if channel_name not in intermediate_data:
            raise Exception("Invalid Channel {}".format(c))
        chan_data = intermediate_data[channel_name]

        meta = chan_data["Meta"]
        attrs = meta.attrs

        sample_rate = attrs["sample_rate"]
        per_channel_data[str(c)] = {
            "offset": str(int(attrs["offset"])),
            "range_in_pA": str(attrs["range"]),
        }

    opts = {"sample_rate": sample_rate}

    return per_channel_data, opts


def is_complete_read_chunk(read_chunk):
    """
    Find if the passed entry from a read chunk table is a complete/final read chunk
    """
    return read_chunk["flags"] & PARTIAL_READ_FLAG == 0


class ReadChunkAggregator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.first_chunk = None

    def aggregate_read_chunk(self, chunk, force_complete=False):
        if self.first_chunk is None:
            self.first_chunk = chunk

        if is_complete_read_chunk(chunk) or force_complete:
            result = chunk.copy()
            # Ensure we cache a read with complete stats is complete
            end = chunk["read_start"] + chunk["read_length"]
            begin = self.first_chunk["read_start"]
            result["read_start"] = begin
            result["read_length"] = end - begin
            result["event_index_start"] = self.first_chunk["event_index_start"]

            self.reset()
            return result

        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("help:")
        print("  Usage is extract_calibration.py [input_hdf] [output_path_calibration]")
        exit(1)

    filename = sys.argv[1]
    output_path = sys.argv[2]

    print("Extracting calibration from {}".format(filename))
    extract_calibration(filename, output_path)

    print("Wrote calibration to {}".format(filename))
