class Channel(object):
    """
    Class that aims to define a channel, holding both the index and the name.
    The index is the channel number when counting from 0, while the name is the channel number
    when counting from 1. This class wants to solve the ambiguity of not knowing whether
    we are counting from 0 or 1 when we see variables like channel_id.
    To create a channel, use from_index or from_name, depending on how the counting is done.

    E.g.: chA = Channel(index=0)
    is the same as chB = Channel(name=1),
    and we can see that chA == chB will evaluate to True.

    If the user wants to access the index or the name from a channel, he can call
    ch.index or ch.name. For example, ch.name will never return 0.
    """

    def __init__(self, *, index=None, name=None):
        if index is not None:
            if name is not None:
                raise TypeError("exactly one of index or name must be provided")
            if index < 0:
                raise ValueError("index cannot be negative")
            self.__index = index
        elif name is not None:
            if name < 1:
                raise ValueError("name cannot be less than 1")
            self.__index = name - 1
        else:
            raise TypeError("index or name must be provided")

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    @classmethod
    def from_index(cls, index):
        return cls(index=index)

    @classmethod
    def from_name(cls, name):
        return cls(name=name)

    @property
    def index(self):
        return self.__index

    @property
    def name(self):
        return self.__index + 1

    def __lt__(self, other):
        return self.__index < other.__index

    def __le__(self, other):
        return self.__index <= other.__index

    def __eq__(self, other):
        return self.__index == other.__index

    def __ne__(self, other):
        return self.__index != other.__index

    def __gt__(self, other):
        return self.__index > other.__index

    def __ge__(self, other):
        return self.__index >= other.__index

    def __add__(self, other):
        if isinstance(other, int):
            return Channel.from_index(self.__index + other)
        elif isinstance(other, Channel):
            raise TypeError(
                "Cannot add a channel to another. Can only add offsets which are ints."
            )
        else:
            raise TypeError("Unexpected type while adding channels")

    def __sub__(self, other):
        if isinstance(other, int):
            return Channel.from_index(self.__index - other)
        elif isinstance(other, Channel):
            raise TypeError(
                "Cannot subtract a channel from another. Can only subtract offsets which are ints."
            )
        else:
            raise TypeError("Unexpected type while subtracting channels")

    def __iadd__(self, other):
        if isinstance(other, int):
            self = Channel.from_index(self.__index + other)
            return self
        elif isinstance(other, Channel):
            raise TypeError(
                "Cannot add a channel to another. Can only add offsets which are ints."
            )
            return self
        else:
            raise TypeError("Unexpected type while adding channels")

    def __isub__(self, other):
        if isinstance(other, int):
            self = Channel.from_index(self.__index - other)
            return self
        elif isinstance(other, Channel):
            raise TypeError(
                "Cannot subtract a channel from another. Can only subtract offsets which are ints."
            )
            return self
        else:
            raise RuntimeError("Unexpected type while adding channels")

    def __hash__(self):
        return hash(self.index)


class ChannelRange:
    """
    Class used to allow using the class Channel in ranges. To use a range of channels,
    call:

    >>> ChannelRange(Channel(index=0), Channel(index=512))

    This will iterate over the channels [0,511] inclusive, or [1,512] inclusive.

    Alternatively, the same can be achieved by:

    >>> ChannelRange(Channel(name=1), Channel(name=513))

    So the following are equivalent:

    >>> for ch in ChannelRange(Channel(index=0), Channel(index=512)):
    >>>    pass

    >>> for ch in ChannelRange(Channel(name=1), Channel(name=513)):
    >>>    pass

    >>> for ch_index in range(0,512):
    >>>    ch = Channel(index=ch_index)

    >>> for ch_name in range(1,513):
    >>>    ch = Channel(name=ch_name)
    """

    def __init__(self, start, end, step=1):
        try:
            self.current = start
            self.limit = end
            self.step = int(step)
        except ValueError:
            raise
        if step == 0:
            raise ValueError("Step can't be 0")

    def __iter__(self):
        return ChannelRange(self.current, self.limit, self.step)

    def __next__(self):
        if self.step > 0 and self.current >= self.limit:
            raise StopIteration()
        if self.step < 0 and self.current <= self.limit:
            raise StopIteration()
        cur = self.current
        self.current += self.step
        return cur
