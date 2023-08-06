import argparse
import h5py
import numpy
from minknow.pbread import reads_pb2


def convert_pbread_to_fast5(pbread_path, fast5_path):
    with h5py.File(fast5_path) as fast5_file:
        with open(pbread_path, "rb") as f:
            channel_proto = reads_pb2.Channel()
            channel_proto.ParseFromString(f.read())

            read = channel_proto.reads[0]
            readgroup_name = "Raw/Reads/Read_{}".format(read.number)
            readgroup = fast5_file.create_group(readgroup_name)

            np_arr = numpy.array(read.signal, dtype="i2")
            raw_dset = readgroup.create_dataset("Signal", data=np_arr)

            readgroup.attrs["duration"] = len(read.signal)
            readgroup.attrs["read_id"] = read.id
            readgroup.attrs["read_number"] = read.number
            readgroup.attrs["start_time"] = read.start_raw_index

            channelgroup_name = "UniqueGlobalKey/channel_id"
            channelgroup = fast5_file.create_group(channelgroup_name)
            channelgroup.attrs["channel_number"] = channel_proto.channel_name
            channelgroup.attrs["digitisation"] = channel_proto.digitisation
            channelgroup.attrs["offset"] = channel_proto.offset
            channelgroup.attrs["range"] = channel_proto.range
            channelgroup.attrs["sampling_rate"] = channel_proto.sample_rate


def convert_fast5_to_pbread(fast5_path, pbread_path):
    with h5py.File(fast5_path) as fast5_file:
        channel_proto = reads_pb2.Channel()
        channel_data = fast5_file["UniqueGlobalKey/channel_id"]

        channel_proto.channel_name = str(channel_data.attrs["channel_number"])
        channel_proto.digitisation = int(channel_data.attrs["digitisation"])
        channel_proto.offset = int(channel_data.attrs["offset"])
        channel_proto.range = float(channel_data.attrs["range"])
        channel_proto.sample_rate = int(channel_data.attrs["sampling_rate"])

        read_group = fast5_file["Raw/Reads"]
        for i, read_name in enumerate(read_group):
            fast5_read = read_group[read_name]

            read = channel_proto.reads.add()
            read.id = str(fast5_read.attrs["read_id"])
            read.number = int(fast5_read.attrs["read_number"])
            read.start_raw_index = int(fast5_read.attrs["start_time"])
            read.signal[:] = fast5_read["Signal"][:].tolist()

        with open(pbread_path, "wb") as pbread_file:
            pbread_file.write(channel_proto.SerializeToString())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a pbread file to a fast5 file or vice versa"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--to_pbread", action="store_true")
    group.add_argument("--to_fast5", action="store_true")

    parser.add_argument("-pbread_path", required=True)
    parser.add_argument("-fast5_path", required=True)

    args = parser.parse_args()

    import time

    if args.to_fast5:
        now = time.time()
        convert_pbread_to_fast5(args.pbread_path, args.fast5_path)
        print("pbread to fast5: {}".format(time.time() - now))
    elif args.to_pbread:
        now = time.time()
        convert_fast5_to_pbread(args.fast5_path, args.pbread_path)
        print("fast5 to pbread: {}".format(time.time() - now))
